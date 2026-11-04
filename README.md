# KBU ディスク一覧

[作業の引き継ぎ・次に調査する内容](HANDOFF.md)

各ディスク名から、ディレクトリ別のコメント・重要度・解析状況を確認できます。

取得日時: 2026-11-04T12:34:25+09:00

今回マウントされている KBU: **8 台**

| ディスク | 全容量 | 空き容量 | 直下の項目数 | 取得状況 | 内容・コメント |
|---|---:|---:|---:|---|---|
| [KBU-002](disks/KBU-002/README.md) | 14.4 TiB | 145.8 GiB | 7 | complete | mat-HCAは共著論文使用・非常に重要。共同研究データと削除可のデータを収録。詳細は個別README。 |
| [KBU-004](disks/KBU-004/README.md) | 14.4 TiB | 6.1 TiB | 7 | complete | 単著論文で参照したAT2R・hattori・Polyhedra・サーモリシン。SunoHgSADは論文未使用。 |
| [KBU-005](disks/KBU-005/README.md) | 14.4 TiB | 3.6 TiB | 16 | complete | 氷の結晶、PDB登録済みShioi、重要ZOOログ、PSII、Hirota複合体解析等。詳細・解析概要は個別README。 |
| [KBU-006](disks/KBU-006/README.md) | 18.1 TiB | 4.3 TiB | 7 | complete | 用途・重要度の聞き取りは未実施。次の整理対象。 |
| [KBU-007](disks/KBU-007/README.md) | 18.1 TiB | 11.6 TiB | 13 | complete | 2025/02/01・02/08・06/11の10 MGyトリプシン：利用可能。その他は未整理。 |
| [KBU-008](disks/KBU-008/README.md) | 18.1 TiB | 12.3 TiB | 4 | complete | 2025/07/14・20〜22の5 MGy×2回設定のトリプシン：利用可能。変更日の正確な境界は未確定。 |
| [KBU-009](disks/KBU-009/README.md) | 14.4 TiB | 13.7 TiB | 1 | complete | 直下はlost+foundのみ。ほぼ空。改名を検討中。 |
| [KBU-R001](disks/KBU-R001/README.md) | 14.4 TiB | 13.7 TiB | 2 | complete | ほぼ空だがTESTあり。用途・削除可否は未確認。改名を検討中。 |

線量の変更履歴・格子定数の詳細は [Hirata 実験の記録](analysis/hirata_conditions.md)を参照。

「内容・コメント」列はこの README で直接編集できます。目録を再取得しても保持されます。表の区切りと衝突するため、コメント内の縦棒は `&#124;` と記入してください。

## 更新方法

```bash
python3 scripts/catalog.py
```

Linux の findmnt と Python 3 を使用します。HDD への書き込みやデータの変更は行いません。
容量は 1024 基準です。ディレクトリ内部の走査、サイズ集計、バックアップ内容の照合は未実施です。
一覧は今回接続中のディスクのみ。接続されていないディスクの既存の目録は削除しません。
各ディスクの catalog.json に UUID・マウント先・バイト単位の容量・取得エラーを保存します。

各ディスクの詳細コメントは `disks/<ディスク名>/README.md` の `disk-notes:start` / `disk-notes:end` コメント間で編集できます。この範囲は目録更新時にも保持されます。
