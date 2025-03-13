import asyncio
from typing import List

from googlesearch import search

from react_agent.tool.base import BaseTool


class GoogleSearch(BaseTool):
    """Google搜索工具。"""
    
    name: str = "google_search"
    description: str = """使用Google搜索引擎查找信息。执行 Google 搜索并返回相关链接列表。
                        当您需要在网络上查找信息、获取最新数据或研究特定主题时，请使用此工具。
                        该工具返回与搜索查询匹配的 URL 列表"""
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(required) The search query to submit to Google.",
            },
            "num_results": {
                "type": "integer",
                "description": "(optional) The number of search results to return. Default is 10.",
                "default": 10,
            },
        },
        "required": ["query"],
    }

    async def execute(self, query: str, num_results: int = 10) -> List[str]:
        """
        Execute a Google search and return a list of URLs.

        Args:
            query (str): The search query to submit to Google.
            num_results (int, optional): The number of search results to return. Default is 10.

        Returns:
            List[str]: A list of URLs matching the search query.
        """
        # Run the search in a thread pool to prevent blocking
        loop = asyncio.get_event_loop()
        links = await loop.run_in_executor(
            None, lambda: list(search(query, num=num_results))
        )

        return links
