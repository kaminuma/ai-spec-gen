# AI Spec Generator

任意のプログラミングプロジェクトから仕様書を自動生成するCLIツール

## 🎯 特徴

- **言語非依存**: Laravel, Python, Java など様々なプロジェクトに対応
- **正規表現 + AI**: 構造は正規表現で確実に抽出、説明はAIで補完
- **柔軟な出力**: Markdown, JSON, Notion 形式で出力可能
- **ディレクトリ/ファイル指定**: プロジェクト全体または特定のファイルのみ解析可能

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
# またはCLI引数で指定
# python main.py --dir ./server --output notion --notion-token YOUR_TOKEN --notion-page-id YOUR_PAGE_ID
```

※ 親ページIDは、NotionのページURLに含まれる32桁のIDを使用します。

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
