"""
AI Client - Gemini API連携
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# 環境変数読み込み
load_dotenv()


class AIClient:
    """Gemini APIクライアント"""

    def __init__(self, model_name='gemini-2.0-flash-exp'):
        """
        初期化

        Args:
            model_name: 使用するGeminiモデル名
        """
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError('GEMINI_API_KEY環境変数が設定されていません')

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        """
        プロンプトからテキスト生成

        Args:
            prompt: 生成プロンプト

        Returns:
            生成されたテキスト
        """
        response = self.model.generate_content(prompt)
        return response.text.strip()

    def generate_json(self, prompt: str) -> dict:
        """
        プロンプトからJSON生成

        Args:
            prompt: 生成プロンプト

        Returns:
            パースされたJSON（dict）
        """
        import json

        text = self.generate(prompt)

        # ```json ``` で囲まれている場合は除去
        if text.startswith('```'):
            lines = text.split('\n')
            # 最初の行（```json）と最後の行（```）を除去
            text = '\n'.join(lines[1:-1])

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f'JSON解析エラー: {e}\nレスポンス: {text[:500]}...')
