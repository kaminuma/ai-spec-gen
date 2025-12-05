"""
Markdown Generator - 解析結果からMarkdownを生成
"""

from typing import Dict, Any, List


class MarkdownGenerator:
    """Markdown生成器"""

    def __init__(self):
        self.lines = []
        self.ai_descriptions = {}

    def generate(self, data: Dict[str, Any], ai_descriptions: Dict[str, str] = None) -> str:
        """
        解析データからMarkdownを生成

        Args:
            data: 解析結果のデータ
            ai_descriptions: AIが生成した説明文の辞書

        Returns:
            Markdown形式の文字列
        """
        self.lines = []
        self.ai_descriptions = ai_descriptions or {}

        # タイトル
        self.add_header("Laravel プロジェクト仕様書", level=1)
        self.add_line()

        # プロジェクト概要（AIが生成）
        if self.ai_descriptions.get('project_summary'):
            self.add_line(self.ai_descriptions['project_summary'])
            self.add_line()
            self.add_line("---")
            self.add_line()

        # Database Schema (Migrations)
        if data.get('migrations'):
            self._generate_migrations_section(data['migrations'])

        # Models
        if data.get('models'):
            self._generate_models_section(data['models'])

        # Controllers
        if data.get('controllers'):
            self._generate_controllers_section(data['controllers'])

        # Routes
        if data.get('routes'):
            self._generate_routes_section(data['routes'])

        # Services
        if data.get('services'):
            self._generate_services_section(data['services'])

        # Middleware
        if data.get('middleware'):
            self._generate_middleware_section(data['middleware'])

        # Form Requests (Validation)
        if data.get('requests'):
            self._generate_requests_section(data['requests'])

        # Policies
        if data.get('policies'):
            self._generate_policies_section(data['policies'])

        # Jobs
        if data.get('jobs'):
            self._generate_jobs_section(data['jobs'])

        # Events
        if data.get('events'):
            self._generate_events_section(data['events'])

        # Listeners
        if data.get('listeners'):
            self._generate_listeners_section(data['listeners'])

        # GraphQL Schemas
        if data.get('graphql_schemas'):
            self._generate_graphql_section(data['graphql_schemas'])

        # GraphQL Resolvers
        if data.get('graphql_resolvers'):
            self._generate_resolvers_section(data['graphql_resolvers'])

        return '\n'.join(self.lines)

    def generate_parts(self, data: Dict[str, Any], ai_descriptions: Dict[str, str] = None) -> Dict[str, str]:
        """
        複数Markdownパートを生成（Notion階層や分割出力用）
        Returns: {'overview': str, 'db': str, 'api': str, 'security': str, 'graphql': str}
        """
        parts: Dict[str, List[str]] = {
            'overview': [],
            'db': [],
            'api': [],
            'security': [],
            'graphql': [],
        }

        self.ai_descriptions = ai_descriptions or {}

        # --- Overview ---
        def add_overview():
            lines = parts['overview']
            lines.append("# プロジェクト概要")
            lines.append("")
            if self.ai_descriptions.get('project_summary'):
                lines.append(self.ai_descriptions['project_summary'])
                lines.append("")
        add_overview()

        # --- DB ---
        def add_db():
            lines = parts['db']
            lines.append("# Database Schema")
            lines.append("")
            if data.get('migrations'):
                framework_tables = {'cache', 'cache_locks', 'jobs', 'job_batches', 'failed_jobs', 'sessions', 'password_reset_tokens', 'personal_access_tokens'}
                business = []
                framework = []
                for migration in data['migrations']:
                    name = migration.get('table_name')
                    if not name:
                        continue
                    if name in framework_tables:
                        framework.append(migration)
                    else:
                        business.append(migration)

                # 業務テーブルのみ詳細
                for migration in business:
                    lines.append(f"## テーブル: {migration['table_name']}")
                    if migration.get('files'):
                        lines.append(f"- マイグレーション: {', '.join(f'`{f}`' for f in migration['files'])}")
                    if migration.get('columns'):
                        lines.append("- テーブル定義:")
                        for col in migration['columns']:
                            lines.append(f"  - `{col['name']}` ({col['type']})")
                    if migration.get('indexes'):
                        lines.append("- インデックス/ユニーク:")
                        for idx in migration['indexes']:
                            lines.append(f"  - `{idx['column']}` ({idx['type']})")
                    if migration.get('foreign_keys'):
                        lines.append("- 外部キー:")
                        for fk in migration['foreign_keys']:
                            ref = f"{fk.get('references')} on {fk.get('on')}" if fk.get('references') and fk.get('on') else ""
                            ondelete = f" onDelete={fk.get('on_delete')}" if fk.get('on_delete') else ""
                            onupdate = f" onUpdate={fk.get('on_update')}" if fk.get('on_update') else ""
                            lines.append(f"  - `{fk['column']}` -> {ref}{ondelete}{onupdate}".strip())
                    lines.append("")

                # フレームワーク系は一覧だけ
                if framework:
                    lines.append("## フレームワーク補助テーブル（概要のみ）")
                    for mig in framework:
                        lines.append(f"- {mig['table_name']} (migrations: {', '.join(mig.get('files', []))})")
                    lines.append("")
        add_db()

        # --- API (REST/Services) ---
        def add_api():
            lines = parts['api']
            lines.append("# API (Routes / Controllers / Services)")
            lines.append("")
            # Routes
            if data.get('routes'):
                lines.append("## Routes")
                total_routes = sum(len(lst) for lst in data['routes'].values())
                if total_routes == 0:
                    lines.append("- ルートは検出されませんでした（GraphQL中心の可能性）")
                for route_type, route_list in data['routes'].items():
                    if route_list:
                        lines.append(f"### {route_type}.php")
                        for route in route_list:
                            mw = route.get('middleware') or []
                            mw_text = f" (middleware: {', '.join(mw)})" if mw else ""
                            lines.append(f"- **{route['method']}** `{route['uri']}` → `{route['action']}`{mw_text}")
                        lines.append("")
                    else:
                        lines.append(f"### {route_type}.php")
                        lines.append("- ルート定義が見つかりませんでした")
                        lines.append("")
            # Controllers
            if data.get('controllers'):
                lines.append("## Controllers")
                for controller in data['controllers']:
                    lines.append(f"### {controller['class_name']}")
                    lines.append(f"- ファイル: `{controller['file_path']}`")
                    if controller.get('traits'):
                        lines.append(f"- トレイト: {', '.join(controller['traits'])}")
                    desc = self.ai_descriptions.get(f"controller_{controller['class_name']}", "")
                    if desc:
                        lines.append(f"- 説明: {desc}")
                    if controller.get('methods'):
                        lines.append("- メソッド:")
                        for method in controller['methods']:
                            params = method.get('parameters') or ''
                            sig = f"{method['name']}({params})" if params else f"{method['name']}()"
                            lines.append(f"  - `{sig}`")
                    else:
                        lines.append("- メソッド: （検出されませんでした。Laravel標準Authコントローラの可能性）")
                    if controller.get('validations'):
                        lines.append("- バリデーション (controller内 validate):")
                        for val in controller['validations']:
                            lines.append(f"  - `{val['field']}`: {val['rules']}")
                    if controller.get('traits'):
                        trait_text = ', '.join(controller['traits'])
                        lines.append(f"- 備考: トレイト {trait_text} を使用（標準Auth動作の可能性）")
                    lines.append("")
            # Services
            if data.get('services'):
                lines.append("## Services")
                for service in data['services']:
                    lines.append(f"### {service['class_name']}")
                    lines.append(f"- ファイル: `{service['file_path']}`")
                    desc = self.ai_descriptions.get(f"service_{service['class_name']}", "")
                    if desc:
                        lines.append(f"- 説明: {desc}")
                    if service.get('logic_notes'):
                        lines.append("- 振る舞い要約:")
                        for note in service['logic_notes']:
                            lines.append(f"  - {note}")
                    if service.get('methods'):
                        lines.append("- メソッド:")
                        for m in service['methods']:
                            params = m.get('parameters') or ''
                            sig = f"{m['name']}({params})" if params else f"{m['name']}()"
                            lines.append(f"  - `{sig}`")
                    lines.append("")
        add_api()

        # --- Security/Validation ---
        def add_security():
            lines = parts['security']
            lines.append("# セキュリティ / バリデーション")
            lines.append("")
            # Middleware
            if data.get('middleware'):
                lines.append("## Middleware")
                for mw in data['middleware']:
                    lines.append(f"- `{mw['class_name']}` ({mw['file_path']})")
                lines.append("")
            else:
                lines.append("## Middleware")
                lines.append("- 検出されませんでした (GraphQLの@guard等で認証している可能性あり)")
                lines.append("")
            # Kernel middleware
            kernel = data.get('kernel') or {}
            if kernel:
                lines.append("## Kernel Middleware")
                if kernel.get('global'):
                    lines.append("- Global:")
                    for m in kernel['global']:
                        lines.append(f"  - {m}")
                if kernel.get('groups'):
                    lines.append("- Groups:")
                    for name, mids in kernel['groups'].items():
                        lines.append(f"  - {name}: {', '.join(mids)}")
                if kernel.get('route'):
                    lines.append("- Route Middleware:")
                    for alias, m in kernel['route'].items():
                        lines.append(f"  - {alias}: {m}")
                lines.append("")
            # Requests
            if data.get('requests'):
                lines.append("## Form Requests")
                for req in data['requests']:
                    lines.append(f"### {req['class_name']}")
                    lines.append(f"- ファイル: `{req['file_path']}`")
                    if req.get('rules'):
                        lines.append("- バリデーションルール:")
                        for rule in req['rules']:
                            lines.append(f"  - `{rule['field']}`: {rule['rules']}")
                    lines.append("")
            else:
                lines.append("## Form Requests")
                lines.append("- 専用FormRequestは検出されませんでした (コントローラ内バリデーションの可能性)")
                lines.append("")
            # Policies
            if data.get('policies'):
                lines.append("## Policies")
                for policy in data['policies']:
                    lines.append(f"### {policy['class_name']}")
                    lines.append(f"- ファイル: `{policy['file_path']}`")
                    if policy.get('methods'):
                        lines.append("- メソッド:")
                        for method in policy['methods']:
                            lines.append(f"  - `{method}()`")
                    lines.append("")
            return
        add_security()

        # --- GraphQL ---
        def add_graphql():
            lines = parts['graphql']
            lines.append("# GraphQL API")
            lines.append("")
            if data.get('graphql_endpoint'):
                lines.append(f"- エンドポイント: `{data['graphql_endpoint']}`")
                lines.append("")
            if data.get('graphql_schemas'):
                lines.append("## スキーマファイル一覧")
                for file_path in sorted(data['graphql_schemas'].keys()):
                    lines.append(f"- {file_path}")
                lines.append("")
            if data.get('graphql_operations'):
                lines.append("## Queries / Mutations 要約")
                if data['graphql_operations'].get('queries'):
                    lines.append("### Queries")
                    for q in data['graphql_operations']['queries']:
                        arg_text = f"({q['args']})" if q.get('args') else ""
                        lines.append(f"- `{q['name']}{arg_text}` : {q.get('return')}")
                    lines.append("")
                if data['graphql_operations'].get('mutations'):
                    lines.append("### Mutations")
                    for m in data['graphql_operations']['mutations']:
                        arg_text = f"({m['args']})" if m.get('args') else ""
                        lines.append(f"- `{m['name']}{arg_text}` : {m.get('return')}")
                    lines.append("")
            if data.get('graphql_resolvers'):
                lines.append("## Resolvers")
                if data['graphql_resolvers'].get('queries'):
                    lines.append("### Queries")
                    for q in data['graphql_resolvers']['queries']:
                        lines.append(f"- `{q}`")
                    lines.append("")
                if data['graphql_resolvers'].get('mutations'):
                    lines.append("### Mutations")
                    for m in data['graphql_resolvers']['mutations']:
                        lines.append(f"- `{m}`")
                    lines.append("")
        add_graphql()

        return {k: '\n'.join(v).strip() for k, v in parts.items()}

    def _generate_models_section(self, models: List[Dict]):
        """Modelsセクション生成"""
        self.add_header("Models", level=2)
        self.add_line()

        for model in models:
            class_name = model['class_name']
            self.add_header(f"{class_name} モデル", level=3)

            # AI説明
            description = self.ai_descriptions.get(f"model_{class_name}", "")
            if description:
                self.add_line(f"**説明**: {description}")
                self.add_line()

            # テーブル名
            if model.get('table_name'):
                self.add_line(f"- **テーブル**: `{model['table_name']}`")
            else:
                # デフォルトのテーブル名を推測
                table_name = self._pluralize(class_name.lower())
                self.add_line(f"- **テーブル**: `{table_name}` (デフォルト)")

            # Fillable
            if model.get('fillable'):
                self.add_line(f"- **Fillable**: {', '.join(f'`{f}`' for f in model['fillable'])}")

            # リレーション
            if model.get('relations'):
                self.add_line("- **リレーション**:")
                for rel in model['relations']:
                    rel_desc = self.ai_descriptions.get(f"relation_{class_name}_{rel['method']}", "")
                    rel_text = f"  - `{rel['method']}()` - {rel['type']} → {rel['related_model']}"
                    if rel_desc:
                        rel_text += f" ({rel_desc})"
                    self.add_line(rel_text)

            self.add_line()

    def _generate_graphql_section(self, schemas: Dict[str, str]):
        """GraphQLセクション生成"""
        self.add_header("GraphQL API", level=2)
        self.add_line()

        for file_path, content in schemas.items():
            self.add_header(f"📄 {file_path}", level=3)
            self.add_line()
            snippet_lines = content.splitlines()
            preview = '\n'.join(snippet_lines[:20])
            if len(snippet_lines) > 20:
                preview += "\n... (truncated)"
            self.add_code_block(preview, language='graphql')
            self.add_line()

    def _generate_resolvers_section(self, resolvers: Dict[str, List[str]]):
        """Resolversセクション生成"""
        self.add_header("GraphQL Resolvers", level=2)
        self.add_line()

        if resolvers.get('queries'):
            self.add_header("Queries", level=3)
            for query_file in resolvers['queries']:
                self.add_line(f"- `{query_file}`")
            self.add_line()

        if resolvers.get('mutations'):
            self.add_header("Mutations", level=3)
            for mutation_file in resolvers['mutations']:
                self.add_line(f"- `{mutation_file}`")
            self.add_line()

    def _generate_migrations_section(self, migrations: List[Dict]):
        """Migrationsセクション生成"""
        self.add_header("Database Schema (Migrations)", level=2)
        self.add_line()

        for migration in migrations:
            if migration.get('table_name'):
                self.add_header(f"テーブル: {migration['table_name']}", level=3)
                if migration.get('files'):
                    self.add_line(f"**マイグレーション**: {', '.join(f'`{f}`' for f in migration['files'])}")
                self.add_line()

                if migration.get('columns'):
                    self.add_line("**最終カラム定義**:")
                    for col in migration['columns']:
                        self.add_line(f"- `{col['name']}` ({col['type']})")
                    self.add_line()

    def _generate_controllers_section(self, controllers: List[Dict]):
        """Controllersセクション生成"""
        self.add_header("Controllers", level=2)
        self.add_line()

        for controller in controllers:
            self.add_header(controller['class_name'], level=3)
            self.add_line(f"**ファイル**: `{controller['file_path']}`")
            self.add_line()

            # AI説明
            description = self.ai_descriptions.get(f"controller_{controller['class_name']}", "")
            if description:
                self.add_line(f"**説明**: {description}")
                self.add_line()

            if controller.get('methods'):
                self.add_line("**メソッド**:")
                for method in controller['methods']:
                    params = method.get('parameters', '')
                    if params:
                        self.add_line(f"- `{method['name']}({params})`")
                    else:
                        self.add_line(f"- `{method['name']}()`")
                self.add_line()

    def _generate_routes_section(self, routes: Dict[str, List[Dict]]):
        """Routesセクション生成"""
        self.add_header("Routes", level=2)
        self.add_line()

        for route_type, route_list in routes.items():
            if route_list:
                self.add_header(f"{route_type}.php", level=3)
                self.add_line()

                for route in route_list:
                    self.add_line(f"- **{route['method']}** `{route['uri']}`")
                    self.add_line(f"  - Action: `{route['action']}`")
                self.add_line()

    def _generate_services_section(self, services: List[Dict]):
        """Servicesセクション生成"""
        self.add_header("Services (ビジネスロジック)", level=2)
        self.add_line()

        for service in services:
            self.add_header(service['class_name'], level=3)
            self.add_line(f"**ファイル**: `{service['file_path']}`")
            self.add_line()

            # AI説明
            description = self.ai_descriptions.get(f"service_{service['class_name']}", "")
            if description:
                self.add_line(f"**説明**: {description}")
                self.add_line()

            if service.get('methods'):
                self.add_line("**メソッド**:")
                for method in service['methods']:
                    self.add_line(f"- `{method}()`")
                self.add_line()

    def _generate_middleware_section(self, middleware: List[Dict]):
        """Middlewareセクション生成"""
        self.add_header("Middleware", level=2)
        self.add_line()

        for mw in middleware:
            self.add_line(f"- **{mw['class_name']}** - `{mw['file_path']}`")
        self.add_line()

    def _generate_requests_section(self, requests: List[Dict]):
        """Form Requestsセクション生成"""
        self.add_header("Form Requests (バリデーション)", level=2)
        self.add_line()

        for request in requests:
            self.add_header(request['class_name'], level=3)
            self.add_line(f"**ファイル**: `{request['file_path']}`")
            self.add_line()

            if request.get('rules'):
                self.add_line("**バリデーションルール**:")
                for rule in request['rules']:
                    self.add_line(f"- `{rule['field']}`: {rule['rules']}")
                self.add_line()

    def _generate_policies_section(self, policies: List[Dict]):
        """Policiesセクション生成"""
        self.add_header("Policies (認可)", level=2)
        self.add_line()

        for policy in policies:
            self.add_header(policy['class_name'], level=3)
            self.add_line(f"**ファイル**: `{policy['file_path']}`")
            self.add_line()

            if policy.get('methods'):
                self.add_line("**認可メソッド**:")
                for method in policy['methods']:
                    self.add_line(f"- `{method}()`")
                self.add_line()

    def _generate_jobs_section(self, jobs: List[Dict]):
        """Jobsセクション生成"""
        self.add_header("Jobs (非同期処理)", level=2)
        self.add_line()

        for job in jobs:
            self.add_line(f"- **{job['class_name']}** - `{job['file_path']}`")
        self.add_line()

    def _generate_events_section(self, events: List[Dict]):
        """Eventsセクション生成"""
        self.add_header("Events", level=2)
        self.add_line()

        for event in events:
            self.add_line(f"- **{event['class_name']}** - `{event['file_path']}`")
        self.add_line()

    def _generate_listeners_section(self, listeners: List[Dict]):
        """Listenersセクション生成"""
        self.add_header("Listeners", level=2)
        self.add_line()

        for listener in listeners:
            self.add_line(f"- **{listener['class_name']}** - `{listener['file_path']}`")
        self.add_line()

    def add_header(self, text: str, level: int = 1):
        """見出し追加"""
        self.lines.append(f"{'#' * level} {text}")

    def add_line(self, text: str = ""):
        """行追加"""
        self.lines.append(text)

    def add_code_block(self, code: str, language: str = ""):
        """コードブロック追加"""
        self.lines.append(f"```{language}")
        self.lines.append(code)
        self.lines.append("```")

    def _pluralize(self, word: str) -> str:
        """簡易的な複数形変換"""
        if word.endswith('y'):
            return word[:-1] + 'ies'
        elif word.endswith('s'):
            return word + 'es'
        else:
            return word + 's'
