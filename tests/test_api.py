"""HTTP and lifecycle tests without loading MLX weights or using the GPU."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from PIL import Image

from dancing_angels_ai.api.config import MAX_REQUEST_BYTES, Settings
from dancing_angels_ai.api.jobs import JobManager
from dancing_angels_ai.api.runtime import GenerationStopped, MlxRuntime, validate_output
from dancing_angels_ai.api.server import create_app


def png(size=(64, 64)):
    stream = io.BytesIO()
    Image.new('RGB', size, 'red').save(stream, format='PNG')
    return stream.getvalue()


class FakeRuntime:
    def __init__(self, ready=True, fail=False, blocked=False):
        self.ready, self.fail = ready, fail
        self.entered, self.release = threading.Event(), threading.Event()
        if not blocked:
            self.release.set()
        self.active = self.peak_active = self.calls = 0
        self.guard = threading.Lock()

    def readiness(self):
        return {'ready': self.ready, 'checks': [{'name': 'fake runtime', 'passed': self.ready}]}

    def generate(self, image, prompt, output, log_path, stop, lock_fd):
        with self.guard:
            self.active += 1
            self.calls += 1
            self.peak_active = max(self.peak_active, self.active)
        self.entered.set()
        try:
            while not self.release.wait(0.01):
                if stop.is_set():
                    raise GenerationStopped('API stopped during generation')
            if self.fail:
                raise RuntimeError('Simulated model failure')
            output.write_bytes(b'fake-video-payload')
            return {'frames': 49, 'fps': 24, 'full_decode': True}
        finally:
            with self.guard:
                self.active -= 1


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.settings = Settings(Path(self.temporary.name))

    def client(self, runtime=None):
        return TestClient(create_app(self.settings, runtime or FakeRuntime()),
                          base_url='http://127.0.0.1')

    def submit(self, client, content=None, filename='hero.png', mime='image/png', action='shuffle'):
        return client.post('/jobs', files={'image': (filename, png() if content is None else content, mime)},
                           data={'action': action})

    def wait_for(self, client, job_id, state):
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            record = client.get('/jobs/' + job_id).json()
            if record['status'] == state:
                return record
            time.sleep(0.01)
        self.fail(f'Job did not reach {state}: {record}')

    def test_http_lifecycle_isolation_and_range_retrieval(self):
        runtime = FakeRuntime(blocked=True)
        with self.client(runtime) as client:
            self.assertTrue(client.get('/health').json()['ready'])
            self.assertEqual(client.get('/ready').status_code, 200)
            response = self.submit(client, filename='../../escape.png')
            self.assertEqual(response.status_code, 202)
            job_id = response.json()['id']
            self.assertEqual(response.headers['location'], '/jobs/' + job_id)
            self.assertTrue(runtime.entered.wait(2))
            self.wait_for(client, job_id, 'running')
            self.assertEqual(client.get(f'/jobs/{job_id}/video').status_code, 409)
            runtime.release.set()
            result = self.wait_for(client, job_id, 'succeeded')
            self.assertEqual(result['preset']['steps'], 40)
            self.assertEqual(result['output']['frames'], 49)
            video = client.get(result['output_url'])
            self.assertEqual(video.content, b'fake-video-payload')
            self.assertEqual(video.headers['content-type'], 'video/mp4')
            self.assertIn('inline', video.headers['content-disposition'])
            ranged = client.get(result['output_url'], headers={'Range': 'bytes=0-3'})
            self.assertEqual(ranged.status_code, 206)
            self.assertEqual(ranged.content, b'fake')
            self.assertEqual(client.get(result['output_url'], headers={'Range': 'bytes=999-'}).status_code, 416)
            directory = self.settings.jobs_directory / job_id
            self.assertEqual((directory/'input.png').read_bytes(), png())
            self.assertFalse((self.settings.project_root/'escape.png').exists())
            record = json.loads((directory/'job.json').read_text())
            self.assertEqual(record['model_config']['sample_fps'], 24)
            self.assertIn('heel-toe', record['prompt'])
            self.assertFalse((directory/'job.json.tmp').exists())

    def test_queue_limit_and_sequential_execution(self):
        runtime = FakeRuntime(blocked=True)
        with self.client(runtime) as client:
            first = self.submit(client).json()['id']
            self.assertTrue(runtime.entered.wait(2))
            waiting = [self.submit(client), self.submit(client)]
            self.assertEqual([r.status_code for r in waiting], [202, 202])
            rejected = self.submit(client)
            self.assertEqual(rejected.status_code, 429)
            self.assertEqual(rejected.headers['retry-after'], '10')
            self.assertEqual(len(list(self.settings.jobs_directory.iterdir())), 3)
            self.assertEqual(client.get('/health').json()['queue'],
                             {'running': 1, 'queued': 2, 'queue_capacity': 2})
            runtime.release.set()
            for job_id in [first] + [r.json()['id'] for r in waiting]:
                self.wait_for(client, job_id, 'succeeded')
            self.assertEqual(runtime.calls, 3)
            self.assertEqual(runtime.peak_active, 1)

    def test_invalid_uploads_never_create_jobs(self):
        runtime = FakeRuntime()
        with self.client(runtime) as client:
            for content, mime, status in [(b'', 'image/png', 422), (b'garbage', 'image/png', 422),
                                          (png(), 'image/jpeg', 415), (png((16, 16)), 'image/png', 422),
                                          (png()[:50], 'image/png', 422)]:
                self.assertEqual(self.submit(client, content, mime=mime).status_code, status)
            self.assertEqual(self.submit(client, action='run').status_code, 422)
            self.assertEqual(client.post('/jobs', json={'image': '/etc/passwd'}).status_code, 415)
            self.assertEqual(client.post('/jobs', data={'action': 'shuffle'}).status_code, 415)
            self.assertEqual(client.post('/jobs', files={'image': ('x.png', png(), 'image/png')}).status_code, 422)
            duplicate = client.post('/jobs', files=[('image', ('a.png', png(), 'image/png')),
                                                   ('image', ('b.png', png(), 'image/png'))], data={'action': 'shuffle'})
            self.assertEqual(duplicate.status_code, 400)
            oversized = client.post('/jobs', content=b'x', headers={'Content-Length': str(MAX_REQUEST_BYTES + 1)})
            self.assertEqual(oversized.status_code, 413)
            chunks = (b'x' * (1024 * 1024) for _ in range(11))
            self.assertEqual(client.post('/jobs', content=chunks).status_code, 413)
            malformed = client.post('/jobs', content=b'broken body',
                                    headers={'Content-Type': 'multipart/form-data; boundary=x'})
            self.assertEqual(malformed.status_code, 400)
            self.assertEqual(runtime.calls, 0)
            self.assertEqual(list(self.settings.jobs_directory.iterdir()), [])

    def test_failed_job_and_not_ready_runtime(self):
        with self.client(FakeRuntime(fail=True)) as client:
            job_id = self.submit(client).json()['id']
            result = self.wait_for(client, job_id, 'failed')
            self.assertEqual(result['error']['code'], 'generation_failed')
            self.assertIn('Simulated model failure', result['error']['message'])
            self.assertEqual(client.get(f'/jobs/{job_id}/video').status_code, 409)
            self.assertIn('Traceback', (self.settings.jobs_directory/job_id/'generation.log').read_text())
        with self.client(FakeRuntime(ready=False)) as client:
            self.assertFalse(client.get('/health').json()['ready'])
            self.assertEqual(client.get('/ready').status_code, 503)
            self.assertEqual(self.submit(client).status_code, 503)

    def test_restart_retains_finished_jobs_and_fails_abandoned_jobs(self):
        with self.client() as client:
            job_id = self.submit(client).json()['id']
            self.wait_for(client, job_id, 'succeeded')
        with self.client() as client:
            self.assertEqual(client.get('/jobs/'+job_id).json()['status'], 'succeeded')
            self.assertEqual(client.get(f'/jobs/{job_id}/video').status_code, 200)
        path = self.settings.jobs_directory/job_id/'job.json'
        for state in ('queued', 'running'):
            record = json.loads(path.read_text()); record['status'] = state
            path.write_text(json.dumps(record))
            with self.client() as client:
                result = client.get('/jobs/'+job_id).json()
                self.assertEqual(result['status'], 'failed')
                self.assertEqual(result['error']['code'], 'interrupted')
                self.assertEqual(client.get(f'/jobs/{job_id}/video').status_code, 409)

    def test_shutdown_fails_active_and_waiting_jobs(self):
        runtime = FakeRuntime(blocked=True)
        with self.client(runtime) as client:
            active = self.submit(client).json()['id']
            self.assertTrue(runtime.entered.wait(2))
            queued = self.submit(client).json()['id']
        for job_id in (active, queued):
            record = json.loads((self.settings.jobs_directory/job_id/'job.json').read_text())
            self.assertEqual(record['status'], 'failed')
            self.assertEqual(record['error']['code'], 'interrupted')

    def test_second_instance_refused_and_lock_survives_inherited_child(self):
        first = JobManager(self.settings, FakeRuntime()); first.start()
        second = JobManager(self.settings, FakeRuntime())
        child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(30)'],
                                 pass_fds=(first._lock_file.fileno(),))
        try:
            with self.assertRaisesRegex(RuntimeError, 'worker lock'):
                second.start()
            first.close()
            with self.assertRaisesRegex(RuntimeError, 'worker lock'):
                second.start()
        finally:
            child.terminate(); child.wait(); first.close()
        second.start(); second.close()

    def test_local_boundary_and_unknown_or_missing_results(self):
        with self.client() as client:
            self.assertEqual(client.get('/health', headers={'Host': 'evil.example'}).status_code, 400)
            self.assertEqual(client.post('/jobs', headers={'Origin': 'https://evil.example'}).status_code, 403)
            self.assertEqual(client.get('/jobs/not-a-job').status_code, 404)
            self.assertEqual(client.get('/jobs/not-a-job/video').status_code, 404)
            job_id = self.submit(client).json()['id']
            self.wait_for(client, job_id, 'succeeded')
            (self.settings.jobs_directory/job_id/'result.mp4').unlink()
            self.assertEqual(client.get(f'/jobs/{job_id}/video').status_code, 410)

    def test_decoder_rejects_invalid_output(self):
        path = self.settings.project_root/'invalid.mp4'; path.write_bytes(b'not video')
        with self.assertRaisesRegex(ValueError, 'full decoding'):
            validate_output(path)

    def test_runtime_timeout_stops_child_and_reports_failure(self):
        settings = Settings(self.settings.project_root, generation_timeout=0.05)
        runtime = MlxRuntime(settings)
        log = self.settings.project_root/'generation.log'
        lock = self.settings.project_root/'lock'; lock.touch()
        process_holder = []
        original_popen = subprocess.Popen

        def slow_process(*args, **kwargs):
            process = original_popen([sys.executable, '-c', 'import time; time.sleep(30)'], **kwargs)
            process_holder.append(process)
            return process

        def invoke_runner(backend, image, prompt, output):
            backend.runner(['unused'], self.settings.project_root)

        with lock.open() as lock_file, patch.object(runtime, '_verify_config', return_value={'sample_neg_prompt': 'negative'}), \
             patch('dancing_angels_ai.api.runtime.subprocess.Popen', side_effect=slow_process), \
             patch('dancing_angels_ai.api.runtime.MlxVideoBackend.generate', invoke_runner):
            with self.assertRaises(TimeoutError):
                runtime.generate(lock, 'prompt', self.settings.project_root/'result.mp4', log,
                                 threading.Event(), lock_file.fileno())
        self.assertIsNotNone(process_holder[0].poll())


if __name__ == '__main__':
    unittest.main()
