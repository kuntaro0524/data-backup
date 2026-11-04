#!/usr/bin/env python3
"""Collect mounted KBU root entries without traversing their contents."""
import json
import os
import stat
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def human(value):
    for unit in ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB'):
        if value < 1024 or unit == 'PiB':
            return f'{value:.1f} {unit}'
        value /= 1024


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', '&#10;').replace('\r', '&#13;')


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8')
    temporary.replace(path)


def main():
    mounts = json.loads(subprocess.check_output(
        ['findmnt', '--json', '--list', '--output', 'SOURCE,TARGET,FSTYPE,UUID'], text=True))['filesystems']
    mounts = [m for m in mounts if Path(m['target']).name.startswith('KBU-')]
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    rows = []
    for mount in sorted(mounts, key=lambda m: m['target']):
        path = Path(mount['target'])
        disk = dict(name=path.name, mount=mount, collected_at=now, entries=[], errors=[])
        try:
            usage = os.statvfs(path)
            disk.update(total_bytes=usage.f_blocks * usage.f_frsize,
                        available_bytes=usage.f_bavail * usage.f_frsize)
            with os.scandir(path) as entries:
                for entry in entries:
                    item = {'name': entry.name}
                    try:
                        info = entry.stat(follow_symlinks=False)
                        item['type'] = ('directory' if stat.S_ISDIR(info.st_mode) else
                                        'file' if stat.S_ISREG(info.st_mode) else
                                        'symlink' if stat.S_ISLNK(info.st_mode) else 'other')
                        if item['type'] == 'file':
                            item['size_bytes'] = info.st_size
                    except OSError as exc:
                        item['type'] = 'unknown'
                        disk['errors'].append(f'{entry.name}: {exc}')
                    disk['entries'].append(item)
        except OSError as exc:
            disk['errors'].append(str(exc))
        disk['entries'].sort(key=lambda e: (e['type'] != 'directory', e['name']))
        disk['status'] = 'partial' if disk['errors'] else 'complete'
        base = ROOT / 'disks' / path.name
        write(base / 'catalog.json', json.dumps(disk, ensure_ascii=False, indent=2) + '\n')
        lines = [f'# {path.name}', '', f'取得日時: {now}', '',
                 f'UUID: `{mount.get("uuid") or "unknown"}`', '',
                 '直下のみを取得。ディレクトリ内の容量・件数は未計測。隠し項目も含み、リンクは辿りません。', '',
                 '| 名前 | 種類 | ファイルサイズ |', '|---|---|---:|']
        for e in disk['entries']:
            lines.append(f'| {cell(e["name"])} | {e["type"]} | {human(e["size_bytes"]) if "size_bytes" in e else "—"} |')
        if disk['errors']:
            lines += ['', '取得エラー:', '', *[f'- {cell(e)}' for e in disk['errors']]]
        write(base / 'README.md', '\n'.join(lines) + '\n')
        rows.append(disk)
    lines = ['# KBU ディスク一覧', '', f'取得日時: {now}', '',
             f'今回マウントされている KBU: **{len(rows)} 台**', '',
             '| ディスク | 全容量 | 空き容量 | 直下の項目数 | 取得状況 |', '|---|---:|---:|---:|---|']
    for d in rows:
        lines.append(f'| [{d["name"]}](disks/{d["name"]}/README.md) | '
                     f'{human(d["total_bytes"]) if "total_bytes" in d else "不明"} | '
                     f'{human(d["available_bytes"]) if "available_bytes" in d else "不明"} | '
                     f'{len(d["entries"])} | {d["status"]} |')
    lines += ['', '## 更新方法', '', '```bash', 'python3 scripts/catalog.py', '```', '',
              'Linux の findmnt と Python 3 を使用します。HDD への書き込みやデータの変更は行いません。',
              '容量は 1024 基準です。ディレクトリ内部の走査、サイズ集計、バックアップ内容の照合は未実施です。',
              '一覧は今回接続中のディスクのみ。接続されていないディスクの既存の目録は削除しません。',
              '各ディスクの catalog.json に UUID・マウント先・バイト単位の容量・取得エラーを保存します。']
    write(ROOT / 'README.md', '\n'.join(lines) + '\n')
    print(f'Collected {len(rows)} disks; {sum(bool(d["errors"]) for d in rows)} with errors.')


if __name__ == '__main__':
    main()
