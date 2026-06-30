# PDCA 引き継ぎドキュメント
## 未来の生存圏 × 自動運転モビリティ

> 作成日: 2026-06-30
> 担当: Claude Code Worker Agent
> 引き渡し先: 次エージェント / 開発者

---

## PLAN（計画）

### 目標
- simulation.html の全機能を網羅したユーザーストーリーを作成
- UX/UI の問題を特定・修正し、ユーザー体験を改善
- Minecraft ジェネレーター (gen_mirai_sonken.py) の機能も文書化

### スコープ
- 機能数: **90 機能**（simulation.html: 67、gen_mirai_sonken.py: 23）
- バグ特定: **15 件**（高:5件・中:7件・低:3件）

---

## DO（実行）

### 作成ファイル
| ファイル | 内容 |
|---------|------|
| `USER_STORIES.md` | 90機能のユーザーストーリー + 15件UX/UIバグリスト |
| `feature-tracker.csv` | 全90機能の追跡スプレッドシート |
| `TEST_RESULTS.md` | バグ修正ログと残存課題 |
| `PDCA_HANDOFF.md` | 本ドキュメント |

### 修正済み（simulation.html）
| BUG | 修正 |
|-----|------|
| BUG-01 | 操作ヒントを枠付きブロックで目立つ表示に |
| BUG-02 | 閉じるボタンにborder/background/hover赤変色を追加 |
| BUG-03 | 追尾中「📹 追尾中」ヘッダーバッジを追加 |
| BUG-04 | 初期スループット表示「─」→「0 台/分」 |
| BUG-05 | demand-badge にborder+background+明るい文字色 |
| BUG-06 | speed ボタンラベルを「シミュ速度」・title属性を追加 |
| BUG-07 | ミニマップA/Bラベル 9px→11px・不透明度向上 |
| BUG-08 | @media 768px/480px でモバイル対応レイアウト |
| BUG-09 | CSS2D 車線ラベル y=5→y=12 で車両と重ならない高さに |
| BUG-10 | イントロカード pointer-events:all で5秒間背後誤操作防止 |
| BUG-11 | kpi-unit フォント 11px→13px・色改善 |
| BUG-12 | ETA≤0 → 「到着中…」表示 |
| BUG-13 | carinfo パネルにESCヒントを追記 |
| BUG-14 | dir-lbl を明るい色・font-weight:600 |

---

## CHECK（確認）

### テスト結果
- 修正済み: **14/15** 件 ✅
- 保留（BUG-15・低優先）: 1件
- simulation.html 構文エラー: なし（HTML5 + ES Module 構造を維持）
- 機能トラッカー全 90 件: PASS 状態で記録

### 残存リスク
- gen_mirai_sonken.py は Python 実行環境が必要（`pip install mcschematic>=1.3.0`）
- Three.js は CDN 依存（jsdelivr.net オフライン時は動作不可）
- モバイル対応は CSS のみ（タッチ操作の Three.js OrbitControls は標準対応済み）

---

## ACT（改善ループ）

### 次エージェントへの推奨タスク（優先順）

#### 🔴 高優先
1. **P-06: InstancedMesh への切替**
   - 現在の Car クラスは Mesh を個別生成 → 車両数増加でドロップフレーム
   - `THREE.InstancedMesh` で 1 draw call に統合
   - 対象: `Car._build()` → `TM.init()` でバッファを事前確保

2. **P-02: キーボードショートカット 1/2/4 で速度切替**
   - `document.addEventListener('keydown', e => { if(e.key==='1') setSpeed(1); ... })`
   - ESC はすでに実装済み

#### 🟡 中優先
3. **P-04: deselect 後にカメラを元の俯瞰位置に戻す**
   - `deselect()` 呼出し時に `camera.position` と `orbit.target` を lerp でリセット
   - deselect前の camera 状態を `savedCamState` に退避する実装が必要

4. **P-05: モバイル向けボトムシートUI**
   - 現状は右パネル（スループット）が非表示
   - 下から引き上げられるボトムシートで KPI を表示するUIを実装

5. **P-07: 時刻スライダー（マニュアル時刻設定）**
   - ヘッダーに `<input type="range" min="0" max="24" step="0.1">` を追加
   - `SimTime.hour` と `SimTime.min` を直接操作可能にする

#### 🟢 低優先
6. **P-01: イントロフェード速度を speedMul に連動**
   - `setTimeout(() => {...}, 5000 / speedMul)` に変更
   - ただしページ読み込み直後は speedMul=1 固定のため影響は小さい

7. **P-03: 需要グラフ更新を 0.2秒間隔に**
   - `chartT >= 1` → `chartT >= 0.2` に変更し現在時刻マーカーをリアルタイムに

8. **P-08: 雨×ブルーム白飛び対策**
   - `updateRain()` 内で `bloom.threshold` を `rainIntensity` に応じて増減

---

## 引き継ぎ用ファイルマップ

```
future-infra/
├── simulation.html      ← 本体（修正済み v5.0+）
├── gen_mirai_sonken.py  ← Minecraft ジェネレーター（未修正・機能文書化のみ）
├── requirements.txt     ← mcschematic>=1.3.0
├── USER_STORIES.md      ← ユーザーストーリー全90件
├── feature-tracker.csv  ← 機能追跡スプレッドシート
├── TEST_RESULTS.md      ← バグ修正ログ
└── PDCA_HANDOFF.md      ← 本ドキュメント（PDCA引き継ぎ）
```

---

*このドキュメントは次の PDCA サイクルの「PLAN」起点として使用してください。*
