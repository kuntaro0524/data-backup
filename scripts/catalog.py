#!/usr/bin/env python3
"""Collect mounted KBU root entries without traversing their contents."""
import json
import os
import stat
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTES_START = '<!-- disk-notes:start -->'
NOTES_END = '<!-- disk-notes:end -->'


def preserved_notes(path):
    if not path.exists():
        return ''
    content = path.read_text(encoding='utf-8')
    if NOTES_START not in content and NOTES_END not in content:
        return ''
    if content.count(NOTES_START) != 1 or content.count(NOTES_END) != 1:
        raise ValueError(f'Invalid disk comment markers: {path}')
    start = content.index(NOTES_START)
    end = content.index(NOTES_END)
    if end < start:
        raise ValueError(f'Invalid disk comment marker order: {path}')
    return content[start:end + len(NOTES_END)]


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
    # README is the source of truth for handwritten disk comments.
    comments = {}
    readme = ROOT / 'README.md'
    if readme.exists():
        for line in readme.read_text(encoding='utf-8').splitlines():
            fields = line.split('|')
            if len(fields) == 8 and fields[1].strip().startswith('[KBU-'):
                name = fields[1].strip().split(']')[0][1:]
                comments[name] = fields[6].strip()
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
        notes = preserved_notes(base / 'README.md')
        lines = [f'# {path.name}', '', '[全ディスク一覧へ](../../README.md)', '']
        if notes:
            lines += [notes, '']
        lines += ['## 最上階層の目録', '', f'取得日時: {now}', '',
                 f'UUID: `{mount.get("uuid") or "unknown"}`', '',
                 '直下のみを取得。ディレクトリ内の容量・件数は未計測。隠し項目も含み、リンクは辿りません。', '',
                 '| 名前 | 種類 | ファイルサイズ |', '|---|---|---:|']
        for e in disk['entries']:
            lines.append(f'| {cell(e["name"])} | {e["type"]} | {human(e["size_bytes"]) if "size_bytes" in e else "—"} |')
        if disk['errors']:
            lines += ['', '取得エラー:', '', *[f'- {cell(e)}' for e in disk['errors']]]
        write(base / 'README.md', '\n'.join(lines) + '\n')
        rows.append(disk)
    lines = ['# KBU ディスク一覧', '', '[作業の引き継ぎ・次に調査する内容](HANDOFF.md)', '',
             '各ディスク名から、ディレクトリ別のコメント・重要度・解析状況を確認できます。', '',
             f'取得日時: {now}', '',
             f'今回マウントされている KBU: **{len(rows)} 台**', '',
             '| ディスク | 全容量 | 空き容量 | 直下の項目数 | 取得状況 | 内容・コメント |', '|---|---:|---:|---:|---|---|']
    for d in rows:
        lines.append(f'| [{d["name"]}](disks/{d["name"]}/README.md) | '
                     f'{human(d["total_bytes"]) if "total_bytes" in d else "不明"} | '
                     f'{human(d["available_bytes"]) if "available_bytes" in d else "不明"} | '
                     f'{len(d["entries"])} | {d["status"]} | {comments.get(d["name"], "未整理")} |')
    lines += ['', '線量の変更履歴・格子定数の詳細は [Hirata 実験の記録](analysis/hirata_conditions.md)を参照。', '',
              '「内容・コメント」列はこの README で直接編集できます。目録を再取得しても保持されます。表の区切りと衝突するため、コメント内の縦棒は `&#124;` と記入してください。', '', '## 更新方法', '', '```bash', 'python3 scripts/catalog.py', '```', '',
              '各ディスクの詳細コメントは disks/<ディスク名>/README.md の disk-notes:start / disk-notes:end コメント間で編集してください。この範囲は目録更新時にも保持されます。',
              'Linux の findmnt と Python 3 を使用します。HDD への書き込みやデータの変更は行いません。',
              '容量は 1024 基準です。ディレクトリ内部の走査、サイズ集計、バックアップ内容の照合は未実施です。',
              '一覧は今回接続中のディスクのみ。接続されていないディスクの既存の目録は削除しません。',
              '各ディスクの catalog.json に UUID・マウント先・バイト単位の容量・取得エラーを保存します。']
    write(ROOT / 'README.md', '\n'.join(lines) + '\n')
    print(f'Collected {len(rows)} disks; {sum(bool(d["errors"]) for d in rows)} with errors.')


if __name__ == '__main__':
    main()
