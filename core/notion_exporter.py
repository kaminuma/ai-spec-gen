"""
Notion Exporter - MarkdownをNotionページとしてアップロード

軽量なMarkdown→Notionブロック変換を行い、単一ページとして作成する。
"""

from __future__ import annotations

import os
from typing import List, Dict


class NotionExporter:
    """Notionへのアップロードを担当するクラス"""

    def __init__(self, token: str):
        try:
            from notion_client import Client  # type: ignore
        except ImportError as e:
            raise ImportError(
                'notion-client がインストールされていません。pip install notion-client を実行してください。'
            ) from e

        self.client = Client(auth=token)

    def _line_to_block(self, line: str) -> Dict:
        """1行のMarkdownを簡易的にNotionブロックに変換"""
        line = line.rstrip()
        if not line:
            return {}

        if line.startswith('### '):
            return {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"rich_text": [{"text": {"content": line[4:]}}]},
            }
        if line.startswith('## '):
            return {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"text": {"content": line[3:]}}]},
            }
        if line.startswith('# '):
            return {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"text": {"content": line[2:]}}]},
            }
        if line.startswith('- '):
            return {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"text": {"content": line[2:]}}]},
            }
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": line}}]},
        }

    def markdown_to_blocks(self, markdown: str) -> List[Dict]:
        """シンプルなMarkdownをNotionブロック配列に変換"""
        blocks: List[Dict] = []
        for raw_line in markdown.splitlines():
            block = self._line_to_block(raw_line)
            if block:
                blocks.append(block)
        return blocks

    def upload_markdown(self, markdown: str, parent_page_id: str, title: str = "AI Spec") -> str:
        """Markdown文字列をNotionページとしてアップロードし、ページURLを返す"""
        blocks = self.markdown_to_blocks(markdown)

        # ページ作成
        response = self.client.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "title": [{"text": {"content": title}}]
            },
            children=blocks[:100],  # Notion API制限: 最初の100ブロックをまとめて
        )

        page_id = response["id"]
        page_url = response.get("url", "")

        # 100件を超える場合は追記
        for i in range(100, len(blocks), 100):
            chunk = blocks[i:i + 100]
            self.client.blocks.children.append(page_id, children=chunk)

        return page_url

    def upload_hierarchy(self, parts: Dict[str, str], parent_page_id: str, root_title: str = "AI Spec") -> str:
        """
        複数のMarkdownパートを子ページとしてアップロードし、ルートページURLを返す
        parts: {'overview': str, 'db': str, 'api': str, 'security': str, 'graphql': str}
        """
        # ルートページを作成（本文なし）
        root = self.client.pages.create(
            parent={"page_id": parent_page_id},
            properties={
                "title": [{"text": {"content": root_title}}]
            },
            children=[]
        )
        root_id = root["id"]
        root_url = root.get("url", "")

        # 子ページを作成
        order = ['overview', 'db', 'api', 'security', 'graphql']
        for key in order:
            if key not in parts:
                continue
            content = parts[key]
            blocks = self.markdown_to_blocks(content)
            self.client.pages.create(
                parent={"page_id": root_id},
                properties={
                    "title": [{"text": {"content": key}}]
                },
                children=blocks[:100]
            )
            # 100件超は追記
            if len(blocks) > 100:
                page_id = self.client.search(filter={"property": "title", "text": {"equals": key}})["results"][0]["id"]
                for i in range(100, len(blocks), 100):
                    chunk = blocks[i:i + 100]
                    self.client.blocks.children.append(page_id, children=chunk)

        return root_url

    def upload_hierarchy_flat(
        self,
        parts: Dict[str, str],
        parent_page_id: str,
        emoji_map: Dict[str, str] = None,
        title_map: Dict[str, str] = None,
    ) -> Dict[str, str]:
        """
        複数パートを親ページ直下に子ページとして作成し、key -> url を返す
        """
        urls = {}
        order = ['overview', 'db', 'api', 'security', 'graphql']
        for key in order:
            if key not in parts:
                continue
            content = parts[key]
            blocks = self.markdown_to_blocks(content)
            icon = None
            if emoji_map and key in emoji_map:
                icon = {"type": "emoji", "emoji": emoji_map[key]}
            title = title_map.get(key, key) if title_map else key

            resp = self.client.pages.create(
                parent={"page_id": parent_page_id},
                icon=icon,
                properties={
                    "title": [{"text": {"content": title}}]
                },
                children=blocks[:100]
            )
            page_url = resp.get("url", "")
            urls[key] = page_url

            # 100件超は追記
            page_id = resp["id"]
            if len(blocks) > 100:
                for i in range(100, len(blocks), 100):
                    chunk = blocks[i:i + 100]
                    self.client.blocks.children.append(page_id, children=chunk)

        return urls


def get_notion_credentials(cli_token: str | None, cli_page_id: str | None) -> tuple[str, str]:
    """
    CLI引数または環境変数からNotionクレデンシャルを取得するヘルパー
    優先順: CLI引数 > NOTION_TOKEN / NOTION_API_KEY, CLI引数 > NOTION_PARENT_PAGE_ID / NOTION_PAGE_ID
    """
    token = cli_token or os.getenv("NOTION_TOKEN") or os.getenv("NOTION_API_KEY")
    page_id = (
        cli_page_id
        or os.getenv("NOTION_PARENT_PAGE_ID")
        or os.getenv("NOTION_PAGE_ID")
    )

    if not token:
        raise ValueError("Notion APIトークンが指定されていません (--notion-token もしくは NOTION_TOKEN/NOTION_API_KEY)")
    if not page_id:
        raise ValueError("Notion親ページIDが指定されていません (--notion-page-id もしくは NOTION_PARENT_PAGE_ID/NOTION_PAGE_ID)")

    return token, page_id
