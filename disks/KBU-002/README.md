# KBU-002

[全ディスク一覧へ](../../README.md)

<!-- disk-notes:start -->
## 内容・保管方針

実験者コメントを2026-11-04に整理。削除可の項目も、データ本体は削除していません。

| ディレクトリ | 内容 | 位置づけ |
|---|---|---|
| `ayamashita/230124` | 共同研究のデータ処理 | 全データが揃っておらず、利用価値は限定的かもしれない |
| `mat-HCA` | まつうら氏との共著論文に使用したデータ。trypsin・toma・muraki等 | **非常に重要** |
| `nogi` | 共同研究データ。`210715`・`220126`・`221018` | 論文化済みで今後の利用優先度は低い |
| `sengoku` | コラボの可能性を考えて保管 | おそらく今後は参照しない |
| `trypsin-swsx` | まつうら氏・なかやま氏が収集したトリプシン | 結果として保管。本人は今後使わないかもしれない |
| `yoshikazu` | おそらくお蔵入りのデータ | 不要。実験者判断で**削除可・未削除** |

### trypsin-swsx の内容

クライオプロテクタントを入れるだけで結晶構造が変わる可能性を示す結果として保管している（実験者説明）。
`ZOOPREP_230207_mat_BL32XU_zoo.csv` は `sample_name=trypsin`、`dose_ds=10`、`reduced_fact=1`、`ntimes=1`、`total_osc=10`。10 MGy・10°収集の設定で、KAMO処理結果もある。
`yoshikazu` は `YT0001-01〜16`、`YT0002-01〜16` を収録。

### バックアップ状況

`rsync.com` にmat-HCA・trypsin-swsxを `/mnt/knas/Data/` へコピーするコマンドがある。ただし実行完了やコピー内容の一致は未確認。その他の完全性・コピー照合も未確認。
<!-- disk-notes:end -->

## 最上階層の目録

取得日時: 2026-11-04T15:12:13+09:00

UUID: `f291ce8a-8331-4434-a988-a14f362a4a2e`

直下のみを取得。ディレクトリ内の容量・件数は未計測。隠し項目も含み、リンクは辿りません。

| 名前 | 種類 | ファイルサイズ |
|---|---|---:|
| ayamashita | directory | — |
| mat-HCA | directory | — |
| nogi | directory | — |
| sengoku | directory | — |
| trypsin-swsx | directory | — |
| yoshikazu | directory | — |
| rsync.com | file | 91.0 B |
