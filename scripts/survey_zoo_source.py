#!/usr/bin/env python3
"""Read-only remote survey. Emit one JSON object per line; progress to stderr."""
import datetime
import json
import os
from pathlib import Path
import socket
import subprocess
import sys


def emit(value):
    print(json.dumps(value, ensure_ascii=True), flush=True)


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else '/user/target/Auto/2026A')
    started = datetime.datetime.now().astimezone().isoformat()
    emit({'type': 'start', 'host': socket.gethostname(), 'root': str(root),
          'started_at': started, 'scope': 'all immediate entries; directory sizes include all descendants',
          'size_method': 'GNU du apparent bytes; one filesystem; no symlink traversal'})
    failures = 0
    try:
        entries = sorted(root.iterdir())
        for entry in entries:
            print('Surveying ' + str(entry), file=sys.stderr, flush=True)
            if entry.is_symlink():
                emit({'type': 'symlink', 'path': str(entry), 'target': os.readlink(entry)})
                continue
            if entry.is_dir():
                # Separate invocation per experiment: hard links across experiments
                # count in both, since independent copies may store both.
                result = subprocess.run(['du', '-x', '--apparent-size', '--block-size=1',
                                         '--max-depth=1', '--null', '--', str(entry)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                sizes = []
                for record in result.stdout.split(b'\0'):
                    if record:
                        size, path = record.split(b'\t', 1)
                        sizes.append({'path': os.fsdecode(path), 'bytes': int(size)})
                errors = os.fsdecode(result.stderr)
                failures += result.returncode != 0
                emit({'type': 'directory', 'path': str(entry), 'sizes': sizes,
                      'complete': result.returncode == 0, 'errors': errors})
            else:
                emit({'type': 'file', 'path': str(entry), 'bytes': entry.stat().st_size})
    except OSError as exc:
        emit({'type': 'error', 'error': str(exc)})
        return 1
    emit({'type': 'finish', 'finished_at': datetime.datetime.now().astimezone().isoformat(),
          'failed_directories': failures,
          'caveat': 'Live source: files may change during survey. Sizes include processed data; raw-data selection is not yet defined.'})
    return int(bool(failures))


if __name__ == '__main__':
    sys.exit(main())
