# ウェブサイト メンテナンスマニュアル

**対象サイト**: 個人学術ウェブサイト (Hugo + Tailwind CSS)
**リポジトリ**: https://github.com/kkaneta/kkaneta.github.io
**公開URL**: https://kkaneta.github.io/
**最終更新**: 2026-09-07

---

## この文書の読み方

このサイトは**無人で動くように作られています**。論文一覧は毎週自動で更新され、公開まで自動で進みます。手作業が必要なのは、年に1回程度の担当講義の追加と、職位や連絡先が変わったときだけです。

そのため「久しぶりに開いたら書き方を忘れている」ことが前提になっています。**書き方を間違えるとビルドが止まり、何をどう直せばよいかがエラーメッセージに出ます。** このマニュアルを開かなくても直せるように作ってありますが、全体像を把握したいときはここを読んでください。

**重要な原則: 間違えても公開サイトは壊れません。** 検証で止まった場合、公開中のサイトは直前の正常な状態のまま残ります。

---

## 目次

1. [概要と技術スタック](#1-概要と技術スタック)
2. [環境セットアップ](#2-環境セットアップ)
3. [ディレクトリ構造](#3-ディレクトリ構造)
4. [ローカル開発サーバーの起動](#4-ローカル開発サーバーの起動)
5. [コンテンツの更新方法](#5-コンテンツの更新方法)
   - [5.1 プロフィール・基本情報](#51-プロフィール基本情報)
   - [5.2 経歴](#52-経歴)
   - [5.3 研究業績（論文）— 全自動](#53-研究業績論文-全自動)
   - [5.4 研究内容](#54-研究内容)
   - [5.5 担当講義 — 年1回の作業](#55-担当講義-年1回の作業)
6. [ページ本文の編集](#6-ページ本文の編集)
7. [画像の更新](#7-画像の更新)
8. [自動化の仕組み](#8-自動化の仕組み)
9. [別PCへの移行手順](#9-別pcへの移行手順)
10. [トラブルシューティング](#10-トラブルシューティング)
11. [既知の未対応事項](#11-既知の未対応事項)
12. [メンテナンス頻度チェックリスト](#12-メンテナンス頻度チェックリスト)

---

## 1. 概要と技術スタック

| 技術 | 役割 | バージョン |
|------|------|-----------|
| [Hugo](https://gohugo.io/) | 静的サイトジェネレーター | 0.156.0 (Extended 必須) |
| [Tailwind CSS](https://tailwindcss.com/) | CSSフレームワーク | v4 |
| Node.js / npm | Tailwind のビルド用 | 任意の LTS 版 |
| Python | 論文同期とデータ検証（CI で実行） | 3.12 |
| GitHub Actions | 自動ビルド・デプロイ・論文同期 | - |
| GitHub Pages | ホスティング | - |

**コンテンツ更新の基本原則**: すべての更新は `data/` フォルダ内の YAML ファイルを編集して git push するだけで完結します。HTML や Hugo のテンプレートを触る必要はありません。

---

## 2. 環境セットアップ

**ローカル環境は必須ではありません。** GitHub の Web エディタから YAML を直接編集しても、検証とデプロイは自動で走ります。スマートフォンからでも作業できます。

見た目を確認しながら編集したい場合のみ、以下を用意します。

```bash
brew install hugo    # Extended 版が必要（hugo version に "extended" と出ること）
brew install node
```

初回セットアップ:

```bash
git clone https://github.com/kkaneta/kkaneta.github.io.git
cd kkaneta.github.io
npm install
```

> `node_modules/` はPC環境固有のファイルを含むため、別のPCに持ち込んでも使えません。詳細は [9章](#9-別pcへの移行手順)。

---

## 3. ディレクトリ構造

```
kkaneta.github.io/
├── .github/workflows/
│   ├── deploy.yml                 ビルドして GitHub Pages へ公開
│   └── sync-publications.yml      週次で論文一覧を同期し、そのまま公開
│
├── scripts/
│   ├── sync_publications.py       INSPIRE-HEP から publications.yml を生成
│   └── check_data.py              data/ の書式をビルド前に検証
│
├── data/                   ★ ここを編集する
│   ├── profile.yml         → 氏名・職位・所属・連絡先・各種リンク
│   ├── career.yml          → 経歴
│   ├── publications.yml    → 研究業績（自動生成。原則として手で触らない）
│   ├── publications_exclude.yml → 一覧に載せない論文の指定
│   ├── research.yml        → 研究内容
│   └── teaching.yml        → 担当講義
│
├── content/                補足的な本文テキスト（あまり触らない）
├── static/images/          画像ファイル
├── assets/css/main.css     デザイン設定（触ることはほぼない）
├── layouts/                HTML テンプレート（触ることはほぼない）
├── hugo.toml               サイト全体の設定（ほぼ触らない）
├── MAINTENANCE.md          このファイル
│
├── archive/                役目を終えたツール（git 管理外）
├── site_spec_v2.md         作業メモ（git 管理外）
└── public/                 ビルド結果（自動生成・git 管理外）
```

---

## 4. ローカル開発サーバーの起動

```bash
hugo server -D
```

`http://localhost:1313/` で確認できます。停止は `Ctrl + C`。

> ローカルでは `scripts/check_data.py` は自動実行されません。書式の検証は push 後に GitHub Actions が行います。手元で確認したい場合は [10章](#10-トラブルシューティング) を参照してください。

---

## 5. コンテンツの更新方法

### 5.1 プロフィール・基本情報

**ファイル**: `data/profile.yml` — **プロフィール系の情報はすべてこのファイルにあります。**

> **重要**: `hugo.toml` にプロフィール情報を書いてもサイトには反映されません。以前は `hugo.toml` にもメールアドレスや GitHub の URL がありましたが、テンプレートが読んでいたのは `profile.yml` だけでした。現在は重複を削除してあります。

```yaml
name:
  ja: "金田 邦雄"
  en: "Kunio Kaneta"

position:
  ja: "助教"
  en: "Assistant Professor"

institution:
  ja: "新潟大学 教育学部"
  en: "Faculty of Education, Niigata University"

email: "kaneta[at]ed.niigata-u.ac.jp"

links:
  github: ""                                          # 空欄ならリンクは表示されない
  google_scholar: ""
  orcid: "https://orcid.org/0000-0001-5391-2204"      # フルURLで書く
  INSPIRE-HEP: "https://inspirehep.net/authors/1078184"

bio:
  ja: |
    理論物理学（素粒子論・宇宙論）を専門とする研究者です。
  en: |
    I am a researcher specializing in theoretical physics.

avatar: "/images/avatar.jpg"                          # 先頭に "/" をつける
```

**メールアドレスについて**: 収集ボット対策のため `[at]` 表記で書いています。サイト上ではこの文字列がそのまま**テキストとして**表示され、クリックできるリンクにはなりません（`mailto:` リンクにすると不正なアドレスでメーラーが開いてしまうため）。

**表示されるリンク**: `github` / `google_scholar` / `orcid` / `INSPIRE-HEP` の4つです。値が空欄のものはリンク自体が表示されません。`researchgate` の項目は**どのテンプレートからも参照されていません**ので、書いても表示されません。

---

### 5.2 経歴

**ファイル**: `data/career.yml` — 新しい職歴を**先頭に追加**します（上から順に表示）。

```yaml
- year: 2024--          # 現在進行中は "--" で終える。期間は "2021--2023"、単年は "2013"
  title:
    ja: "新潟大学 教育学部 助教"
    en: "Assistant Professor, Faculty of Education, Niigata University"
```

---

### 5.3 研究業績（論文）— 全自動

**手作業は不要です。何もしなくても公開されます。**

#### 仕組み

`.github/workflows/sync-publications.yml` が**毎週月曜 9:00 (JST)** に `scripts/sync_publications.py` を実行し、INSPIRE-HEP の著者レコード（BAI: `K.Kaneta.1`）から `data/publications.yml` を再生成します。差分があれば **`main` に直接コミットし、そのままサイトを更新します。**

INSPIRE は次の2つを両方追跡するため、これだけで一覧は最新に保たれます。

| 出来事 | 反映される内容 |
|---|---|
| arXiv にプレプリント公開 | 新しい論文が一覧に追加される |
| 雑誌に掲載 | 雑誌名・巻・号・ページ・DOI が埋まる |

> **なぜレビュー工程がないのか**: PRを作る方式にしていた時期がありますが、マージするまで公開されないため、年に数回しかサイトを見ない運用では一覧が古いまま放置されます。代わりに「**結果がおかしければ公開せずに止まる**」という守り方をしています（次項）。

#### 安全装置

`scripts/sync_publications.py` は、次のいずれかに当てはまると**ファイルを書かずに異常終了**します。ワークフローが失敗し、GitHub から失敗通知のメールが届きます。**公開中のサイトはそのまま残ります。**

| 検出内容 | 想定される原因 |
|---|---|
| 件数が既存ファイルの90%未満 | INSPIRE の著者識別子やAPIが変わり、検索が一致しなくなった |
| `JOURNAL_MAP` にない雑誌略称 | 新しい雑誌に掲載された |
| 著者名またはタイトルが空 | INSPIRE のレコードが不完全 |

対処方法はエラーメッセージ自体に書かれています。

#### 意図的に論文を減らす場合

複数の論文をまとめて除外して件数が大きく減るときは、件数の安全装置に引っかかります。その場合はローカルで次を実行してください。

```bash
python3 scripts/sync_publications.py --allow-shrink
```

#### 載せたくない論文がある場合

`data/publications_exclude.yml` に INSPIRE の texkey を追加します。

```yaml
- Okamoto:2007zz   # 理由をコメントに書いておく
```

なお**国際会議録と博士論文は自動的に除外**されます（雑誌論文のみを掲載）。

#### タイトルを直したい場合

`data/publications.yml` の `title:` だけは例外で、**手で書き換えた内容が次回以降の同期でも保持されます**。INSPIRE 側の大文字小文字が不揃いなためです。

それ以外の項目（雑誌名・巻・号・ページ・DOI・年）は毎回上書きされます。**直すべき場所は INSPIRE です。**

#### すぐに反映したいとき

GitHub の **Actions タブ → Sync publications from INSPIRE-HEP → Run workflow**

手元で実行する場合:

```bash
python3 scripts/sync_publications.py           # ファイルを更新
python3 scripts/sync_publications.py --check   # 差分の有無だけ確認
python3 scripts/sync_publications.py --stdout  # 結果を表示するだけ
```

#### 新しい雑誌に掲載されたとき

同期が「未知の雑誌略称です」で止まった場合、`scripts/sync_publications.py` の `JOURNAL_MAP` に1行追加します。追加すべき行はエラーメッセージにそのまま出ます。

```python
JOURNAL_MAP = {
    "Phys.Rev.D": "Physical Review D",
    "SciPost Phys.": "SciPost Physics",   # ← このような行を追加
}
```

---

### 5.4 研究内容

**ファイル**: `data/research.yml` — 研究テーマごとに1エントリ。

```yaml
- id: "dark-matter"
  title:
    ja: "暗黒物質の研究"
    en: "Dark Matter Research"
  description:
    ja: |
      暗黒物質の性質に関する理論的研究を行っています。
    en: |
      We conduct theoretical research on the properties of dark matter.
  equation: "\\Omega_{\\rm DM} h^2 \\propto m_{\\rm DM}"   # 任意
  keywords:
    - "Dark Matter"
```

`equation:` を書くと数式が表示されます。YAML 内でバックスラッシュは `\\` と二重にします（`\mu` → `\\mu`）。

> **注意**: エントリ内に `math: true` と書いても効果はありません。数式ライブラリ（KaTeX）の読み込みは `content/research/_index.md` のフロントマターにある `math: true` が制御しています。研究ページには既に設定済みなので、通常は何もする必要がありません。

---

### 5.5 担当講義 — 年1回の作業

**ファイル**: `data/teaching.yml`

**このサイトで唯一、定期的に手を入れる場所です。**

#### 毎年の更新（通常はこれだけ）

科目ごとの `years:` に新しい年度を足すだけです。**シラバスURLは年度と科目コードから自動生成される**ので、コピペは不要です。

```yaml
- code: "0K6140"
  dept: "03"
  years: [2024, 2025, 2026, 2027]    # ← 2027 を足すだけ
```

#### 科目を新しく追加する場合

既存のブロックを1つコピーして書き換えます。

```yaml
- code: "0K6140"                   # シラバスの科目番号から先頭2桁（年度）を除いた部分
  dept: "03"                       # シラバスURLに現れる学部コード（2桁、引用符で囲む）
  years: [2026]
  semester: { ja: "通年", en: "All Year" }
  level:    { ja: "学部4年", en: "Undergraduate (4th year)" }
  title:
    ja: "卒業研究"
    en: "Graduation Thesis"        # 省略すると日本語ページにのみ表示される
```

**`code` の求め方**: 2026年度のシラバス番号が `260K6140` なら、先頭の `26`（年度の下2桁）を除いた `0K6140` が `code` です。

**`dept` の求め方**: シラバスURL `.../syllabusHtml/2026/03/03_260K6140_ja_JP.html` の `03` の部分です。**必ず引用符で囲んでください**（囲まないと `3` と解釈され、検証で止まります）。

#### 科目名や開講期が変わった場合

エントリを2つに分け、`years:` を振り分けます。

```yaml
- code: "0K5805"
  dept: "03"
  years: [2024, 2025, 2026]
  semester: { ja: "前期", en: "Spring" }
  level:    { ja: "学部3〜6年", en: "Undergraduate (3rd-6th year)" }
  title:
    ja: "物理学セミナー"
    en: "Physics Seminar"

- code: "0K5805"                   # 同じ科目コードでよい
  dept: "03"
  years: [2027]                    # 年度が重複しないように分ける
  semester: { ja: "後期", en: "Fall" }
  level:    { ja: "学部3〜6年", en: "Undergraduate (3rd-6th year)" }
  title:
    ja: "物理学セミナー"
    en: "Physics Seminar"
```

同じ科目コードと年度の組み合わせが2箇所に現れると、検証で止まります。

#### シラバスのURLが変わった場合

大学がURLの方式を変更すると、自動生成されたリンクが切れます。その場合はエントリに `url:` を追加してください。**自動生成より優先されます。**

```yaml
- code: "0K6140"
  dept: "03"
  years: [2027]
  url: "https://（正しいURLをそのまま貼る）"
```

複数の科目で同時に起きた場合は、テンプレート `layouts/teaching/list.html` の生成規則を直すほうが早い場合もあります。

#### シラバスの中身が変わった場合

**何もする必要はありません。** サイトが持っているのは科目名・対象学年・開講期とリンクだけで、授業計画や成績評価の方法はシラバス側にあります。年度ごとのURLがその年度のシラバスを指すため、自動的に最新の内容が表示されます。

---

## 6. ページ本文の編集

`data/` に収まらない追記テキストは `content/` の Markdown に書きます。

| ページ | 日本語 | 英語 |
|--------|--------|------|
| トップ | `content/_index.md` | `content/en/_index.md` |
| 研究 | `content/research/_index.md` | `content/en/research/_index.md` |
| 業績 | `content/publications/_index.md` | `content/en/publications/_index.md` |
| 担当講義 | `content/teaching/_index.md` | `content/en/teaching/_index.md` |

---

## 7. 画像の更新

### プロフィール写真

`static/images/avatar.jpg` を上書きします（256×256px 以上の正方形推奨）。ファイル名を変える場合は `data/profile.yml` の `avatar:` も変更します。

### SNSシェア用画像（OGP画像）

`static/images/og-default.png` を置きます（1200×630px 推奨）。**現在このファイルは存在せず、SNSでシェアしても画像が表示されません**（[11章](#11-既知の未対応事項)）。

---

## 8. 自動化の仕組み

### ワークフローは2つ

**`.github/workflows/deploy.yml`** — サイトのビルドと公開

起動条件は3つです。

1. `main` への push
2. Actions タブからの手動実行
3. `sync-publications.yml` からの呼び出し

処理の順序:

1. Hugo 0.156.0 (extended) をインストール
2. **`scripts/check_data.py` で `data/` の書式を検証** ← ここで止まればサイトは更新されない
3. `npm ci` で Tailwind をインストール
4. `hugo --minify` でビルド
5. GitHub Pages へデプロイ

**`.github/workflows/sync-publications.yml`** — 論文一覧の同期

毎週月曜 9:00 (JST) と、手動実行で起動します。

1. `scripts/sync_publications.py` を実行（安全装置つき）
2. 差分があれば `main` にコミットして push
3. 差分があれば `deploy.yml` を呼び出してサイトを更新

> **なぜ手順3が必要なのか**: GitHub には「Actions が自分で行った push は別のワークフローを起動しない」という仕様（無限ループ防止）があります。そのため放置すると `publications.yml` だけが更新され、公開ページは古いままになります。同期側から明示的にデプロイを呼ぶことで防いでいます。

### 通常の更新フロー

VS Code から:

1. ファイルを編集・保存
2. Source Control アイコン → 「+」でステージング
3. コミットメッセージを入力して **Commit**
4. **Sync Changes**（または Push）

ターミナルから:

```bash
git add .
git commit -m "更新内容の説明"
git push origin main
```

push すると自動でビルドが走り、2〜3分で反映されます。GitHub の **Actions タブ**で進行状況を確認できます。

### GitHub Pages の設定（初回のみ）

**Settings → Pages → Source** を **GitHub Actions** に設定します。

> **注意**: `.github/workflows/` 配下のファイルは、認証トークンに `workflow` スコープが無いとコマンドラインから push できません（`refusing to allow an OAuth App to create or update workflow` というエラー）。その場合は GitHub の Web エディタから編集してください。

---

## 9. 別PCへの移行手順

`node_modules/` には OS 固有のバイナリが含まれます。別のPCに持ち込んでもそのままでは動きません。

```bash
git clone https://github.com/kkaneta/kkaneta.github.io.git
cd kkaneta.github.io
npm install
hugo server -D
```

**同期・コピーしてはいけないもの**: `node_modules/`、`public/`（どちらも `.gitignore` 済み）

### QNAP 同期を使っている場合

`node_modules/` を同期対象から**除外してください**。除外していないと、同期の過程でファイルが欠落し、ビルドが失敗します（[10章](#10-トラブルシューティング)）。

```bash
rsync -av --exclude='node_modules/' --exclude='public/' ./kkaneta.github.io/ user@qnap:/path/to/backup/
```

### git の著者情報

新しいPCでは最初に設定してください。設定しないとホスト名由来のアドレスが使われ、GitHub アカウントに紐づきません。

```bash
git config --global user.name  "kkaneta"
git config --global user.email "67679029+kkaneta@users.noreply.github.com"
```

---

## 10. トラブルシューティング

### GitHub Actions が失敗した（メールが届いた）

**まず Actions タブでどちらのワークフローが失敗したかを確認します。**

#### 「Deploy Hugo site to GitHub Pages」の `Check data/` で失敗

`data/` の書式に問題があります。**公開サイトは直前の状態のまま**なので、慌てる必要はありません。ログに次のような形で、ファイル名・エントリ・直し方が出ます。

```
data/ has problems the site would render as blank spaces:
  - teaching.yml course 1 (0K6140): dept is 3, but it must be the two-digit
      faculty code that appears in the syllabus URL, quoted (e.g. "03").
```

指示どおりに直して push すれば復旧します。手元で確認する場合:

```bash
pip install pyyaml          # 初回のみ
python3 scripts/check_data.py
```

#### 「Sync publications from INSPIRE-HEP」で失敗

安全装置が働いた可能性が高いです。ログのメッセージを読んでください（[5.3節](#53-研究業績論文-全自動)）。

| メッセージの要点 | 対処 |
|---|---|
| `INSPIRE returned N publications, replacing a file that holds M` | INSPIRE 側を確認。正しければ `--allow-shrink` で手動実行 |
| `unknown journal abbreviation` | `JOURNAL_MAP` に1行追加 |
| `INSPIRE returned no author list` | INSPIRE のレコードを修正 |

**公開中の論文一覧は失敗しても消えません。** 同期が成功するまで前回の内容が残ります。

### ローカルでのエラー

#### `tailwindcss: Permission denied`
#### `No prebuild or local build of @parcel/watcher found`
#### `Cannot find module './AsyncParallelBailHook'`

**原因**: 別OSで作られた `node_modules/` を持ち込んだ、または QNAPsync による同期でファイルが欠落した。

**対処**:

```bash
npm ci
```

> **重要**: `npm install` ではなく **`npm ci`** を使ってください。`npm install` は既存の `node_modules/` を信用するため、ファイルが欠落していても再展開しません。`npm ci` は削除してから `package-lock.json` どおりに再構築します。この症状は QNAPsync 環境で繰り返し発生しています。

#### `hugo: command not found`

```bash
brew install hugo
```

#### `requires Hugo Extended`

```bash
brew uninstall hugo && brew install hugo
hugo version   # "extended" と表示されることを確認
```

### YAML のシンタックスエラー

```yaml
# NG: インデントがずれている        # NG: コロンの後にスペースがない
- id: "example"                     title:"タイトル"
title: "タイトル"

# OK                                # OK
- id: "example"                     title: "タイトル"
  title: "タイトル"
```

### GitHub Pages に反映されない

**Settings → Pages → Source** が **GitHub Actions** になっているか確認してください。

### `hugo.toml` を編集したのに反映されない

**設定を書く位置に注意してください。** TOML では `[build]` のようなテーブル見出しより後に書いた設定は、そのテーブルの中の設定として解釈されます。サイト全体の設定（`disableKinds` など）は**必ず最初のテーブル見出しより前**に書いてください。位置を間違えても**警告は出ず、黙って無視されます**。

また、プロフィール情報は `hugo.toml` ではなく `data/profile.yml` にあります（[5.1節](#51-プロフィール基本情報)）。

---

## 11. 既知の未対応事項

急を要さないため対応を見送っている項目です。

| 項目 | 内容 |
|---|---|
| OGP画像 | `static/images/og-default.png` が存在せず、SNSシェア時に画像が出ない（1200×630px の画像を置けば解決） |
| favicon | `static/favicon.ico` が存在せず、全ページで404リクエストが発生している |
| 画像サイズ | `avatar.jpg` が 846×814px / 80KB。表示は128×128pxなので過大 |
| フォント | Google Fonts を3ファミリー読み込んでいる（JetBrains Mono はほぼ使われていない） |
| 併合科目 | 宇宙素粒子物理学概論は 2026年度から `260Y3106` でも履修登録できるが、そちらのシラバスURLは公開されていないためリンクしていない |

---

## 12. メンテナンス頻度チェックリスト

| タイミング | 作業内容 | 対象ファイル |
|-----------|---------|------------|
| 論文掲載・発表後 | **不要**（毎週月曜に自動で公開される） | — |
| 年度開始時 | `years:` に年度を追加 | `data/teaching.yml` |
| 新しい科目の担当時 | 科目ブロックを追加 | `data/teaching.yml` |
| 異動・昇任時 | 職位・所属・経歴を更新 | `data/profile.yml`, `data/career.yml` |
| 研究テーマ変更時 | 研究内容を更新 | `data/research.yml` |
| 連絡先変更時 | メール・リンクを更新 | `data/profile.yml` |
| 写真変更時 | 写真を差し替え | `static/images/avatar.jpg` |
| 新しい雑誌に掲載時 | 同期が止まったら1行追加 | `scripts/sync_publications.py` |
