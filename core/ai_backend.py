"""
AI Backend - 複数のAIバックエンドに対応
"""

import os
import json
import subprocess
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()


class AIBackend(ABC):
    """AI バックエンドの抽象基底クラス"""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """テキスト生成"""
        pass

    def generate_json(self, prompt: str) -> dict:
        """JSON生成"""
        text = self.generate(prompt)

        # ```json ``` で囲まれている場合は除去
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.rfind('```')
            text = text[start:end].strip()
        elif text.startswith('```'):
            lines = text.split('\n')
            text = '\n'.join(lines[1:-1])

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f'JSON解析エラー: {e}\nレスポンス: {text[:500]}...')


class ClaudeBackend(AIBackend):
    """Claude API バックエンド"""

    def __init__(self, model='claude-3-5-sonnet-20241022'):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError('ANTHROPIC_API_KEY環境変数が設定されていません')

        try:
            import anthropic
        except ImportError:
            raise ImportError(
                'anthropic パッケージがインストールされていません。\n'
                'pip install anthropic を実行してください。'
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text


class ClaudeCodeBackend(AIBackend):
    """Claude Code CLI バックエンド (ローカル環境)"""

    def __init__(self, cli_path=None):
        # 環境変数 CLAUDE_CLI_PATH があればそれを使用、なければ 'claude' コマンドを使用
        if cli_path is None:
            cli_path = os.getenv('CLAUDE_CLI_PATH', 'claude')

        self.cli_path = cli_path

        # フルパスが指定されている場合のみ存在確認
        if '/' in cli_path and not os.path.exists(cli_path):
            raise ValueError(f'Claude CLI が見つかりません: {cli_path}')

    def generate(self, prompt: str) -> str:
        """Claude Code CLI を使ってテキスト生成"""
        try:
            env = os.environ.copy()
            # CLIは独自の認証を持つため、誤った外部APIキーを渡さない
            env.pop('ANTHROPIC_API_KEY', None)

            # claude --print でプロンプトを送信（非対話モード）
            result = subprocess.run(
                [self.cli_path, '--print', '--output-format', 'text'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
                env=env
            )

            if result.returncode != 0:
                raise RuntimeError(
                    f'Claude CLI エラー (code {result.returncode}): '
                    f'stdout={result.stdout.strip()[:500]} stderr={result.stderr.strip()[:500]}'
                )

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise RuntimeError('Claude CLI がタイムアウトしました (120秒)')
        except Exception as e:
            raise RuntimeError(f'Claude CLI 実行エラー: {e}')


class GeminiBackend(AIBackend):
    """Gemini API バックエンド"""

    def __init__(self, model='gemini-2.0-flash-exp'):
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY環境変数が設定されていません')

        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                'google-generativeai パッケージがインストールされていません。\n'
                'pip install google-generativeai を実行してください。'
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text.strip()


def get_ai_backend(backend_name: str = None) -> AIBackend:
    """
    AI バックエンドを取得

    Args:
        backend_name: バックエンド名 ('claude' | 'claude-code' | 'gemini')
                     Noneの場合は環境変数 AI_BACKEND を参照
                     'claude-code' でローカルCLI使用

    Returns:
        AIBackend インスタンス
    """
    if backend_name is None:
        backend_name = os.getenv('AI_BACKEND', 'claude-code')

    backend_name = backend_name.lower()

    if backend_name == 'claude':
        return ClaudeBackend()
    elif backend_name == 'claude-code':
        return ClaudeCodeBackend()
    elif backend_name == 'gemini':
        return GeminiBackend()
    else:
        raise ValueError(f'未対応のバックエンド: {backend_name}')
