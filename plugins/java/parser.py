"""
Java Parser - Java/Spring Boot プロジェクトを解析
"""

import re
from pathlib import Path
from typing import Dict, List, Any


class JavaParser:
    """Java/Spring Bootプロジェクトパーサー"""

    def __init__(self, project_root: Path):
        """
        初期化

        Args:
            project_root: Javaプロジェクトのルートディレクトリ
        """
        self.project_root = Path(project_root)

    def parse_all(self) -> Dict[str, Any]:
        """
        プロジェクト全体を解析

        Returns:
            解析結果の辞書
        """
        return {
            'entities': self.parse_entities(),
            'controllers': self.parse_controllers(),
            'services': self.parse_services(),
            'repositories': self.parse_repositories(),
            'dtos': self.parse_dtos(),
            'configs': self.parse_configs(),
            'rest_endpoints': self.parse_rest_endpoints(),
        }

    def parse_entities(self) -> List[Dict]:
        """
        JPA Entityを解析

        Returns:
            Entity情報のリスト
        """
        entities = []

        # src/main/java 配下の Entity を検索
        for java_file in self.project_root.rglob('*.java'):
            content = java_file.read_text(encoding='utf-8', errors='ignore')

            # @Entity アノテーションを持つクラスを検出
            if '@Entity' in content or '@Table' in content:
                entity_info = self._parse_entity_file(java_file, content)
                if entity_info:
                    entities.append(entity_info)

        return entities

    def _parse_entity_file(self, file_path: Path, content: str) -> Dict:
        """
        Entityファイルを解析

        Args:
            file_path: ファイルパス
            content: ファイル内容

        Returns:
            Entity情報
        """
        # クラス名を取得
        class_match = re.search(r'(?:public\s+)?class\s+(\w+)', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # テーブル名を取得
        table_match = re.search(r'@Table\s*\(\s*name\s*=\s*"(\w+)"', content)
        table_name = table_match.group(1) if table_match else class_name.lower()

        # フィールドを解析
        fields = []
        field_pattern = re.compile(
            r'@(?:Id|Column|OneToMany|ManyToOne|ManyToMany|OneToOne|JoinColumn|GeneratedValue)'
            r'[\s\S]*?'
            r'(?:private|protected|public)\s+(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*;',
            re.MULTILINE
        )

        for match in field_pattern.finditer(content):
            field_type = match.group(1)
            field_name = match.group(2)

            # アノテーションを抽出
            annotations = self._extract_field_annotations(content, field_name)

            fields.append({
                'name': field_name,
                'type': field_type,
                'annotations': annotations,
            })

        return {
            'name': class_name,
            'table': table_name,
            'file': str(file_path.relative_to(self.project_root)),
            'fields': fields,
        }

    def _extract_field_annotations(self, content: str, field_name: str) -> List[str]:
        """
        フィールドのアノテーションを抽出

        Args:
            content: ファイル内容
            field_name: フィールド名

        Returns:
            アノテーションのリスト
        """
        annotations = []

        # フィールド定義の前の行からアノテーションを抽出
        pattern = re.compile(
            rf'(@\w+(?:\([^)]*\))?)\s*'
            rf'(?:(?:@\w+(?:\([^)]*\))?)\s*)*'
            rf'(?:private|protected|public)\s+\w+(?:<[\w\s,<>]+>)?\s+{field_name}\s*;',
            re.MULTILINE
        )

        match = pattern.search(content)
        if match:
            # すべてのアノテーションを取得
            anno_pattern = re.compile(r'@(\w+)(?:\([^)]*\))?')
            for anno_match in anno_pattern.finditer(match.group(0)):
                annotations.append(anno_match.group(1))

        return annotations

    def parse_controllers(self) -> List[Dict]:
        """
        REST Controllerを解析

        Returns:
            Controller情報のリスト
        """
        controllers = []

        for java_file in self.project_root.rglob('*.java'):
            content = java_file.read_text(encoding='utf-8', errors='ignore')

            # @RestController または @Controller を持つクラスを検出
            if '@RestController' in content or '@Controller' in content:
                controller_info = self._parse_controller_file(java_file, content)
                if controller_info:
                    controllers.append(controller_info)

        return controllers

    def _parse_controller_file(self, file_path: Path, content: str) -> Dict:
        """
        Controllerファイルを解析

        Args:
            file_path: ファイルパス
            content: ファイル内容

        Returns:
            Controller情報
        """
        # クラス名を取得
        class_match = re.search(r'(?:public\s+)?class\s+(\w+)', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # ベースパスを取得
        base_path_match = re.search(r'@RequestMapping\s*\(\s*"([^"]+)"', content)
        base_path = base_path_match.group(1) if base_path_match else ''

        # エンドポイントを解析
        endpoints = []
        method_pattern = re.compile(
            r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)'
            r'\s*\(\s*(?:value\s*=\s*)?(?:"([^"]+)"|path\s*=\s*"([^"]+)")?\s*\)',
            re.MULTILINE
        )

        for match in method_pattern.finditer(content):
            http_method = match.group(1).replace('Mapping', '').upper()
            if http_method == 'REQUEST':
                http_method = 'GET'  # デフォルト

            endpoint_path = match.group(2) or match.group(3) or ''
            full_path = f"{base_path}{endpoint_path}"

            # メソッド名を取得
            method_name_match = re.search(
                rf'{re.escape(match.group(0))}[\s\S]*?(?:public|private|protected)\s+\w+(?:<[\w\s,<>]+>)?\s+(\w+)\s*\(',
                content
            )
            method_name = method_name_match.group(1) if method_name_match else 'unknown'

            endpoints.append({
                'method': http_method,
                'path': full_path,
                'handler': method_name,
            })

        return {
            'name': class_name,
            'file': str(file_path.relative_to(self.project_root)),
            'base_path': base_path,
            'endpoints': endpoints,
        }

    def parse_services(self) -> List[Dict]:
        """
        Service層を解析

        Returns:
            Service情報のリスト
        """
        services = []

        for java_file in self.project_root.rglob('*.java'):
            content = java_file.read_text(encoding='utf-8', errors='ignore')

            # @Service アノテーションを持つクラスを検出
            if '@Service' in content:
                service_info = self._parse_service_file(java_file, content)
                if service_info:
                    services.append(service_info)

        return services

    def _parse_service_file(self, file_path: Path, content: str) -> Dict:
        """
        Serviceファイルを解析

        Args:
            file_path: ファイルパス
            content: ファイル内容

        Returns:
            Service情報
        """
        # クラス名を取得
        class_match = re.search(r'(?:public\s+)?class\s+(\w+)', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # メソッドを解析
        methods = []
        method_pattern = re.compile(
            r'(?:public|private|protected)\s+(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*\(([^)]*)\)',
            re.MULTILINE
        )

        for match in method_pattern.finditer(content):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3).strip()

            # コンストラクタは除外
            if method_name == class_name:
                continue

            methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': params if params else 'なし',
            })

        return {
            'name': class_name,
            'file': str(file_path.relative_to(self.project_root)),
            'methods': methods,
        }

    def parse_repositories(self) -> List[Dict]:
        """
        Repositoryを解析

        Returns:
            Repository情報のリスト
        """
        repositories = []

        for java_file in self.project_root.rglob('*.java'):
            content = java_file.read_text(encoding='utf-8', errors='ignore')

            # @Repository または JpaRepository を継承するインターフェースを検出
            if '@Repository' in content or 'extends JpaRepository' in content or 'extends CrudRepository' in content:
                repo_info = self._parse_repository_file(java_file, content)
                if repo_info:
                    repositories.append(repo_info)

        return repositories

    def _parse_repository_file(self, file_path: Path, content: str) -> Dict:
        """
        Repositoryファイルを解析

        Args:
            file_path: ファイルパス
            content: ファイル内容

        Returns:
            Repository情報
        """
        # インターフェース名を取得
        interface_match = re.search(r'(?:public\s+)?interface\s+(\w+)', content)
        if not interface_match:
            return None

        interface_name = interface_match.group(1)

        # Entity型を取得
        entity_match = re.search(r'extends\s+(?:JpaRepository|CrudRepository)<(\w+),\s*(\w+)>', content)
        entity_type = entity_match.group(1) if entity_match else 'Unknown'
        id_type = entity_match.group(2) if entity_match else 'Unknown'

        # カスタムメソッドを解析
        methods = []
        method_pattern = re.compile(r'(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*;', re.MULTILINE)

        for match in method_pattern.finditer(content):
            return_type = match.group(1)
            method_name = match.group(2)
            params = match.group(3).strip()

            methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': params if params else 'なし',
            })

        return {
            'name': interface_name,
            'file': str(file_path.relative_to(self.project_root)),
            'entity': entity_type,
            'id_type': id_type,
            'custom_methods': methods,
        }

    def parse_dtos(self) -> List[Dict]:
        """
        DTO (Data Transfer Object) を解析

        Returns:
            DTO情報のリスト
        """
        dtos = []

        for java_file in self.project_root.rglob('*.java'):
            # dto, request, response パッケージ内のクラスを検索
            if any(keyword in str(java_file).lower() for keyword in ['dto', 'request', 'response']):
                content = java_file.read_text(encoding='utf-8', errors='ignore')

                dto_info = self._parse_dto_file(java_file, content)
                if dto_info:
                    dtos.append(dto_info)

        return dtos

    def _parse_dto_file(self, file_path: Path, content: str) -> Dict:
        """
        DTOファイルを解析

        Args:
            file_path: ファイルパス
            content: ファイル内容

        Returns:
            DTO情報
        """
        # クラス名を取得
        class_match = re.search(r'(?:public\s+)?class\s+(\w+)', content)
        if not class_match:
            return None

        class_name = class_match.group(1)

        # フィールドを解析
        fields = []
        field_pattern = re.compile(
            r'(?:private|protected|public)\s+(\w+(?:<[\w\s,<>]+>)?)\s+(\w+)\s*;',
            re.MULTILINE
        )

        for match in field_pattern.finditer(content):
            field_type = match.group(1)
            field_name = match.group(2)

            fields.append({
                'name': field_name,
                'type': field_type,
            })

        return {
            'name': class_name,
            'file': str(file_path.relative_to(self.project_root)),
            'fields': fields,
        }

    def parse_configs(self) -> List[Dict]:
        """
        設定ファイルを解析

        Returns:
            設定情報のリスト
        """
        configs = []

        # application.properties を検索
        for prop_file in self.project_root.rglob('application*.properties'):
            configs.append({
                'file': str(prop_file.relative_to(self.project_root)),
                'type': 'properties',
                'content': self._parse_properties_file(prop_file),
            })

        # application.yml を検索
        for yml_file in self.project_root.rglob('application*.yml'):
            configs.append({
                'file': str(yml_file.relative_to(self.project_root)),
                'type': 'yml',
                'content': self._parse_yml_file(yml_file),
            })

        for yaml_file in self.project_root.rglob('application*.yaml'):
            configs.append({
                'file': str(yaml_file.relative_to(self.project_root)),
                'type': 'yaml',
                'content': self._parse_yml_file(yaml_file),
            })

        return configs

    def _parse_properties_file(self, file_path: Path) -> Dict:
        """
        propertiesファイルを解析

        Args:
            file_path: ファイルパス

        Returns:
            設定情報
        """
        properties = {}
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    # センシティブ情報をマスク
                    if any(keyword in key.lower() for keyword in ['password', 'secret', 'key', 'token']):
                        value = '***'
                    properties[key.strip()] = value.strip()

        return properties

    def _parse_yml_file(self, file_path: Path) -> str:
        """
        YMLファイルを解析（簡易版）

        Args:
            file_path: ファイルパス

        Returns:
            YML内容（センシティブ情報マスク済み）
        """
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # センシティブ情報をマスク
        lines = []
        for line in content.split('\n'):
            if any(keyword in line.lower() for keyword in ['password', 'secret', 'key', 'token']):
                # 値部分をマスク
                if ':' in line:
                    key_part = line.split(':', 1)[0]
                    lines.append(f"{key_part}: ***")
                else:
                    lines.append(line)
            else:
                lines.append(line)

        return '\n'.join(lines)

    def parse_rest_endpoints(self) -> List[Dict]:
        """
        REST エンドポイントの一覧を生成

        Returns:
            エンドポイント情報のリスト
        """
        endpoints = []
        controllers = self.parse_controllers()

        for controller in controllers:
            for endpoint in controller.get('endpoints', []):
                endpoints.append({
                    'method': endpoint['method'],
                    'path': endpoint['path'],
                    'controller': controller['name'],
                    'handler': endpoint['handler'],
                })

        return sorted(endpoints, key=lambda x: (x['path'], x['method']))
