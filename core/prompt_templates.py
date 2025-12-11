"""
Prompt Templates - AI生成用のプロンプトテンプレート

Few-Shot学習と仕様書テンプレートを活用したプロンプトエンジニアリング
"""

# ============================================
# Few-Shot Examples for Models
# ============================================

MODEL_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (モデル説明の例)

例1:
モデル名: User
テーブル名: users
Fillable: name, email, password
リレーション: todos (hasMany → Todo), profile (hasOne → Profile)

説明: ユーザーアカウント情報を管理し、認証とTodoとの関連を持つ

---

例2:
モデル名: Todo
テーブル名: todos
Fillable: title, description, completed, user_id, deadline, priority
リレーション: user (belongsTo → User), category (belongsTo → Category)

説明: ユーザーのタスク情報を管理し、期限・優先度・カテゴリで分類できる

---

例3:
モデル名: Category
テーブル名: categories
Fillable: name, color
リレーション: todos (hasMany → Todo)

説明: Todoのカテゴリ分類を管理し、名前と色で視覚的に区別する
"""


# ============================================
# Few-Shot Examples for Controllers
# ============================================

CONTROLLER_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (コントローラー説明の例)

例1:
クラス名: TodoController
メソッド: index(), create(), store(Request), show($id), edit($id), update(Request, $id), destroy($id)

説明: Todoのリソース管理を担当し、CRUD操作と一覧表示を提供する

---

例2:
クラス名: AuthController
メソッド: login(Request), logout(), register(Request), me()

説明: ユーザー認証を担当し、ログイン・登録・トークン管理を行う

---

例3:
クラス名: CategoryController
メソッド: index(), store(Request), update(Request, $id), destroy($id)

説明: カテゴリのCRUD操作を担当し、Todo分類の管理を行う
"""


# ============================================
# Few-Shot Examples for Services
# ============================================

SERVICE_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (サービス説明の例)

例1:
クラス名: TodoQueryBuilder
メソッド: applyFilters(), filterByStatus(), filterByPriority(), sortByDeadline()

説明: Todoのクエリ構築とフィルタリングロジックを担当し、複雑な検索条件を処理する

---

例2:
クラス名: NotificationService
メソッド: sendEmail(), sendSlack(), notifyDeadline()

説明: 通知処理を担当し、メール・Slackでのリマインダーを送信する

---

例3:
クラス名: ReportGenerator
メソッド: generatePDF(), generateCSV(), exportUserStats()

説明: レポート生成を担当し、統計データをPDF/CSV形式で出力する
"""


# ============================================
# Specification Document Template
# ============================================

SPEC_DOCUMENT_TEMPLATE = """
# Laravel プロジェクト技術仕様書テンプレート

## 1. プロジェクト概要
- **プロジェクト名**: [自動抽出]
- **フレームワーク**: Laravel
- **アーキテクチャ**: MVC + Repository/Service層
- **主要機能**: [AIが解析データから推測]

## 2. データベース設計
### テーブル一覧
[Migrationsから抽出したテーブル定義]

### ER図（テキスト表現）
[Modelsのリレーションから推測]

## 3. ドメインモデル
### Models
[Eloquent Modelsの詳細]
- 役割説明（AI生成）
- リレーション図
- ビジネスロジック

## 4. API設計
### RESTful API
[Routes + Controllers から抽出]

### GraphQL API
[GraphQL Schemas から抽出]

## 5. ビジネスロジック
### Services
[Services層の責務]

### Policies
[認可ルール]

## 6. バリデーション
### Form Requests
[各リクエストのバリデーションルール]

## 7. 非同期処理
### Jobs/Queues
[バックグラウンドジョブ]

### Events/Listeners
[イベント駆動処理]

## 8. セキュリティ
### Middleware
[認証・認可・CORS等]

### Policies
[リソースアクセス制御]

## 9. 技術的な特徴
[AIが全体を分析して推測]
"""


# ============================================
# Prompt Generator Functions
# ============================================

def generate_model_prompt(model: dict) -> str:
    """
    Eloquent Modelの説明を生成するためのプロンプト

    Few-Shot学習を活用し、一貫性のある説明を生成
    """
    class_name = model['class_name']
    table_name = model.get('table_name', 'N/A')
    fillable = ', '.join(model.get('fillable', []))
    relations = ', '.join([f"{r['method']} ({r['type']} → {r['related_model']})"
                          for r in model.get('relations', [])])

    prompt = f"""
{MODEL_DESCRIPTION_EXAMPLES}

### 新しいモデルの説明を生成

モデル名: {class_name}
テーブル名: {table_name}
Fillable: {fillable}
リレーション: {relations}

上記のFew-Shot例に倣って、このモデルの役割を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を管理し、〜の機能を提供する」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_controller_prompt(controller: dict) -> str:
    """Controllerの説明を生成するためのプロンプト"""
    class_name = controller['class_name']
    methods = ', '.join([m['name'] + '()' for m in controller.get('methods', [])])

    prompt = f"""
{CONTROLLER_DESCRIPTION_EXAMPLES}

### 新しいコントローラーの説明を生成

クラス名: {class_name}
メソッド: {methods}

上記のFew-Shot例に倣って、このコントローラーの責務を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を担当し、〜の操作を提供する」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_service_prompt(service: dict) -> str:
    """Serviceの説明を生成するためのプロンプト"""
    class_name = service['class_name']
    method_items = service.get('methods', [])
    method_names = []
    if method_items and isinstance(method_items[0], dict):
        method_names = [m.get('name') for m in method_items if m.get('name')]
    else:
        method_names = method_items
    methods = ', '.join([m for m in method_names if m])

    prompt = f"""
{SERVICE_DESCRIPTION_EXAMPLES}

### 新しいサービスの説明を生成

クラス名: {class_name}
メソッド: {methods}

上記のFew-Shot例に倣って、このサービスの責務を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を担当し、〜の処理を行う」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_project_summary_prompt(data: dict) -> str:
    """
    プロジェクト全体のサマリーを生成するためのプロンプト

    Notion連携を考慮した構造化された出力を生成
    """
    models_count = len(data.get('models', []))
    controllers_count = len(data.get('controllers', []))
    routes_count = sum(len(routes) for routes in data.get('routes', {}).values())
    migrations_count = len(data.get('migrations', []))
    services_count = len(data.get('services', []))
    has_graphql = len(data.get('graphql_schemas', {})) > 0

    models_list = ', '.join([m['class_name'] for m in data.get('models', [])])

    # GraphQL情報
    graphql_queries = len(data.get('graphql_resolvers', {}).get('queries', []))
    graphql_mutations = len(data.get('graphql_resolvers', {}).get('mutations', []))

    prompt = f"""
あなたはLaravelプロジェクトの技術仕様書を作成するテクニカルライターです。
以下の解析データは「実際のLaravelアプリケーション」のコード解析結果です。  
このアプリケーションのみについて説明し、ツールやAIについては一切言及しないでください。

## 解析対象プロジェクトのデータ

### アーキテクチャ構成
- **Models**: {models_count}個 ({models_list or 'なし'})
- **Controllers**: {controllers_count}個
- **Routes**: {routes_count}個
- **Migrations**: {migrations_count}個
- **Services**: {services_count}個
- **GraphQL API**: {'あり' if has_graphql else 'なし'}
  - Queries: {graphql_queries}個
  - Mutations: {graphql_mutations}個

### 推測のヒント
- Modelsの名前から、このアプリケーションが管理するドメインを推測してください
- GraphQL APIがある場合は、SPAやモバイルアプリ向けのバックエンドの可能性
- Servicesがある場合は、ビジネスロジックが分離された設計

## 出力要件

以下のMarkdown構造**のみ**で出力してください。先頭の挨拶や前置き、---などの区切り、余計なテキストを一切追加しないでください。Notionにペーストしても崩れないよう、シンプルな見出しと箇条書きのみを使ってください。

## プロジェクト概要

[このLaravelアプリケーションが何を目的としているか、どんな問題を解決するかを2〜3文で説明]

## 主要機能

- [機能1: 具体的な機能名と簡潔な説明]
- [機能2: 具体的な機能名と簡潔な説明]
- [機能3: 具体的な機能名と簡潔な説明]

## 技術的な特徴

- [特徴1: 使用技術やアーキテクチャパターン]
- [特徴2: API設計やデータモデリングの特徴]
- [特徴3: 認証・認可やセキュリティ設計]

## 重要な注意事項

1. **このツール自体（AI Spec Generator）について説明しないでください**
2. **解析対象のLaravelアプリケーション**についてのみ記述してください（ツール/AI/仕様書生成について言及しない）
3. 「このプロジェクトは〜」と書く場合、それは**解析対象のLaravelアプリケーション**を指します
4. 推測が難しい場合は、ModelsやRoutes名から最も妥当なドメインを推測してください
5. 回答は上記のMarkdown構造のみ。コードブロック・装飾・注釈・謝罪・質問・補足は禁止
6. 箇条書きは3〜5件に収め、動詞は名詞形で簡潔に（例: 「タスク管理」「カテゴリ分類」）
"""
    return prompt.strip()


# ============================================
# Java/Spring Boot用のFew-Shot Examples
# ============================================

JAVA_ENTITY_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (Entity説明の例)

例1:
Entity名: UserEntity
テーブル名: users
フィールド: user_id, username, email, password, created_at, updated_at
アノテーション: @Entity, @Table, @Id, @GeneratedValue

説明: ユーザーアカウント情報を永続化し、認証とアプリケーション全体のユーザー管理を担う

---

例2:
Entity名: TodoEntity
テーブル名: todos
フィールド: todo_id, title, description, completed, user_id, deadline
アノテーション: @Entity, @Table, @Id, @ManyToOne

説明: ユーザーのタスク情報を管理し、期限や完了状態を記録する

---

例3:
Entity名: RefreshTokenEntity
テーブル名: refresh_tokens
フィールド: token_id, user_id, token, expires_at, created_at
アノテーション: @Entity, @Table, @Id, @Column

説明: リフレッシュトークンを永続化し、セキュアなトークン更新を実現する
"""


JAVA_CONTROLLER_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (Controller説明の例)

例1:
Controller名: TodoController
ベースパス: /api/todos
エンドポイント: GET /, POST /, PUT /{id}, DELETE /{id}

説明: TodoのCRUD操作を提供し、RESTful APIとしてクライアントにタスク管理機能を公開する

---

例2:
Controller名: AuthController
ベースパス: /auth
エンドポイント: POST /login, POST /register, POST /refresh, POST /logout

説明: ユーザー認証とトークン管理を担当し、セキュアな認証フローを提供する

---

例3:
Controller名: UserController
ベースパス: /api/users
エンドポイント: GET /{id}, PUT /{id}, DELETE /{id}, GET /me

説明: ユーザー情報の取得と更新を提供し、プロフィール管理機能を公開する
"""


JAVA_SERVICE_DESCRIPTION_EXAMPLES = """
### Few-Shot Examples (Service説明の例)

例1:
Service名: TodoService
メソッド: findAll(), findById(), create(), update(), delete()

説明: Todoのビジネスロジックを集約し、永続化層とコントローラー層を仲介する

---

例2:
Service名: AuthService
メソッド: login(), register(), refreshToken(), validateToken()

説明: 認証処理とトークン管理のロジックを担当し、セキュリティ要件を実装する

---

例3:
Service名: NotificationService
メソッド: sendEmail(), sendPushNotification(), scheduleReminder()

説明: 通知処理を担当し、メールやプッシュ通知の送信ロジックを提供する
"""


# ============================================
# Java用のPrompt Generator Functions
# ============================================

def generate_java_entity_prompt(entity: dict) -> str:
    """JPA Entityの説明を生成するためのプロンプト"""
    entity_name = entity['name']
    table_name = entity.get('table', 'N/A')
    fields = ', '.join([f['name'] for f in entity.get('fields', [])])
    annotations = set()
    for field in entity.get('fields', []):
        annotations.update(field.get('annotations', []))
    annotation_str = ', '.join([f'@{a}' for a in annotations])

    prompt = f"""
{JAVA_ENTITY_DESCRIPTION_EXAMPLES}

### 新しいEntityの説明を生成

Entity名: {entity_name}
テーブル名: {table_name}
フィールド: {fields}
アノテーション: {annotation_str}

上記のFew-Shot例に倣って、このEntityの役割を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を永続化し、〜を担う」または「〜を管理し、〜を記録する」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_java_controller_prompt(controller: dict) -> str:
    """REST Controllerの説明を生成するためのプロンプト"""
    controller_name = controller['name']
    base_path = controller.get('base_path', '/')
    endpoints = controller.get('endpoints', [])
    endpoint_summary = ', '.join([f"{e['method']} {e['path']}" for e in endpoints[:5]])

    prompt = f"""
{JAVA_CONTROLLER_DESCRIPTION_EXAMPLES}

### 新しいControllerの説明を生成

Controller名: {controller_name}
ベースパス: {base_path}
エンドポイント: {endpoint_summary}

上記のFew-Shot例に倣って、このControllerの責務を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を提供し、〜を公開する」または「〜を担当し、〜を提供する」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_java_service_prompt(service: dict) -> str:
    """Serviceの説明を生成するためのプロンプト"""
    service_name = service['name']
    methods = ', '.join([m['name'] + '()' for m in service.get('methods', [])])

    prompt = f"""
{JAVA_SERVICE_DESCRIPTION_EXAMPLES}

### 新しいServiceの説明を生成

Service名: {service_name}
メソッド: {methods}

上記のFew-Shot例に倣って、このServiceの責務を**1文**で簡潔に日本語で説明してください。

説明のフォーマット:
「〜を担当し、〜を提供する」または「〜を集約し、〜を実装する」

回答は説明文のみを返してください（前置きや補足は不要）。
"""
    return prompt.strip()


def generate_java_project_summary_prompt(data: dict) -> str:
    """Java/Spring Bootプロジェクト全体のサマリーを生成するためのプロンプト"""
    entities_count = len(data.get('entities', []))
    controllers_count = len(data.get('controllers', []))
    services_count = len(data.get('services', []))
    endpoints_count = len(data.get('rest_endpoints', []))

    entities_list = ', '.join([e['name'] for e in data.get('entities', [])])

    prompt = f"""
あなたはJava/Spring Bootプロジェクトの技術仕様書を作成するテクニカルライターです。
以下の解析データは「実際のSpring Bootアプリケーション」のコード解析結果です。
このアプリケーションのみについて説明し、ツールやAIについては一切言及しないでください。

## 解析対象プロジェクトのデータ

### アーキテクチャ構成
- **Entities**: {entities_count}個 ({entities_list or 'なし'})
- **Controllers**: {controllers_count}個
- **Services**: {services_count}個
- **REST Endpoints**: {endpoints_count}個

### 推測のヒント
- Entitiesの名前から、このアプリケーションが管理するドメインを推測してください
- REST API構成から、SPAやモバイルアプリ向けのバックエンドの可能性
- Servicesの存在から、ビジネスロジックが分離された設計

## 出力要件

以下のMarkdown構造**のみ**で出力してください。先頭の挨拶や前置き、---などの区切り、余計なテキストを一切追加しないでください。

## プロジェクト概要

[このSpring Bootアプリケーションが何を目的としているか、どんな問題を解決するかを2〜3文で説明]

## 主要機能

- [機能1: 具体的な機能名と簡潔な説明]
- [機能2: 具体的な機能名と簡潔な説明]
- [機能3: 具体的な機能名と簡潔な説明]

## 技術的な特徴

- [特徴1: Spring Bootの機能やアーキテクチャパターン]
- [特徴2: API設計やデータモデリングの特徴]
- [特徴3: 認証・認可やセキュリティ設計]

## 重要な注意事項

1. **このツール自体（AI Spec Generator）について説明しないでください**
2. **解析対象のSpring Bootアプリケーション**についてのみ記述してください
3. 推測が難しい場合は、EntitiesやController名から最も妥当なドメインを推測してください
4. 回答は上記のMarkdown構造のみ。コードブロック・装飾・注釈・謝罪・質問・補足は禁止
5. 箇条書きは3〜5件に収め、動詞は名詞形で簡潔に
"""
    return prompt.strip()
