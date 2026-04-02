# 研究者ウェブサイト構築仕様書（Hugo + YAML管理）
**Version 2.0（改訂版）**

---

## 1. プロジェクト概要

- **目的**: 研究実績、研究内容、担当講義等の情報を、日本語・英語の両方で効率的に公開・管理する。

### 設計思想

- **低メンテナンスコスト**: 特定のAIツールに依存せず、YAMLファイルの編集のみで更新を完結させる。
- **一元管理**: 1つのデータファイル内で日本語と英語を併記し、情報の乖離を防ぐ。
- **柔軟な言語制御**: 授業情報など、日本語のみのコンテンツにも自然に対応できるデザイン。

---

## 2. 技術スタック

- **フレームワーク**: Hugo (Static Site Generator)
- **スタイリング**: Tailwind CSS（または Hugo の軽量テーマ）
- **数式レンダリング**: KaTeX — Markdown 内で `$...$` および `$$...$$` を使用可能にする。ページ単位で `math: true` を frontmatter で明示的に有効化する。
- **デプロイ**: GitHub Pages（推奨）または Cloudflare Pages（ビルド速度・キャッシュ制御で優位）。

---

## 3. ディレクトリ構成とデータ構造

日々の更新は `data/` フォルダ内の YAML ファイルを編集する運用とします。

### 3.1 データ管理（`data/` ディレクトリ）

- **`profile.yml`**: 氏名、所属、SNSリンク等の基本情報。
- **`career.yml`**: 略歴・職歴（`profile.yml` から分離し、ネストの深さを抑える）。
- **`research.yml`**: 研究テーマの解説、最新のトピックス。
- **`teaching.yml`**: 担当授業リスト。
- **`publications.yml`**: 論文情報（マスターデータ）。

### 3.2 `publications.yml` をマスターデータとする設計

論文情報は BibTeX ではなく `publications.yml` を唯一のマスターとします。これにより、更新フローが「YAMLを編集して `git push`」のみで完結します。

**初回移行手順:**

1. 既存の `.bib` ファイルから Python スクリプト（20行程度）で `publications.yml` を一括生成する。
2. 生成後は `publications.yml` のみを管理対象とする（`.bib` ファイルは参照不要）。
3. 以後の論文追加は `publications.yml` への直接追記で完結する。

### 3.3 YAML 記述例

#### `data/teaching.yml`

```yaml
- id: "phys2026"
  year: 2026
  title:
    ja: "基礎物理学実験"
    en: "Basic Physics Experiment"
  lang: ["ja"]   # ["ja"] のみ → 英語ページに表示しない
  url: "https://example.ac.jp/syllabus"
```

#### `data/publications.yml`

```yaml
- id: "yamada2024quantum"
  type: "article"
  year: 2024
  authors:
    - "Yamada, Kunio"
    - "Tanaka, Hiroshi"
  title: "Quantum entanglement in topological systems"
  journal: "Physical Review Letters"
  volume: 132
  pages: "051601"
  doi: "10.1103/PhysRevLett.132.051601"
```

#### `data/career.yml`

```yaml
- year: 2020
  title:
    ja: "新潟大学 准教授"
    en: "Associate Professor, Niigata University"
```

---

## 4. 各ページの仕様

### 4.1 Home / Profile

- プロフィール、所属、連絡先を表示。
- `profile.yml` および `career.yml` から日英それぞれの情報を取得。
- OGP・メタ情報（`<meta>` タグ）を各ページに設定し、SNS共有時の表示を最適化する。

### 4.2 Research

- 現在の研究プロジェクトの概要を表示。
- 数式（KaTeX）を多用しても崩れないレイアウト。
- frontmatter に `math: true` を設定したページのみ KaTeX を読み込む。

### 4.3 Publications

- `publications.yml` をマスターデータとして Hugo が直接読み込む。
- 著者名はリスト形式で管理し、自分の名前だけ太字にする制御をテンプレート側で実装。
- DOI リンクを自動生成する。

### 4.4 Teaching（多言語制御）

- `teaching.yml` を参照。
- **表示ロジック**:
  - 日本語ページ：全項目を表示。
  - 英語ページ：`lang` に `"en"` が含まれる項目のみを表示。
- ※ 英語ページで項目が少なくなった場合でも、不自然な空白ができないカード型デザインを採用。

---

## 5. 多言語・数式対応の設計

### 5.1 多言語切り替え

- Hugo の標準機能（`languages` 設定）を使用。
- URL 構造: `example.com/`（日本語）および `example.com/en/`（英語）。
- テンプレート側で、現在の言語に応じた YAML 項目（`.title.ja` または `.title.en`）を自動選択する。

### 5.2 言語フラグの設計（拡張版）

`is_ja_only` フラグ（二択）から `lang` リスト形式に変更し、将来の拡張に対応する。

```yaml
lang: ["ja"]         # 日本語のみ
lang: ["ja", "en"]   # 両言語（デフォルト）
lang: ["en"]         # 英語のみ（国際学会情報など）
```

### 5.3 数式表示（KaTeX）

- ブラウザでの閲覧時にレンダリングする設定（ビルド時ではない）。
- `$`（inline）と `$$`（block）の両方に対応し、理論物理学の複雑な数式も表示可能にする。
- 数式を使うページのみ frontmatter で `math: true` を指定し、不要な JS 読み込みを防ぐ。

### 5.4 OGP・メタ情報

- 各ページに `<title>`、`<meta name="description">`、OGP タグ（`og:title`, `og:description`）を設定。
- `profile.yml` の情報をベースに、Hugo テンプレートで自動生成する。
- Google Scholar や ResearchGate からのリンクに対して、適切なプレビューが表示される。

---

## 6. Claude Code への初期構築指示（プロンプト案）

サイト構築の際、以下の指示を Claude Code に与えて土台を作ります。

> Hugoを使用して多言語対応の研究者サイトを作成してください。
> 
> 1. data/*.yml に日本語と英語を併記する形式でコンテンツを管理したい
>    （profile, career, research, teaching, publications の5ファイル構成）。
> 2. teaching.yml の lang フィールドにリストで言語を指定し、英語ページでは
>    lang に "en" を含む項目のみ表示するロジックを組んでください。
> 3. KaTeXを導入し、frontmatterに math: true を指定したページのみ
>    数式が使えるように設定してください。
> 4. publications.yml から論文一覧ページを自動生成し、著者名リストを展開して
>    自分の名前（Kaneta, Kunio）を太字にするロジックを実装してください。
> 5. 各ページにOGPタグとメタ情報を出力するテンプレートを作成してください。
> 6. スタイリングはTailwind CSSを使用してください。
> 7. デプロイはGitHub Pagesを想定し、hugo.toml に baseURL と
>    GitHub Actions のワークフローファイルも作成してください。
> 8. 最後に hugo server でローカルプレビューできる状態にしてください。
---

## 7. 今後のメンテナンスサイクル

1. **通常更新**: `data/` 内の YAML を書き換えて `git push` する。
2. **論文追加**: `publications.yml` に追記して `git push` する（スクリプト不要）。
3. **略歴更新**: `career.yml` を編集して `git push` する。
4. **環境変更**: Hugo 本体と YAML データさえあれば、Claude Code がなくても恒久的に維持可能。

---

## 変更履歴

**Version 2.0** — 以下の点を初版から改訂：

1. **【文献管理】** `publications.yml` をマスターデータとする設計に変更（BibTeX 依存・変換スクリプト不要化）。
2. **【プロフィール】** `career.yml` を `profile.yml` から分離。
3. **【言語フラグ】** `is_ja_only` フラグを `lang` リスト形式に拡張。
4. **【数式】** KaTeX をページ単位で有効化する設計を追加。
5. **【デプロイ】** 選択肢に Cloudflare Pages を追記。
6. **【メタ情報】** OGP・メタ情報の仕様を追加。
