# AI Spec Generator

任意のプログラミングプロジェクトから仕様書を自動生成するCLIツール

## 🎯 特徴

- **言語非依存**: Laravel, Python, Java など様々なプロジェクトに対応
- **正規表現 + AI**: 構造は正規表現で確実に抽出、説明はAIで補完
- **柔軟な出力**: Markdown, JSON, Notion 形式で出力可能
- **ディレクトリ/ファイル指定**: プロジェクト全体または特定のファイルのみ解析可能
- **Notion連携**: 親ページ直下に各仕様書をフラット配置（emoji＋日本語タイトル）する `--notion-flat` をサポート

## 📦 インストール

```bash
pip install -r requirements.txt
```

## 🚀 使い方

### ディレクトリ全体を解析
```bash
python main.py --dir ./server --output markdown
```

### 特定のファイルのみ解析
```bash
python main.py --file ./server/app/Models/User.php --output markdown
```

### Notion出力
```bash
export NOTION_TOKEN=your_token
export NOTION_PARENT_PAGE_ID=your_parent_page_id
python main.py --dir ./server --output notion
# 親ページ直下に各パートを並べて出力（emoji・日本語タイトル付き）
python main.py --dir ./server --output notion-hier --notion-flat
# またはCLI引数で指定
# python main.py --dir ./server --output notion --notion-token YOUR_TOKEN --notion-page-id YOUR_PAGE_ID
```

※ 親ページIDは、NotionのページURLに含まれる32桁のIDを使用します。

## ✅ 現行機能（Laravel）
- Models / Controllers（トレイト補完・validate/Validator検出）
- Routes（middleware・prefix対応、ミドルウェア併記）
- Migrations（PK・FK・Index 抽出）
- Services（メソッドシグネチャと振る舞い要約）
- GraphQL（エンドポイント `/graphql`、Query/Mutation 一覧）
- Kernel ミドルウェア一覧
- 出力: 分割Markdown（overview/db/api/security/graphql）、Notionフラット出力（emoji＋日本語タイトル）

## 🤖 AIバックエンド
- `--ai-backend gemini|claude|claude-code` で切替可。デフォルトは `.env` の `AI_BACKEND`（現状 gemini）。
- GeminiはモデルごとにRPM制限があります。429が出た場合は少し待つか、バックエンドを切り替えて再実行してください。

## 🔧 対応言語・フレームワーク

- ✅ Laravel (Phase 1)
- 🚧 Python/Django (計画中)
- 🚧 Java/Spring (計画中)

## 📚 ドキュメント

詳しい仕様は [docs/spec-generator-design.md](docs/spec-generator-design.md) を参照してください。

## 🛠️ 開発

```bash
# テスト実行
pytest tests/

# サンプルプロジェクトで試す
python main.py --dir ./examples/laravel-sample
```

## 📄 ライセンス

MIT
