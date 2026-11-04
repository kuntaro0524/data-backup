# KBU ディスク一覧

取得日時: 2026-11-04T12:21:11+09:00

今回マウントされている KBU: **8 台**

| ディスク | 全容量 | 空き容量 | 直下の項目数 | 取得状況 |
|---|---:|---:|---:|---|
| [KBU-002](disks/KBU-002/README.md) | 14.4 TiB | 145.8 GiB | 7 | complete |
| [KBU-004](disks/KBU-004/README.md) | 14.4 TiB | 6.1 TiB | 7 | complete |
| [KBU-005](disks/KBU-005/README.md) | 14.4 TiB | 3.6 TiB | 16 | complete |
| [KBU-006](disks/KBU-006/README.md) | 18.1 TiB | 4.3 TiB | 7 | complete |
| [KBU-007](disks/KBU-007/README.md) | 18.1 TiB | 11.6 TiB | 13 | complete |
| [KBU-008](disks/KBU-008/README.md) | 18.1 TiB | 12.3 TiB | 4 | complete |
| [KBU-009](disks/KBU-009/README.md) | 14.4 TiB | 13.7 TiB | 1 | complete |
| [KBU-R001](disks/KBU-R001/README.md) | 14.4 TiB | 13.7 TiB | 2 | complete |

## 更新方法

```bash
python3 scripts/catalog.py
```

Linux の findmnt と Python 3 を使用します。HDD への書き込みやデータの変更は行いません。
容量は 1024 基準です。ディレクトリ内部の走査、サイズ集計、バックアップ内容の照合は未実施です。
一覧は今回接続中のディスクのみ。接続されていないディスクの既存の目録は削除しません。
各ディスクの catalog.json に UUID・マウント先・バイト単位の容量・取得エラーを保存します。
