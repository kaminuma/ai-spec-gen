#!/usr/bin/env python3
"""
AI Spec Generator - メインエントリーポイント

使い方:
    # ディレクトリ全体を解析
    python main.py --dir ./server --output markdown

    # 特定のファイルのみ解析
    python main.py --file ./server/app/Models/User.php --output markdown
"""

import argparse
import sys
from pathlib import Path
import os


def main():
    parser = argparse.ArgumentParser(
        description='AIを使ってプロジェクトの仕様書を自動生成'
    )

    # 入力オプション
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--dir',
        type=str,
        help='解析対象のディレクトリパス'
    )
    input_group.add_argument(
        '--file',
        type=str,
        help='解析対象のファイルパス (複数指定可)',
        nargs='+'
    )

    # プラグイン指定
    parser.add_argument(
        '--plugin',
        type=str,
        default='laravel',
        choices=['laravel', 'python', 'java'],
        help='使用するプラグイン (デフォルト: laravel)'
    )

    # AIバックエンド指定
    parser.add_argument(
        '--ai-backend',
        type=str,
        default=None,
        choices=['claude', 'claude-code', 'gemini'],
        help='使用するAIバックエンド (デフォルト: claude-code、環境変数AI_BACKENDでも設定可)'
    )

    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='AI補完を使用せず、正規表現抽出のみで仕様書生成'
    )

    # 出力オプション
    parser.add_argument(
        '--output',
        type=str,
        default='markdown',
        choices=['markdown', 'markdown-multi', 'json', 'notion', 'notion-hier'],
        help='出力形式 (デフォルト: markdown, markdown-multi で複数MD出力, notion-hier でNotion階層出力)'
    )

    parser.add_argument(
        '--output-file',
        type=str,
        default='./outputs/spec.md',
        help='出力ファイルパス (デフォルト: ./outputs/spec.md)'
    )

    # Notion オプション
    parser.add_argument(
        '--notion-token',
        type=str,
        help='Notion APIトークン (--output notion の場合に必要)'
    )

    parser.add_argument(
        '--notion-page-id',
        type=str,
        help='Notion親ページID'
    )

    parser.add_argument(
        '--notion-flat',
        action='store_true',
        help='Notion階層出力時に中間ページを作らず、親ページ直下に各パートを作成する'
    )

    # その他
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='詳細ログを表示'
    )

    args = parser.parse_args()

    # バリデーション
    if args.output == 'notion':
        if not (args.notion_token or os.getenv('NOTION_TOKEN') or os.getenv('NOTION_API_KEY')):
            parser.error('--output notion を指定する場合は --notion-token または環境変数 NOTION_TOKEN/NOTION_API_KEY が必要です')
        if not (args.notion_page_id or os.getenv('NOTION_PARENT_PAGE_ID') or os.getenv('NOTION_PAGE_ID')):
            parser.error('--output notion を指定する場合は --notion-page-id または環境変数 NOTION_PARENT_PAGE_ID/NOTION_PAGE_ID が必要です')

    # ディレクトリ/ファイルの存在確認
    if args.dir:
        target_path = Path(args.dir)
        if not target_path.exists():
            print(f'エラー: ディレクトリが存在しません: {args.dir}', file=sys.stderr)
            sys.exit(1)
        if not target_path.is_dir():
            print(f'エラー: 指定されたパスはディレクトリではありません: {args.dir}', file=sys.stderr)
            sys.exit(1)

    if args.file:
        for file_path in args.file:
            if not Path(file_path).exists():
                print(f'エラー: ファイルが存在しません: {file_path}', file=sys.stderr)
                sys.exit(1)

    # 実行
    print(f'🚀 AI Spec Generator 開始')
    print(f'  プラグイン: {args.plugin}')
    print(f'  出力形式: {args.output}')

    if args.dir:
        print(f'  対象ディレクトリ: {args.dir}')
    else:
        print(f'  対象ファイル: {", ".join(args.file)}')

    # プラグイン読み込みと実行
    try:
        if args.plugin == 'laravel':
            from plugins.laravel.parser import LaravelParser
            from core.markdown_generator import MarkdownGenerator

            # パーサー初期化
            if args.dir:
                parser = LaravelParser(args.dir)
                print('\n🔍 プロジェクト全体を解析中...')
                data = parser.parse_all()
            else:
                # 最初のファイルからプロジェクトルートを推測
                first_file = Path(args.file[0])
                project_root = first_file.parent
                while project_root.parent != project_root:
                    if (project_root / 'composer.json').exists():
                        break
                    project_root = project_root.parent

                parser = LaravelParser(project_root)
                print(f'\n🔍 指定されたファイルを解析中...')
                data = parser.parse_files(args.file)

            # 統計表示
            print(f'\n📊 解析結果:')
            print(f'  - Models: {len(data.get("models", []))}個')
            print(f'  - Controllers: {len(data.get("controllers", []))}個')
            print(f'  - Routes: {sum(len(routes) for routes in data.get("routes", {}).values())}個')
            print(f'  - Migrations: {len(data.get("migrations", []))}個')
            print(f'  - Services: {len(data.get("services", []))}個')
            print(f'  - Middleware: {len(data.get("middleware", []))}個')
            print(f'  - Requests: {len(data.get("requests", []))}個')
            print(f'  - Policies: {len(data.get("policies", []))}個')
            print(f'  - Jobs: {len(data.get("jobs", []))}個')
            print(f'  - Events: {len(data.get("events", []))}個')
            print(f'  - Listeners: {len(data.get("listeners", []))}個')
            print(f'  - GraphQL Schemas: {len(data.get("graphql_schemas", {}))}個')
            print(f'  - GraphQL Queries: {len(data.get("graphql_resolvers", {}).get("queries", []))}個')
            print(f'  - GraphQL Mutations: {len(data.get("graphql_resolvers", {}).get("mutations", []))}個')

            # AI補完（オプション）
            ai_descriptions = {}
            if not args.no_ai:
                from core.ai_backend import get_ai_backend
                from core.prompt_templates import (
                    generate_model_prompt,
                    generate_controller_prompt,
                    generate_service_prompt,
                    generate_project_summary_prompt
                )

                print(f'\n🤖 AIで説明を補完中（Few-Shot学習使用）...')
                backend_name = args.ai_backend or 'claude-code'
                print(f'   使用するAI: {backend_name}')

                try:
                    ai = get_ai_backend(backend_name)

                    # プロジェクト全体のサマリー生成
                    print(f'   📋 プロジェクト概要を生成中...')
                    try:
                        summary_prompt = generate_project_summary_prompt(data)
                        ai_descriptions['project_summary'] = ai.generate(summary_prompt).strip()
                        print(f'   ✓ プロジェクト概要')
                    except Exception as e:
                        print(f'   ✗ プロジェクト概要: {e}')

                    # Modelsの説明を生成
                    print(f'   📦 Models説明を生成中...')
                    for model in data.get('models', []):
                        class_name = model['class_name']
                        try:
                            prompt = generate_model_prompt(model)
                            ai_descriptions[f'model_{class_name}'] = ai.generate(prompt).strip()
                            print(f'   ✓ Model: {class_name}')
                        except Exception as e:
                            print(f'   ✗ Model {class_name}: {e}')

                    # Controllersの説明を生成
                    print(f'   🎮 Controllers説明を生成中...')
                    for controller in data.get('controllers', []):
                        class_name = controller['class_name']
                        if not controller.get('methods'):
                            continue
                        try:
                            prompt = generate_controller_prompt(controller)
                            ai_descriptions[f'controller_{class_name}'] = ai.generate(prompt).strip()
                            print(f'   ✓ Controller: {class_name}')
                        except Exception as e:
                            print(f'   ✗ Controller {class_name}: {e}')

                    # Servicesの説明を生成
                    print(f'   ⚙️  Services説明を生成中...')
                    for service in data.get('services', []):
                        class_name = service['class_name']
                        try:
                            prompt = generate_service_prompt(service)
                            ai_descriptions[f'service_{class_name}'] = ai.generate(prompt).strip()
                            print(f'   ✓ Service: {class_name}')
                        except Exception as e:
                            print(f'   ✗ Service {class_name}: {e}')

                    print(f'\n   ✅ 完了: {len(ai_descriptions)}個の説明を生成')

                except Exception as e:
                    print(f'   ⚠️  AI補完をスキップ: {e}')

            # Markdown生成（Notion出力時もMarkdownを生成してアップロードする）
            if args.output in ['markdown', 'markdown-multi', 'notion', 'notion-hier']:
                print(f'\n📝 Markdownを生成中...')
                generator = MarkdownGenerator()
                markdown = generator.generate(data, ai_descriptions)

                # 出力ディレクトリ作成
                output_path = Path(args.output_file)
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if args.output == 'markdown':
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown)
                    print(f'✅ 仕様書を生成しました: {output_path}')
                    print(f'   サイズ: {len(markdown)} 文字')

                elif args.output == 'markdown-multi':
                    parts = generator.generate_parts(data, ai_descriptions)
                    for name, content in parts.items():
                        part_path = output_path.parent / f"{output_path.stem}_{name}.md"
                        with open(part_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f'✅ {name} を出力: {part_path} ({len(content)} 文字)')

                elif args.output in ['notion', 'notion-hier']:
                    # まずローカル保存（単一/複数でもデバッグ用に残す）
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(markdown)
                    print(f'✅ 仕様書を生成しました: {output_path}')
                    print(f'   サイズ: {len(markdown)} 文字')

                    from core.notion_exporter import NotionExporter, get_notion_credentials

                    print('\n🌐 Notionへアップロード中...')
                    token, parent_page_id = get_notion_credentials(args.notion_token, args.notion_page_id)

                    try:
                        exporter = NotionExporter(token)
                        if args.output == 'notion':
                            page_url = exporter.upload_markdown(markdown, parent_page_id, title=output_path.stem or 'AI Spec')
                            print(f'✅ Notion にアップロードしました: {page_url}')
                        else:
                            # 階層モード: 複数パートをアップロード
                            parts = generator.generate_parts(data, ai_descriptions)
                            if args.notion_flat:
                                emoji_map = {
                                    'overview': '🗂️',
                                    'db': '🗄️',
                                    'api': '🔗',
                                    'security': '🔒',
                                    'graphql': '🔮',
                                }
                                title_map = {
                                    'overview': '概要',
                                    'db': 'DB仕様',
                                    'api': 'API仕様',
                                    'security': 'セキュリティ',
                                    'graphql': 'GraphQL仕様',
                                }
                                urls = exporter.upload_hierarchy_flat(parts, parent_page_id, emoji_map=emoji_map, title_map=title_map)
                                for k, v in urls.items():
                                    print(f'   - {k}: {v}')
                            else:
                                root_title = output_path.stem or 'AI Spec'
                                root_url = exporter.upload_hierarchy(parts, parent_page_id, root_title)
                                print(f'✅ Notion 階層にアップロードしました: {root_url}')
                    except Exception as e:
                        print(f'❌ Notion へのアップロードに失敗しました: {e}')

            else:
                print(f'\n⚠️  {args.output} 出力は未実装です')

        else:
            print(f'\n⚠️  {args.plugin} プラグインは未実装です')

    except Exception as e:
        print(f'\n❌ エラーが発生しました: {e}')
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

    print('\n🎉 完了！')
    return 0


if __name__ == '__main__':
    sys.exit(main())
