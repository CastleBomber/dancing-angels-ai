"""Durable per-job records and exactly one local GPU worker."""
import copy
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
import queue
import re
import shutil
import threading
import time
import traceback
import uuid

from .config import PRESET, SHUFFLE_PROMPT, reference_model_config
from .runtime import GenerationStopped


class QueueFull(RuntimeError):
    pass


class Unavailable(RuntimeError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


class JobManager:
    def __init__(self, settings, runtime):
        self.settings, self.runtime = settings, runtime
        self._guard = threading.RLock()
        self._queue = queue.Queue(maxsize=settings.queue_slots)
        self._stop = threading.Event()
        self._records = {}
        self._lock_file = None
        self._thread = None
        self.readiness = {"ready": False, "checks": []}

    def start(self):
        self.settings.jobs_directory.mkdir(parents=True, exist_ok=True)
        self._lock_file = self.settings.lock_path.open("a+")
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self._lock_file.close()
            self._lock_file = None
            raise RuntimeError("Another API or its generation process still owns the GPU worker lock")
        try:
            for path in self.settings.jobs_directory.glob("*/job.json"):
                record = json.loads(path.read_text())
                job_id = record['id']
                if not re.fullmatch(r"[0-9a-f]{32}", job_id) or path.parent.name != job_id:
                    raise ValueError(f"Invalid stored job record: {path}")
                self._records[job_id] = record
                if record['status'] in ("queued", "running"):
                    record.update(status="failed", finished_at=now(), error={
                        "code": "interrupted", "message": "API restarted before completion; submit a new job",
                    })
                    self._save(record)
            self.readiness = self.runtime.readiness()
            self._thread = threading.Thread(target=self._work, name="mlx-generation", daemon=False)
            self._thread.start()
        except BaseException:
            self._lock_file.close()
            self._lock_file = None
            raise

    def _save(self, record):
        directory = self.settings.jobs_directory / record['id']
        temporary = directory / "job.json.tmp"
        with temporary.open("w") as stream:
            json.dump(record, stream, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(directory / "job.json")

    def submit(self, content, image_info):
        with self._guard:
            if self._stop.is_set() or not self.readiness['ready'] or not self._thread.is_alive():
                raise Unavailable("Generation runtime is unavailable; check /ready")
            if self._queue.full():
                raise QueueFull("Generation queue is full; retry later")
            job_id = uuid.uuid4().hex
            directory = self.settings.jobs_directory / job_id
            directory.mkdir()
            record = {
                "id": job_id, "status": "queued", "action": "shuffle",
                "created_at": now(), "started_at": None, "finished_at": None,
                "runtime_seconds": None, "error": None, "output": None,
                "preset": copy.deepcopy(PRESET), "prompt": SHUFFLE_PROMPT,
                "model_config": reference_model_config(),
                "input": {**image_info, "bytes": len(content),
                          "sha256": hashlib.sha256(content).hexdigest()},
            }
            try:
                (directory / ("input." + image_info['extension'])).write_bytes(content)
                (directory / "generation.log").touch()
                self._save(record)
            except BaseException:
                shutil.rmtree(directory)
                raise
            self._records[job_id] = record
            self._queue.put_nowait(job_id)
            return self._public(record)

    def get(self, job_id):
        with self._guard:
            return self._public(self._records[job_id])

    def _public(self, record):
        result = {key: copy.deepcopy(record[key]) for key in (
            'id', 'status', 'action', 'created_at', 'started_at', 'finished_at',
            'runtime_seconds', 'error', 'output', 'preset', 'input',
        )}
        result['output_url'] = (
            f"/jobs/{record['id']}/video" if record['status'] == 'succeeded' else None
        )
        return result

    def counts(self):
        with self._guard:
            return {"running": sum(r['status'] == 'running' for r in self._records.values()),
                    "queued": sum(r['status'] == 'queued' for r in self._records.values()),
                    "queue_capacity": self.settings.queue_slots}

    def readiness_report(self):
        report = copy.deepcopy(self.readiness)
        worker_ready = bool(self._thread and self._thread.is_alive() and not self._stop.is_set())
        report['checks'].append({'name': 'job worker', 'passed': worker_ready})
        report['ready'] = report['ready'] and worker_ready
        return report

    def _work(self):
        while not self._stop.is_set():
            try:
                job_id = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            with self._guard:
                record = self._records[job_id]
                if self._stop.is_set():
                    self._queue.task_done()
                    break
                record.update(status="running", started_at=now())
                self._save(record)
            directory = self.settings.jobs_directory / job_id
            start = time.monotonic()
            try:
                output = self.runtime.generate(
                    directory / ("input." + record['input']['extension']),
                    record['prompt'], directory / "result.mp4",
                    directory / "generation.log", self._stop, self._lock_file.fileno(),
                )
                update = {"status": "succeeded", "output": output}
            except Exception as error:
                with (directory / "generation.log").open("a") as log:
                    traceback.print_exc(file=log)
                code = ("interrupted" if isinstance(error, GenerationStopped) else
                        "generation_timeout" if isinstance(error, TimeoutError) else "generation_failed")
                update = {"status": "failed", "error": {"code": code, "message": str(error)[:500]}}
            with self._guard:
                record.update(**update, finished_at=now(), runtime_seconds=round(time.monotonic() - start, 3))
                self._save(record)
            self._queue.task_done()

    def close(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        with self._guard:
            for record in self._records.values():
                if record['status'] in ('queued', 'running'):
                    record.update(status="failed", finished_at=now(), error={
                        "code": "interrupted", "message": "API stopped before completion; submit a new job",
                    })
                    self._save(record)
        if self._lock_file:
            # Closing (not LOCK_UN) preserves a lock inherited by an orphan child.
            self._lock_file.close()
            self._lock_file = None
