# ウェブサイト メンテナンスマニュアル

**対象サイト**: 個人学術ウェブサイト (Hugo + Tailwind CSS)
**最終更新**: 2026-02-25

---

## 目次

1. [概要と技術スタック](#1-概要と技術スタック)
2. [環境セットアップ](#2-環境セットアップ)
3. [ディレクトリ構造](#3-ディレクトリ構造)
4. [ローカル開発サーバーの起動](#4-ローカル開発サーバーの起動)
5. [コンテンツの更新方法（日常的な作業）](#5-コンテンツの更新方法日常的な作業)
   - [5.1 プロフィール・基本情報の更新](#51-プロフィール基本情報の更新)
   - [5.2 経歴の更新](#52-経歴の更新)
   - [5.3 研究業績（論文）の追加](#53-研究業績論文の追加)
   - [5.4 研究内容の更新](#54-研究内容の更新)
   - [5.5 担当講義の更新](#55-担当講義の更新)
6. [ページ本文の編集](#6-ページ本文の編集)
7. [画像の更新](#7-画像の更新)
8. [本番ビルドとデプロイ](#8-本番ビルドとデプロイ)
9. [別PCへの移行手順](#9-別pcへの移行手順)
10. [トラブルシューティング](#10-トラブルシューティング)
11. [メンテナンス頻度チェックリスト](#11-メンテナンス頻度チェックリスト)

---

## 1. 概要と技術スタック

このウェブサイトは以下の技術で構築されています。

| 技術 | 役割 | バージョン |
|------|------|-----------|
| [Hugo](https://gohugo.io/) | 静的サイトジェネレーター | 0.156.0+ (Extended 必須) |
| [Tailwind CSS](https://tailwindcss.com/) | CSSフレームワーク | v4.2.1 |
| Node.js / npm | パッケージ管理 (Tailwind のビルド用) | 任意の LTS 版 |

**コンテンツ更新の基本原則**: ほぼすべての更新は `/data/` フォルダ内の YAML ファイルを編集するだけで完結します。HTML や Hugo のテンプレートを触る必要はありません。

---

## 2. 環境セットアップ

### 必要なソフトウェア

1. **Hugo Extended 版** (通常版ではなく Extended 版が必要)
   ```bash
   brew install hugo    # macOS の場合
   hugo version         # インストール確認 (extended と表示されること)
   ```

2. **Node.js と npm**
   ```bash
   brew install node    # macOS の場合
   node --version       # インストール確認
   ```

### 初回セットアップ（新しいPCでの作業開始時）

プロジェクトフォルダに移動後、以下を実行します。

```bash
npm install
```

> **重要**: `node_modules/` フォルダはPC環境固有のファイルを含むため、別のPCに持ち込んでも使えません。新しいPCでは必ず `npm install` を実行してください。詳細は [9章](#9-別pcへの移行手順) を参照。

---

## 3. ディレクトリ構造

```
academic-site/
├── data/                   ★ コンテンツの中心（ここを主に編集する）
│   ├── profile.yml         → プロフィール・基本情報・連絡先
│   ├── career.yml          → 経歴
│   ├── publications.yml    → 研究業績（論文・発表）
│   ├── research.yml        → 研究内容の説明
│   └── teaching.yml        → 担当講義
│
├── content/                補足的な本文テキスト（あまり触らない）
│   ├── _index.md           → トップページ
│   ├── publications/_index.md
│   ├── research/_index.md
│   ├── teaching/_index.md
│   └── en/                 → 英語版ページ（同じ構造）
│
├── static/
│   └── images/             ★ 画像ファイルの置き場
│       ├── avatar.jpg      → プロフィール写真
│       └── og-default.png  → SNS シェア用画像
│
├── assets/
│   └── css/main.css        デザイン設定（触ることはほぼない）
│
├── layouts/                HTML テンプレート（触ることはほぼない）
├── hugo.toml               サイト全体の設定（URL 変更時のみ）
├── package.json            npm 設定
└── public/                 ビルド後の成果物（自動生成・直接編集しない）
```

---

## 4. ローカル開発サーバーの起動

サイトの見た目を確認しながら編集する場合は、以下のコマンドを実行します。

```bash
hugo server -D
```

または

```bash
npm run dev
```

ブラウザで `http://localhost:1313/` を開くと確認できます。ファイルを保存するたびにブラウザが自動的に更新されます。

サーバーを停止するには `Ctrl + C` を押します。

---

## 5. コンテンツの更新方法（日常的な作業）

### 5.1 プロフィール・基本情報の更新

**ファイル**: `data/profile.yml`

このファイルでは以下の情報を管理しています。

- 氏名（日英）
- 職位（日英）
- 所属機関（日英）
- 住所（日英）
- メールアドレス
- 各種リンク（GitHub、Google Scholar、ORCID、ResearchGate）
- 自己紹介文（日英）
- プロフィール写真のパス

**編集例：職位と所属が変わった場合**

```yaml
name:
  ja: "金田 邦雄"
  en: "Kunio Kaneta"

position:
  ja: "准教授"               # ← 変更
  en: "Associate Professor"  # ← 変更

institution:
  ja: "○○大学 理学部"        # ← 変更
  en: "Faculty of Science, XX University"  # ← 変更
```

**自己紹介文の更新**（複数行テキストは `|` の後にインデントして記述）

```yaml
bio:
  ja: |
    理論物理学を専門とする研究者です。
    特に初期宇宙の物理に興味を持っています。
  en: |
    I am a researcher specializing in theoretical physics.
    My research interests include early universe physics.
```

**ソーシャルリンクの更新**（不要なものは空欄にする）

```yaml
links:
  github: "https://github.com/your-username"
  google_scholar: "https://scholar.google.com/citations?user=XXXXX"
  orcid: "0000-0000-0000-0000"
  researchgate: ""   # 使わない場合は空欄
```

---

### 5.2 経歴の更新

**ファイル**: `data/career.yml`

経歴の一覧で、新しい職歴を **先頭に追加** します（表示は上から順に表示されます）。

**書式**

```yaml
- year: 2025--       # 現在進行中の場合は "--" で終わる
  title:
    ja: "○○大学 准教授"
    en: "Associate Professor, XX University"

- year: 2023--2025   # 期間の場合は "開始年--終了年"
  title:
    ja: "○○大学 助教"
    en: "Assistant Professor, XX University"

- year: 2021         # 単年の場合
  title:
    ja: "博士（理学）取得"
    en: "Ph.D. in Science"
```

---

### 5.3 研究業績（論文）の追加

**ファイル**: `data/publications.yml`

すべての論文・発表がこの1つのファイルで管理されています。ウェブサイトの業績一覧ページは自動的に年順に並び替えられ、種別でフィルタリングできます。

#### 雑誌論文の追加

```yaml
- id: "kaneta2025example"         # 一意のID（ファイル内で重複しなければ何でもよい）
  type: "article"                  # 雑誌論文の場合は "article"
  year: 2025
  authors:
    - "Kaneta, Kunio"              # 著者は "姓, 名" の形式
    - "Tanaka, Hiroshi"
  title: "論文タイトルをここに書く"
  journal: "Physical Review B"
  volume: 110
  issue: 12                        # 号数（不明の場合は削除可）
  pages: "125401"
  doi: "10.1103/PhysRevB.110.125401"   # DOI（不明の場合は削除可）
  arxiv: "2403.12345"              # arXiv ID（番号のみ。不要な場合は削除可）
```

#### 国際会議発表の追加

```yaml
- id: "kaneta2025conf"
  type: "proceedings"              # 会議録の場合は "proceedings"
  year: 2025
  authors:
    - "Kaneta, Kunio"
  title: "発表タイトル"
  booktitle: "Proceedings of the International Conference on ..."
  pages: "112-118"
  doi: ""                          # あれば記入、なければ削除か空欄
```

> **自分の名前の太字表示について**: `hugo.toml` の `params.author = "Kaneta, Kunio"` に設定された名前と一致する著者名が自動的に太字になります。名前の表記が統一されていることを確認してください。

---

### 5.4 研究内容の更新

**ファイル**: `data/research.yml`

研究テーマごとに1エントリで記述します。

```yaml
- id: "dark-matter"                # 一意のID
  title:
    ja: "暗黒物質の研究"
    en: "Dark Matter Research"

  description:
    ja: |
      暗黒物質の性質に関する理論的研究を行っています。
      特に初期宇宙における暗黒物質の生成機構に注目しています。
    en: |
      We conduct theoretical research on the properties of dark matter.
      We focus particularly on the production mechanism of dark matter in the early universe.

  keywords:
    - "Dark Matter"
    - "Early Universe"
    - "Inflation"
```

**数式を含む場合**（LaTeX 形式で記述）

```yaml
- id: "field-theory"
  title:
    ja: "場の量子論"
    en: "Quantum Field Theory"
  description:
    ja: |
      場の量子論の基礎的研究...
    en: |
      Fundamental research on quantum field theory...
  math: true
  equation: "\\mathcal{L} = \\bar{\\psi}(i\\gamma^\\mu \\partial_\\mu - m)\\psi"
  keywords:
    - "QFT"
    - "Lagrangian"
```

> **注意**: YAML 内でバックスラッシュを書く場合は `\\` と二重にします（`\` → `\\`、`\mu` → `\\mu`）。

---

### 5.5 担当講義の更新

**ファイル**: `data/teaching.yml`

学期ごとに1エントリで記述します。新しい学期の講義は**先頭に追加**します。

```yaml
- id: "phys101-2026s"              # 一意のID
  year: 2026

  semester:
    ja: "前期"
    en: "Spring"

  title:
    ja: "基礎物理学"
    en: "Introduction to Physics"

  level:
    ja: "学部1年"
    en: "Undergraduate (1st year)"

  lang: ["ja", "en"]               # 英語ページにも表示する場合
  # lang: ["ja"]                   # 日本語ページのみに表示する場合

  url: "https://syllabus.example.ac.jp/2026/phys101"  # シラバスURL（なければ "" にする）
```

**`lang` フィールドについて**

| 設定 | 日本語ページ | 英語ページ |
|------|-------------|-----------|
| `lang: ["ja"]` | 表示（「日本語のみ」バッジあり） | 非表示 |
| `lang: ["ja", "en"]` | 表示 | 表示 |
| `lang: ["en"]` | 非表示 | 表示 |

---

## 6. ページ本文の編集

`data/` フォルダの YAML に収まらない追記テキスト（例：研究ページへの追加説明）は、`content/` フォルダの Markdown ファイルに書きます。

**ファイル一覧**

| ページ | 日本語 | 英語 |
|--------|--------|------|
| トップ | `content/_index.md` | `content/en/_index.md` |
| 研究 | `content/research/_index.md` | `content/en/research/_index.md` |
| 業績 | `content/publications/_index.md` | `content/en/publications/_index.md` |
| 担当講義 | `content/teaching/_index.md` | `content/en/teaching/_index.md` |

**書式**（TOML フロントマター + Markdown 本文）

```toml
+++
title = "研究"
description = "研究の説明文（ブラウザタブや検索結果に使われる）"
math = true
+++

ここから Markdown で自由に本文を書けます。

数式も書けます：$E = mc^2$

```

> **`math = true`** を指定すると、そのページで $\LaTeX$ 数式（KaTeX）が使えます。

---

## 7. 画像の更新

### プロフィール写真の変更

1. 新しい写真を `static/images/avatar.jpg` に保存（上書き）
2. 推奨サイズ：256×256px 以上の正方形
3. ファイル名を変える場合は `data/profile.yml` の `avatar:` も変更する

```yaml
avatar: "/images/new-photo.jpg"
```

### SNSシェア用画像の変更（OGP画像）

`static/images/og-default.png` を差し替えます。
推奨サイズ：1200×630px

---

## 8. 本番ビルドとデプロイ

### ビルド（HTML/CSS の生成）

```bash
hugo --minify
```

または

```bash
npm run build
```

成果物は `public/` フォルダに生成されます。

### GitHub Pages へのデプロイ

`public/` フォルダの中身を GitHub Pages のリポジトリにプッシュします。

```bash
# public/ フォルダ内に移動してデプロイ
cd public
git init
git add .
git commit -m "Deploy"
git push -f origin main
```

または、GitHub Actions による自動デプロイを設定している場合は、`main` ブランチへのプッシュで自動デプロイされます。

---

## 9. 別PCへの移行手順

`node_modules/` フォルダには macOS/Windows/Linux それぞれ専用のバイナリファイルが含まれます。別のPCに持ち込んでもそのままでは動きません。

### 移行手順

1. **移行してはいけないフォルダ/ファイル**
   - `node_modules/` （絶対に同期・コピーしない）
   - `public/` （ビルドで再生成される）

2. **新しいPCでの初回セットアップ**

   ```bash
   # プロジェクトフォルダに移動後
   npm install   # これだけで OK（node_modules が正しく再作成される）
   hugo server -D
   ```

### QNAP 同期を使っている場合

QNAP の Qsync で同期する際、`node_modules/` フォルダを除外する設定を行うことを強く推奨します。Qsync の除外フィルター設定については [QNAP 公式ドキュメント](https://www.qnap.com/) で「Qsync フィルタールール」を確認してください。

手動で rsync を使っている場合は以下のように除外できます。

```bash
rsync -av --exclude='node_modules/' --exclude='public/' ./academic-site/ user@qnap:/path/to/backup/
```

---

## 10. トラブルシューティング

### `hugo server -D` でエラーが出る

#### エラー: `Permission denied` (tailwindcss)

```
sh: .../node_modules/.bin/tailwindcss: Permission denied
```

**原因**: `node_modules/` を別環境からコピーしてきた場合に発生することがある。
**対処**:

```bash
rm -rf node_modules
npm install
```

#### エラー: `No prebuild or local build of @parcel/watcher found`

```
Error: No prebuild or local build of @parcel/watcher found. Tried @parcel/watcher-darwin-arm64.
```

**原因**: 別OS/アーキテクチャで作成された `node_modules/` を持ち込んだ。
**対処**:

```bash
rm -rf node_modules
npm install
```

#### エラー: `Cannot find module '../lightningcss.darwin-arm64.node'`

**原因**: 上と同じ。`node_modules/` が別環境のもの。
**対処**:

```bash
rm -rf node_modules
npm install
```

#### エラー: `hugo: command not found`

**原因**: Hugo がインストールされていない。
**対処**:

```bash
brew install hugo
```

#### エラー: `requires Hugo Extended`

**原因**: Hugo の通常版をインストールしている（Extended 版が必要）。
**対処**:

```bash
brew uninstall hugo
brew install hugo   # Homebrew の Hugo は Extended 版が含まれる
hugo version        # "extended" と表示されることを確認
```

### YAML のシンタックスエラー

`data/` フォルダの YAML ファイルを編集後にエラーが出る場合、YAML の書式ミスが多いです。

**よくある間違い**

```yaml
# NG: インデントがずれている
- id: "example"
title: "タイトル"   # ← 先頭に空白がない

# OK: 正しいインデント
- id: "example"
  title: "タイトル"   # ← 半角スペース2つのインデント
```

```yaml
# NG: コロンの後のスペースがない
title:"タイトル"

# OK
title: "タイトル"
```

```yaml
# NG: 数式中のバックスラッシュが1つ
equation: "\mu"

# OK: バックスラッシュは2つ
equation: "\\mu"
```

---

## 11. メンテナンス頻度チェックリスト

| タイミング | 作業内容 | 対象ファイル |
|-----------|---------|------------|
| 論文掲載・発表後 | 新しい業績を追加 | `data/publications.yml` |
| 学期開始時 | 担当講義を追加 | `data/teaching.yml` |
| 異動・昇任時 | 職位・所属・経歴を更新 | `data/profile.yml`, `data/career.yml` |
| 研究テーマ変更時 | 研究内容の説明を更新 | `data/research.yml` |
| 連絡先変更時 | メール・リンクを更新 | `data/profile.yml` |
| 写真変更時 | プロフィール写真を差し替え | `static/images/avatar.jpg` |

---

*このマニュアルは `/MAINTENANCE.md` に保存されています。*
