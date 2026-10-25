"""Loopback HTTP boundary for image uploads, jobs, and video retrieval."""
from contextlib import asynccontextmanager
import io
from pathlib import Path
import warnings

from fastapi import FastAPI, HTTPException, Request
from PIL import Image, UnidentifiedImageError
from python_multipart.exceptions import MultipartParseError
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import UploadFile
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import FileResponse, JSONResponse

from .config import MAX_IMAGE_BYTES, MAX_REQUEST_BYTES, PRESET, Settings
from .jobs import JobManager, QueueFull, Unavailable
from .runtime import MlxRuntime


class UploadBoundary:
    """Cap even chunked bodies before multipart parsing or temporary-file spooling."""
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http' or scope['method'] != 'POST':
            return await self.app(scope, receive, send)
        headers = {k.lower(): v for k, v in scope['headers']}
        origin = headers.get(b'origin')
        expected = (scope.get('scheme', 'http') + '://' + headers.get(b'host', b'').decode()).encode()
        if origin and origin != expected:
            return await JSONResponse({'detail': 'Cross-origin submissions are not enabled'}, 403)(scope, receive, send)
        try:
            length = int(headers.get(b'content-length', b'0'))
            if length < 0:
                raise ValueError
        except ValueError:
            return await JSONResponse({'detail': 'Invalid Content-Length'}, 400)(scope, receive, send)
        if length > MAX_REQUEST_BYTES:
            return await JSONResponse({'detail': 'Upload exceeds 10 MiB plus multipart overhead'}, 413)(scope, receive, send)
        chunks, size = [], 0
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            size += len(message.get('body', b''))
            if size > MAX_REQUEST_BYTES:
                return await JSONResponse({'detail': 'Upload exceeds request limit'}, 413)(scope, receive, send)
            chunks.append(message.get('body', b''))
            if not message.get('more_body', False):
                break
        body = b''.join(chunks)
        delivered = False

        async def replay():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return await receive()
        await self.app(scope, replay, send)


def validate_image(content, content_type):
    if not content:
        raise HTTPException(422, 'Image is empty')
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(413, 'Image exceeds 10 MiB')
    formats = {'PNG': ('png', 'image/png'), 'JPEG': ('jpg', 'image/jpeg'),
               'WEBP': ('webp', 'image/webp')}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as image:
                if image.format not in formats:
                    raise HTTPException(415, 'Use PNG, JPEG, or WebP')
                extension, mime = formats[image.format]
                if content_type != mime:
                    raise HTTPException(415, 'Content-Type does not match the image format')
                width, height = image.size
                if not (64 <= width <= 4096 and 64 <= height <= 4096):
                    raise HTTPException(422, 'Image dimensions must be 64–4096 pixels per side')
                if getattr(image, 'n_frames', 1) != 1:
                    raise HTTPException(422, 'Use a single-frame image')
                image.verify()
            with Image.open(io.BytesIO(content)) as image:
                image.load()  # Reject truncated payloads; preserve original bytes.
    except (OSError, ValueError, UnidentifiedImageError, Image.DecompressionBombError,
            Image.DecompressionBombWarning) as error:
        raise HTTPException(422, 'Image could not be decoded') from error
    return {'extension': extension, 'content_type': mime, 'width': width, 'height': height}


def create_app(settings=None, runtime=None):
    settings = settings or Settings(Path.cwd())
    manager = JobManager(settings, runtime or MlxRuntime(settings))

    @asynccontextmanager
    async def lifespan(app):
        await run_in_threadpool(manager.start)
        try:
            yield
        finally:
            await run_in_threadpool(manager.close)

    app = FastAPI(title='Dancing Angels Local API', version='0.1.0', lifespan=lifespan)
    app.state.jobs = manager
    app.add_middleware(UploadBoundary)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=['127.0.0.1', 'localhost'])

    @app.exception_handler(MultipartParseError)
    async def malformed_multipart(request, error):
        return JSONResponse({'detail': 'Malformed multipart body'}, 400)

    @app.get('/health')
    def health():
        return {'status': 'ok', 'ready': manager.readiness_report()['ready'],
                'queue': manager.counts(), 'preset': PRESET}

    @app.get('/ready')
    def ready():
        report = manager.readiness_report()
        return JSONResponse(report, 200 if report['ready'] else 503)

    @app.post('/jobs', status_code=202)
    async def submit(request: Request):
        if request.headers.get('content-type', '').split(';')[0].strip() != 'multipart/form-data':
            raise HTTPException(415, 'Send multipart/form-data with image and action=shuffle')
        async with request.form(max_files=1, max_fields=1, max_part_size=1024) as form:
            entries = list(form.multi_items())
            if len(entries) != 2 or set(form.keys()) != {'image', 'action'}:
                raise HTTPException(422, 'Exactly one image and action=shuffle are required')
            upload, action = form['image'], form['action']
            if not isinstance(upload, UploadFile) or action != 'shuffle':
                raise HTTPException(422, 'Exactly one image and action=shuffle are required')
            content = await upload.read(MAX_IMAGE_BYTES + 1)
            info = await run_in_threadpool(validate_image, content, upload.content_type)
        try:
            record = await run_in_threadpool(manager.submit, content, info)
        except QueueFull as error:
            raise HTTPException(429, str(error), headers={'Retry-After': '10'}) from error
        except Unavailable as error:
            raise HTTPException(503, str(error)) from error
        return JSONResponse(record, 202, headers={'Location': f"/jobs/{record['id']}"})

    def find_job(job_id):
        try:
            return manager.get(job_id)
        except KeyError:
            raise HTTPException(404, 'Job not found')

    @app.get('/jobs/{job_id}')
    def get_job(job_id: str):
        return find_job(job_id)

    @app.get('/jobs/{job_id}/video')
    def video(job_id: str):
        record = find_job(job_id)
        if record['status'] != 'succeeded':
            raise HTTPException(409, f"Video unavailable: job is {record['status']}")
        path = settings.jobs_directory / record['id'] / 'result.mp4'
        if not path.is_file():
            raise HTTPException(410, 'Completed video is missing from local storage')
        return FileResponse(path, media_type='video/mp4', filename=f"{job_id}.mp4",
                            content_disposition_type='inline')

    return app
