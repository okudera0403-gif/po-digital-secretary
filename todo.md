# 下肢装具見積システム - マスターデータ全面更新

## 完了済み
- [x] 新テーブル作成: base_prices, manufacturing_joints, manufacturing_supports, manufacturing_additions, finished_parts_master
- [x] Excelデータ投入: 基本価格(10件), 継手(8件), 支持部(19件), 加算(18件), 完成用部品(11件)

## 実装タスク
- [ ] EstimatePage.tsx を新しいデータ構造に合わせて全面書き換え
  - Step①: 基本価格コード選択 (A-1〜A-10) + 価格方式 (採型/採寸)
  - Step②: 製作要素_継手 選択 (チェックボックス + 数量)
  - Step③: 製作要素_支持部 選択 (チェックボックス + 数量)
  - Step④: 製作要素_加算 選択 (チェックボックス + 数量)
  - Step⑤: 完成用部品 選択 (検索 + チェックボックス)
  - 見積内訳サマリー + 合計金額
  - 保存機能
- [ ] lint & build 確認