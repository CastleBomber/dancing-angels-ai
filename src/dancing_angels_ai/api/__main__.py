"""Start exactly one API process on loopback; do not use uvicorn multi-worker mode."""
import argparse
from pathlib import Path
import uvicorn

from .config import Settings
from .server import create_app


def main():
    parser = argparse.ArgumentParser(description='Local MLX image-to-video API')
    parser.add_argument('--project-root', type=Path, default=Path.cwd())
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(create_app(Settings(args.project_root)), host='127.0.0.1', port=args.port,
                workers=1, limit_concurrency=16, timeout_keep_alive=5)


if __name__ == '__main__':
    main()
