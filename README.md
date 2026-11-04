# KBU ディスク一覧

取得日時: 2026-11-04T12:34:25+09:00

今回マウントされている KBU: **8 台**

| ディスク | 全容量 | 空き容量 | 直下の項目数 | 取得状況 | 内容・コメント |
|---|---:|---:|---:|---|---|
| [KBU-002](disks/KBU-002/README.md) | 14.4 TiB | 145.8 GiB | 7 | complete | ayamashita（230124：共同研究のデータ処理。全データが揃っておらず、利用価値は限定的かもしれない／実験者コメント）、mat-HCA（【非常に重要】まつうら氏との共著論文に使用したデータ。trypsin・toma等）、nogi（210715・220126・221018：共同研究データ。論文化済みで、今後の利用優先度は低い／実験者コメント）、sengoku（コラボの可能性を考えて保管しているが、おそらく今後は参照しない／実験者コメント）、trypsin-swsx、yoshikazuを収録。trypsin-swsxは230207のCSVでtrypsin・dose_ds=10・10°収集設定。その他の詳細・コピー照合は未確認。 |
| [KBU-004](disks/KBU-004/README.md) | 14.4 TiB | 6.1 TiB | 7 | complete | 未整理 |
| [KBU-005](disks/KBU-005/README.md) | 14.4 TiB | 3.6 TiB | 16 | complete | 未整理 |
| [KBU-006](disks/KBU-006/README.md) | 18.1 TiB | 4.3 TiB | 7 | complete | 未整理 |
| [KBU-007](disks/KBU-007/README.md) | 18.1 TiB | 11.6 TiB | 13 | complete | Hirata の2025/02/01・02/08・06/11収集分：10 MGyトリプシンとして利用可能。その他は未整理。 |
| [KBU-008](disks/KBU-008/README.md) | 18.1 TiB | 12.3 TiB | 4 | complete | Hirata の2025/07/14・07/20〜22収集分：5 MGy × 2回の設定。5 MGyトリプシンとして利用可能。5 MGy設定の最初の確認日は7/14（正確な変更日は未確定）。その他は未整理。 |
| [KBU-009](disks/KBU-009/README.md) | 14.4 TiB | 13.7 TiB | 1 | complete | 未整理 |
| [KBU-R001](disks/KBU-R001/README.md) | 14.4 TiB | 13.7 TiB | 2 | complete | 未整理 |

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
