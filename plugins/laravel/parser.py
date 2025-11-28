"""
Laravel Parser - Laravel プロジェクトを解析
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Iterable


class LaravelParser:
    """Laravelプロジェクトパーサー"""

    def __init__(self, project_root: Path):
        """
        初期化

        Args:
            project_root: Laravelプロジェクトのルートディレクトリ
        """
        self.project_root = Path(project_root)

    def parse_all(self) -> Dict[str, Any]:
        """
        プロジェクト全体を解析

        Returns:
            解析結果の辞書
        """
        return {
            'models': self.parse_models(),
            'controllers': self.parse_controllers(),
            'routes': self.parse_routes(),
            'migrations': self.parse_migrations(),
            'services': self.parse_services(),
            'middleware': self.parse_middleware(),
            'requests': self.parse_requests(),
            'policies': self.parse_policies(),
            'jobs': self.parse_jobs(),
            'events': self.parse_events(),
            'listeners': self.parse_listeners(),
            'graphql_schemas': self.parse_graphql_schemas(),
            'graphql_resolvers': self.parse_graphql_resolvers(),
            'kernel': self.parse_kernel(),
            'graphql_endpoint': self.parse_graphql_endpoint(),
            'graphql_operations': self.parse_graphql_operations(),
        }

    def parse_models(self) -> List[Dict]:
        """
        Eloquent Modelsを解析

        Returns:
            モデル情報のリスト
        """
        models_dir = self.project_root / 'app' / 'Models'
        if not models_dir.exists():
            return []

        models = []
        for php_file in models_dir.glob('*.php'):
            model_info = self._parse_model_file(php_file)
            if model_info:
                models.append(model_info)

        return models

    def _parse_model_file(self, file_path: Path) -> Dict:
        """
        単一のModelファイルを解析

        Args:
            file_path: PHPファイルのパス

        Returns:
            モデル情報の辞書
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # クラス名抽出
        class_match = re.search(r'class\s+(\w+)\s+extends\s+Model', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # テーブル名抽出
        table_match = re.search(r'protected\s+\$table\s*=\s*[\'"](\w+)[\'"]', content)
        table_name = table_match.group(1) if table_match else None

        # fillable抽出
        fillable_match = re.search(r'protected\s+\$fillable\s*=\s*\[(.*?)\]', content, re.DOTALL)
        fillable = []
        if fillable_match:
            fillable_str = fillable_match.group(1)
            fillable = [f.strip().strip('\'"') for f in fillable_str.split(',') if f.strip()]

        # リレーション抽出
        relations = self._extract_relations(content)

        return {
            'class_name': class_name,
            'file_path': str(file_path.relative_to(self.project_root)),
            'table_name': table_name,
            'fillable': fillable,
            'relations': relations,
        }

    def _extract_relations(self, content: str) -> List[Dict]:
        """
        Eloquentリレーションを抽出

        Args:
            content: PHPファイルの内容

        Returns:
            リレーション情報のリスト
        """
        relations = []

        # belongsTo, hasMany, hasOne, belongsToMany を抽出
        pattern = r'public\s+function\s+(\w+)\s*\([^)]*\)\s*:\s*\w+\s*\{\s*return\s+\$this->(belongsTo|hasMany|hasOne|belongsToMany)\((\w+)::class'

        for match in re.finditer(pattern, content):
            method_name = match.group(1)
            relation_type = match.group(2)
            related_model = match.group(3)

            relations.append({
                'method': method_name,
                'type': relation_type,
                'related_model': related_model,
            })

        return relations

    def parse_graphql_schemas(self) -> Dict[str, str]:
        """
        GraphQLスキーマファイルを解析

        Returns:
            ファイルパス -> 内容 の辞書
        """
        graphql_dir = self.project_root / 'graphql'
        if not graphql_dir.exists():
            return {}

        schemas = {}
        for graphql_file in graphql_dir.rglob('*.graphql'):
            relative_path = graphql_file.relative_to(graphql_dir)
            with open(graphql_file, 'r', encoding='utf-8') as f:
                schemas[str(relative_path)] = f.read()

        return schemas

    def parse_graphql_operations(self) -> Dict[str, List[Dict[str, str]]]:
        """
        GraphQL Query/Mutationの簡易的な定義一覧を抽出
        """
        ops = {'queries': [], 'mutations': []}
        schemas = self.parse_graphql_schemas()

        def extract_ops(kind: str, content: str) -> List[Dict[str, str]]:
            results = []
            pattern = rf'extend\s+type\s+{kind}\s*\{{(.*?)\}}'
            for block in re.findall(pattern, content, re.DOTALL):
                for line in block.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    # name(args): ReturnType
                    m = re.match(r'(\w+)\s*\(([^)]*)\)\s*:\s*([\w\[\]!]+)', line)
                    if m:
                        name, args, ret = m.groups()
                        results.append({'name': name, 'args': args, 'return': ret})
                    else:
                        m = re.match(r'(\w+)\s*:\s*([\w\[\]!]+)', line)
                        if m:
                            name, ret = m.groups()
                            results.append({'name': name, 'args': '', 'return': ret})
            return results

        for content in schemas.values():
            ops['queries'].extend(extract_ops('Query', content))
            ops['mutations'].extend(extract_ops('Mutation', content))

        return ops

    def parse_graphql_resolvers(self) -> Dict[str, List[str]]:
        """
        GraphQL Resolversを解析

        Returns:
            カテゴリ -> ファイルリスト の辞書
        """
        resolvers = {
            'queries': [],
            'mutations': [],
        }

        # Queries
        queries_dir = self.project_root / 'app' / 'GraphQL' / 'Queries'
        if queries_dir.exists():
            resolvers['queries'] = [
                str(f.relative_to(self.project_root))
                for f in queries_dir.glob('*.php')
            ]

        # Mutations
        mutations_dir = self.project_root / 'app' / 'GraphQL' / 'Mutations'
        if mutations_dir.exists():
            resolvers['mutations'] = [
                str(f.relative_to(self.project_root))
                for f in mutations_dir.glob('*.php')
            ]

        return resolvers

    def parse_controllers(self) -> List[Dict]:
        """
        Controllersを解析

        Returns:
            コントローラー情報のリスト
        """
        controllers = []

        # app/Http/Controllers
        controllers_dir = self.project_root / 'app' / 'Http' / 'Controllers'
        if controllers_dir.exists():
            for php_file in controllers_dir.rglob('*.php'):
                controller_info = self._parse_controller_file(php_file)
                if controller_info:
                    controllers.append(controller_info)

        return controllers

    def _parse_controller_file(self, file_path: Path) -> Dict:
        """単一のControllerファイルを解析"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # クラス名抽出
        class_match = re.search(r'class\s+(\w+)\s+extends\s+Controller', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        traits = []
        for trait_match in re.finditer(r'use\s+([\w\\]+);', content):
            trait_name = trait_match.group(1).split('\\')[-1]
            traits.append(trait_name)

        # メソッド抽出（public function）
        methods = []
        method_pattern = r'public\s+function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            params = match.group(2).strip()

            # コンストラクタやマジックメソッドは除外
            if method_name.startswith('__'):
                continue

            methods.append({
                'name': method_name,
                'parameters': params if params else None,
            })

        # Authトレイト由来メソッドの補完
        methods = self._augment_auth_methods(traits, methods)

        # Controller内バリデーション validate([...])
        validations = []
        validate_pattern = r'validate\s*\(\s*\[\s*(.*?)\s*\]\s*\)'
        for vm in re.finditer(validate_pattern, content, re.DOTALL):
            body = vm.group(1)
            for rule in re.finditer(r'[\'"](\w+)[\'"]\s*=>\s*[\'"]([^\'"]+)[\'"]', body):
                validations.append({'field': rule.group(1), 'rules': rule.group(2)})

        # Validator::make([...]) パターン
        validator_pattern = r'Validator::make\s*\(\s*[^,]+,\s*\[\s*(.*?)\s*\]\s*\)'
        for vm in re.finditer(validator_pattern, content, re.DOTALL):
            body = vm.group(1)
            for rule in re.finditer(r'[\'"](\w+)[\'"]\s*=>\s*[\'"]([^\'"]+)[\'"]', body):
                validations.append({'field': rule.group(1), 'rules': rule.group(2)})

        return {
            'class_name': class_name,
            'file_path': str(file_path.relative_to(self.project_root)),
            'methods': methods,
            'traits': traits,
            'validations': validations,
        }

    def _augment_auth_methods(self, traits: List[str], methods: List[Dict]) -> List[Dict]:
        """Laravel標準Authトレイトを検出したら代表メソッドを補完"""
        known = {
            'AuthenticatesUsers': ['login', 'logout', 'showLoginForm'],
            'RegistersUsers': ['showRegistrationForm', 'register'],
            'ResetsPasswords': ['showResetForm', 'reset'],
            'VerifiesEmails': ['verify', 'show'],
        }
        existing = {m['name'] for m in methods}
        for t in traits:
            if t in known:
                for name in known[t]:
                    if name not in existing:
                        methods.append({'name': name, 'parameters': None, 'note': f'from {t}'})
        return methods

    def parse_routes(self) -> Dict[str, List[Dict]]:
        """
        Routesを解析

        Returns:
            ルート情報の辞書 (api, web, etc.)
        """
        routes = {}

        routes_dir = self.project_root / 'routes'
        if not routes_dir.exists():
            return routes

        for route_file in routes_dir.glob('*.php'):
            route_type = route_file.stem  # api, web, etc.
            routes_in_file = []
            routes_in_file.extend(self._parse_route_file(route_file))
            # グループ対応
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
            routes_in_file.extend(self._parse_routes_with_groups(content))
            routes[route_type] = routes_in_file

        return routes

    def _parse_route_file(self, file_path: Path) -> List[Dict]:
        """単一のRouteファイルを解析"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        routes = []

        # Route::get/post/put/delete/patch など + optional ->middleware(...)
        route_pattern = r'Route::(get|post|put|delete|patch|options|any)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*([^\);]+)\)\s*(?:->middleware\(([^)]*)\))?'

        for match in re.finditer(route_pattern, content):
            method = match.group(1).upper()
            uri = match.group(2)
            raw_action = match.group(3).strip()
            action = self._normalize_route_action(raw_action)
            mw_raw = match.group(4) or ''
            middlewares = [m.strip().strip('\'"') for m in mw_raw.split(',') if m.strip()]

            routes.append({
                'method': method,
                'uri': uri,
                'action': action,
                'middleware': middlewares,
            })

        # Route::middleware(...)->get(...)
        mw_route_pattern = r'Route::middleware\(\s*([^)]+)\s*\)\s*->\s*(get|post|put|delete|patch|options|any)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*([^\);]+)'
        for match in re.finditer(mw_route_pattern, content):
            mw_raw = match.group(1)
            method = match.group(2).upper()
            uri = match.group(3)
            raw_action = match.group(4).strip()
            action = self._normalize_route_action(raw_action)
            middlewares = [m.strip().strip('\'"') for m in mw_raw.split(',') if m.strip()]
            routes.append({
                'method': method,
                'uri': uri,
                'action': action,
                'middleware': middlewares,
            })

        return routes

    def _parse_routes_with_groups(self, content: str) -> List[Dict]:
        """Routeグループ (middleware/prefix) を含めてパース"""
        routes = []

        # プレフィックスやミドルウェアを持つグループに対応
        group_pattern = re.compile(
            r'Route::(?:middleware\(([^)]*)\)\s*)?(?:prefix\(([^)]*)\)\s*)?group\s*\(\s*function\s*\(\s*\)\s*\{(.*?)\}\s*\);',
            re.DOTALL
        )
        for gm in group_pattern.finditer(content):
            middleware_raw = gm.group(1) or ''
            prefix_raw = gm.group(2) or ''
            body = gm.group(3)

            middlewares = [m.strip().strip('\'"') for m in middleware_raw.split(',') if m.strip()]
            prefix = prefix_raw.strip().strip('\'"')

            route_pattern = r'Route::(get|post|put|delete|patch|options|any)\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*([^\);]+)\)\s*(?:->middleware\(([^)]*)\))?'
            for match in re.finditer(route_pattern, body):
                method = match.group(1).upper()
                uri = match.group(2)
                if prefix:
                    uri = f"{prefix.rstrip('/')}/{uri.lstrip('/')}"
                raw_action = match.group(3).strip()
                action = self._normalize_route_action(raw_action)
                mw_raw = match.group(4) or ''
                extra_mw = [m.strip().strip('\'"') for m in mw_raw.split(',') if m.strip()]
                all_mw = middlewares.copy()
                all_mw.extend(extra_mw)

                routes.append({
                    'method': method,
                    'uri': uri,
                    'action': action,
                    'middleware': all_mw,
                })

        return routes

    def _normalize_route_action(self, action: str) -> str:
        """Routeアクション表記を統一する"""
        # ["Controller::class, 'method'"] を Class@method 形式に
        class_call = re.search(r'([\w\\\\]+)::class\s*,\s*[\'"](\w+)[\'"]', action)
        if class_call:
            return f"{class_call.group(1)}@{class_call.group(2)}"

        # 'Controller@method' 形式
        at_call = re.search(r'[\'"]?([\w\\\\]+@[\w]+)[\'"]?', action)
        if at_call:
            return at_call.group(1)

        # クロージャなどはそのまま
        return action

    def parse_migrations(self) -> List[Dict]:
        """
        Migrationsを解析

        Returns:
            マイグレーション情報のリスト（テーブル単位の最終スキーマ）
        """
        table_schemas: Dict[str, Dict[str, str]] = {}
        table_indexes: Dict[str, List[Dict[str, str]]] = {}
        table_fks: Dict[str, List[Dict[str, str]]] = {}
        table_files: Dict[str, List[str]] = {}

        migrations_dir = self.project_root / 'database' / 'migrations'
        if not migrations_dir.exists():
            return []

        for migration_file in sorted(migrations_dir.glob('*.php')):
            for table_name, ops in self._parse_migration_file(migration_file):
                if not table_name:
                    continue

                table_files.setdefault(table_name, [])
                if migration_file.name not in table_files[table_name]:
                    table_files[table_name].append(migration_file.name)

                schema = table_schemas.setdefault(table_name, {})
                idxs = table_indexes.setdefault(table_name, [])
                fks = table_fks.setdefault(table_name, [])
                for op in ops:
                    action = op['action']
                    col = op['name']
                    if action == 'add':
                        if op['type'] in {'index', 'unique', 'primary'}:
                            idxs.append({'column': col, 'type': op['type']})
                        elif op['type'] == 'foreign':
                            fks.append({
                                'column': col,
                                'references': op.get('references'),
                                'on': op.get('on'),
                                'on_delete': op.get('on_delete'),
                                'on_update': op.get('on_update'),
                            })
                        else:
                            schema[col] = op['type']
                    elif action == 'drop':
                        schema.pop(col, None)

        # 整形して返す
        result = []
        for table, cols in table_schemas.items():
            columns = [{'name': name, 'type': cols[name]} for name in cols.keys()]
            result.append({
                'table_name': table,
                'columns': columns,
                'files': table_files.get(table, []),
                'indexes': table_indexes.get(table, []),
                'foreign_keys': table_fks.get(table, []),
            })

        # テーブル名でソート
        result.sort(key=lambda x: x['table_name'])
        return result

    def _parse_migration_file(self, file_path: Path) -> Iterable[tuple[str, List[Dict[str, str]]]]:
        """単一のMigrationファイルを解析し、(table_name, operations) をyieldする"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # up() セクションのみを対象にする（down の dropColumn を無視する）
        up_start = content.find('function up')
        down_start = content.find('function down', up_start if up_start != -1 else 0)
        if up_start != -1 and down_start != -1:
            content = content[up_start:down_start]

        # Schema::create / Schema::table ブロックを全て抽出
        block_pattern = re.compile(
            r'Schema::(create|table)\s*\(\s*[\'"](\w+)[\'"]\s*,\s*function\s*\([^)]*\)\s*\{(.*?)\}\s*\);',
            re.DOTALL
        )

        for match in block_pattern.finditer(content):
            action_type = match.group(1)
            table_name = match.group(2)
            body = match.group(3)

            ops: List[Dict[str, str]] = []

            # 追加カラム: $table->string('name')
            for add in re.finditer(r'\$table->(\w+)\s*\(\s*[\'"](\w+)[\'"]', body):
                col_type = add.group(1)
                col_name = add.group(2)
                if col_type in {'index', 'unique', 'primary', 'foreign', 'fullText', 'spatialIndex'}:
                    # インデックス系はカラムとして扱わない
                    continue
                ops.append({'action': 'add', 'name': col_name, 'type': col_type})

            # id / increments 系
            for add in re.finditer(r'\$table->(id|bigIncrements|increments)\s*\(\s*[\'"]?(\w*)[\'"]?\s*\)', body):
                col_type = add.group(1)
                col_name = add.group(2) or 'id'
                ops.append({'action': 'add', 'name': col_name, 'type': col_type})

            # timestamps / softDeletes 等
            if 'timestamps()' in body:
                ops.append({'action': 'add', 'name': 'created_at', 'type': 'timestamp'})
                ops.append({'action': 'add', 'name': 'updated_at', 'type': 'timestamp'})
            if 'softDeletes()' in body:
                ops.append({'action': 'add', 'name': 'deleted_at', 'type': 'timestamp'})

            # foreignId()->constrained()
            for add in re.finditer(r'\$table->foreignId\s*\(\s*[\'"](\w+)[\'"]\s*\)(?:->\w+\([^)]*\))*', body):
                col_name = add.group(1)
                ops.append({'action': 'add', 'name': col_name, 'type': 'foreignId'})

            # index/unique/primary (単一カラム)
            for idx in re.finditer(r'\$table->(index|unique|primary)\s*\(\s*[\'"](\w+)[\'"]', body):
                ops.append({'action': 'add', 'name': idx.group(2), 'type': idx.group(1)})

            # 外部キー詳細 ($table->foreign('user_id')->references('id')->on('users')->onDelete('cascade');)
            for fk in re.finditer(r'\$table->foreign\s*\(\s*[\'"](\w+)[\'"]\s*\)([^;]+);', body):
                col = fk.group(1)
                chain = fk.group(2)
                ref = re.search(r'references\(\s*[\'"](\w+)[\'"]', chain)
                on = re.search(r'on\(\s*[\'"](\w+)[\'"]', chain)
                on_delete = re.search(r'onDelete\(\s*[\'"]?(\w+)[\'"]?\)', chain)
                on_update = re.search(r'onUpdate\(\s*[\'"]?(\w+)[\'"]?\)', chain)
                ops.append({
                    'action': 'add',
                    'name': col,
                    'type': 'foreign',
                    'references': ref.group(1) if ref else None,
                    'on': on.group(1) if on else None,
                    'on_delete': on_delete.group(1) if on_delete else None,
                    'on_update': on_update.group(1) if on_update else None,
                })

            # dropColumn 単体
            for drop in re.finditer(r'dropColumn\(\s*[\'"](\w+)[\'"]\s*\)', body):
                ops.append({'action': 'drop', 'name': drop.group(1), 'type': 'drop'})

            # dropColumn 配列
            for drop_arr in re.finditer(r'dropColumn\(\s*\[\s*([^\]]+)\]\s*\)', body):
                names_str = drop_arr.group(1)
                for name in re.findall(r'[\'"](\w+)[\'"]', names_str):
                    ops.append({'action': 'drop', 'name': name, 'type': 'drop'})

            yield table_name, ops

    def parse_kernel(self) -> Dict[str, Any]:
        """app/Http/Kernel.php からミドルウェア構成を抽出"""
        kernel_file = self.project_root / 'app' / 'Http' / 'Kernel.php'
        if not kernel_file.exists():
            return {}

        content = kernel_file.read_text(encoding='utf-8')
        result: Dict[str, Any] = {'global': [], 'groups': {}, 'route': {}}

        # global middleware
        global_match = re.search(r'\$middleware\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if global_match:
            result['global'] = [m.strip().strip('\'"') for m in global_match.group(1).split(',') if m.strip()]

        # groups
        groups_match = re.search(r'\$middlewareGroups\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if groups_match:
            groups_body = groups_match.group(1)
            for group_match in re.finditer(r'[\'"](\w+)[\'"]\s*=>\s*\[(.*?)\]', groups_body, re.DOTALL):
                name = group_match.group(1)
                middlewares = [m.strip().strip('\'"') for m in group_match.group(2).split(',') if m.strip()]
                result['groups'][name] = middlewares

        # route middleware
        route_match = re.search(r'\$routeMiddleware\s*=\s*\[(.*?)\];', content, re.DOTALL)
        if route_match:
            for rm in re.finditer(r'[\'"](\w+)[\'"]\s*=>\s*[\'"]([^\'"]+)[\'"]', route_match.group(1)):
                result['route'][rm.group(1)] = rm.group(2)

        return result

    def parse_graphql_endpoint(self) -> str:
        """Lighthouse の GraphQLエンドポイントを config から推測（デフォルト /graphql）"""
        config_file = self.project_root / 'config' / 'lighthouse.php'
        if config_file.exists():
            content = config_file.read_text(encoding='utf-8')
            match = re.search(r'\'route\'\s*=>\s*[\'"]([^\'"]+)[\'"]', content)
            if match:
                return match.group(1)
        return '/graphql'

    def parse_services(self) -> List[Dict]:
        """
        Servicesを解析（app/Services ディレクトリ）

        Returns:
            サービス情報のリスト
        """
        services = []

        services_dir = self.project_root / 'app' / 'Services'
        if not services_dir.exists():
            return services

        for php_file in services_dir.rglob('*.php'):
            service_info = self._parse_service_file(php_file)
            if service_info:
                services.append(service_info)

        return services

    def _parse_service_file(self, file_path: Path) -> Dict:
        """単一のServiceファイルを解析"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # クラス名抽出
        class_match = re.search(r'class\s+(\w+)', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # publicメソッド抽出
        methods = []
        method_pattern = r'public\s+(?:static\s+)?function\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(method_pattern, content):
            method_name = match.group(1)
            if not method_name.startswith('__'):
                params = match.group(2).strip()
                methods.append({
                    'name': method_name,
                    'parameters': params if params else None,
                })

        logic_notes = self._summarize_todo_query_builder(content, class_name)

        return {
            'class_name': class_name,
            'file_path': str(file_path.relative_to(self.project_root)),
            'methods': methods,
            'raw_content': content,
            'logic_notes': logic_notes,
        }

    def _summarize_todo_query_builder(self, content: str, class_name: str) -> List[str]:
        """
        TodoQueryBuilder のようなクエリビルダ系のフィルタ/ソートロジックを簡易要約
        いまはキーワード検出ベースで汎用性は低めだが、仕様書向けの手がかりを出す
        """
        notes: List[str] = []
        if 'deadline_status' in content:
            notes.append("deadline_status で期限状態をフィルタ（overdue/due_today/due_this_week）")
        if 'completed' in content:
            notes.append("completed が null でない場合のみ完了フラグで絞り込み")
        if 'priority' in content:
            notes.append("priority が指定されれば優先度で絞り込み（high/medium/low）")
        if 'category_id' in content:
            notes.append("category_id が指定されればカテゴリで絞り込み")
        if 'sort_by' in content or 'sort_direction' in content:
            notes.append("sort_by/sort_direction に従って並び替え。priorityはカスタム順、deadlineはNULLを末尾")
        return notes

    def parse_middleware(self) -> List[Dict]:
        """Middlewareを解析"""
        middleware = []

        middleware_dir = self.project_root / 'app' / 'Http' / 'Middleware'
        if not middleware_dir.exists():
            return middleware

        for php_file in middleware_dir.glob('*.php'):
            with open(php_file, 'r', encoding='utf-8') as f:
                content = f.read()

            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                middleware.append({
                    'class_name': class_match.group(1),
                    'file_path': str(php_file.relative_to(self.project_root)),
                })

        return middleware

    def parse_requests(self) -> List[Dict]:
        """Form Requestsを解析"""
        requests = []

        requests_dir = self.project_root / 'app' / 'Http' / 'Requests'
        if not requests_dir.exists():
            return requests

        for php_file in requests_dir.rglob('*.php'):
            request_info = self._parse_request_file(php_file)
            if request_info:
                requests.append(request_info)

        return requests

    def _parse_request_file(self, file_path: Path) -> Dict:
        """単一のForm Requestファイルを解析"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        class_match = re.search(r'class\s+(\w+)\s+extends\s+FormRequest', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # rulesメソッド内のバリデーションルール抽出（簡易版）
        rules = []
        rules_match = re.search(r'public\s+function\s+rules\s*\(\s*\)\s*:\s*array\s*\{(.*?)\}', content, re.DOTALL)
        if rules_match:
            rules_content = rules_match.group(1)
            # 'field' => 'required|...' パターン
            rule_pattern = r'[\'"](\w+)[\'"]\s*=>\s*[\'"]([^\'"]+)[\'"]'
            for match in re.finditer(rule_pattern, rules_content):
                field = match.group(1)
                validation = match.group(2)
                rules.append({
                    'field': field,
                    'rules': validation,
                })

        return {
            'class_name': class_name,
            'file_path': str(file_path.relative_to(self.project_root)),
            'rules': rules,
        }

    def parse_policies(self) -> List[Dict]:
        """Policiesを解析"""
        policies = []

        policies_dir = self.project_root / 'app' / 'Policies'
        if not policies_dir.exists():
            return policies

        for php_file in policies_dir.glob('*.php'):
            with open(php_file, 'r', encoding='utf-8') as f:
                content = f.read()

            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                # メソッド抽出（view, create, update, delete など）
                methods = []
                method_pattern = r'public\s+function\s+(\w+)\s*\('
                for match in re.finditer(method_pattern, content):
                    method_name = match.group(1)
                    if not method_name.startswith('__'):
                        methods.append(method_name)

                policies.append({
                    'class_name': class_match.group(1),
                    'file_path': str(php_file.relative_to(self.project_root)),
                    'methods': methods,
                })

        return policies

    def parse_jobs(self) -> List[Dict]:
        """Jobsを解析"""
        jobs = []

        jobs_dir = self.project_root / 'app' / 'Jobs'
        if not jobs_dir.exists():
            return jobs

        for php_file in jobs_dir.rglob('*.php'):
            with open(php_file, 'r', encoding='utf-8') as f:
                content = f.read()

            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                jobs.append({
                    'class_name': class_match.group(1),
                    'file_path': str(php_file.relative_to(self.project_root)),
                })

        return jobs

    def parse_events(self) -> List[Dict]:
        """Eventsを解析"""
        events = []

        events_dir = self.project_root / 'app' / 'Events'
        if not events_dir.exists():
            return events

        for php_file in events_dir.glob('*.php'):
            with open(php_file, 'r', encoding='utf-8') as f:
                content = f.read()

            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                events.append({
                    'class_name': class_match.group(1),
                    'file_path': str(php_file.relative_to(self.project_root)),
                })

        return events

    def parse_listeners(self) -> List[Dict]:
        """Listenersを解析"""
        listeners = []

        listeners_dir = self.project_root / 'app' / 'Listeners'
        if not listeners_dir.exists():
            return listeners

        for php_file in listeners_dir.glob('*.php'):
            with open(php_file, 'r', encoding='utf-8') as f:
                content = f.read()

            class_match = re.search(r'class\s+(\w+)', content)
            if class_match:
                listeners.append({
                    'class_name': class_match.group(1),
                    'file_path': str(php_file.relative_to(self.project_root)),
                })

        return listeners

    def parse_files(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        指定されたファイルのみを解析

        Args:
            file_paths: 解析対象のファイルパスリスト

        Returns:
            解析結果の辞書
        """
        result = {
            'models': [],
            'graphql_schemas': {},
            'graphql_resolvers': {'queries': [], 'mutations': []},
        }

        for file_path_str in file_paths:
            file_path = Path(file_path_str)

            # Modelファイル
            if 'app/Models' in str(file_path) and file_path.suffix == '.php':
                model_info = self._parse_model_file(file_path)
                if model_info:
                    result['models'].append(model_info)

            # GraphQLスキーマ
            elif file_path.suffix == '.graphql':
                with open(file_path, 'r', encoding='utf-8') as f:
                    result['graphql_schemas'][str(file_path)] = f.read()

            # GraphQL Resolver
            elif 'app/GraphQL' in str(file_path) and file_path.suffix == '.php':
                if 'Queries' in str(file_path):
                    result['graphql_resolvers']['queries'].append(str(file_path))
                elif 'Mutations' in str(file_path):
                    result['graphql_resolvers']['mutations'].append(str(file_path))

        return result
