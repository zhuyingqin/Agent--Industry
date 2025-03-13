"""Google Scholar 搜索工具。

此模块提供了一个工具，用于在 Google Scholar 上搜索学术文献并总结结果。
"""

import asyncio
import os
from typing import Dict, List, Optional, Any
import json

from scholarly import scholarly
try:
    from serpapi import GoogleSearch
except ImportError:
    try:
        # 尝试新版本的导入方式
        from serpapi.google_search import GoogleSearch
    except ImportError:
        # 如果仍然无法导入，创建一个模拟类
        class GoogleSearch:
            """模拟的GoogleSearch类，用于在serpapi不可用时提供占位符。"""
            
            def __init__(self, **kwargs):
                self.params = kwargs
                print(f"警告: serpapi库不可用，使用模拟的GoogleSearch类。参数: {kwargs}")
            
            def get_dict(self):
                """返回一个空的结果字典。"""
                return {
                    "error": "serpapi库不可用，无法执行实际搜索。",
                    "organic_results": []
                }

from langchain_text_splitters import RecursiveCharacterTextSplitter

from react_agent.tool.base import BaseTool


class ScholarSearch(BaseTool):
    """在 Google Scholar 上搜索学术文献并总结结果的工具。"""

    name: str = "scholar_search"
    description: str = """在 Google Scholar 上搜索学术文献并总结结果。
使用此工具可以搜索特定主题的学术文献，并获取文献的摘要、作者、发表年份等信息。
该工具还可以对搜索结果进行总结，提供对该主题的研究概述。
"""
    parameters: dict = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "(必需) 要搜索的学术主题或关键词。",
            },
            "num_results": {
                "type": "integer",
                "description": "(可选) 要返回的搜索结果数量。默认为 5。",
                "default": 5,
            },
            "year_from": {
                "type": "integer",
                "description": "(可选) 搜索结果的起始年份。默认为 None。",
            },
            "year_to": {
                "type": "integer",
                "description": "(可选) 搜索结果的结束年份。默认为 None。",
            },
            "summarize": {
                "type": "boolean",
                "description": "(可选) 是否对搜索结果进行总结。默认为 True。",
                "default": True,
            },
        },
        "required": ["query"],
    }

    async def _search_with_scholarly(self, query: str, num_results: int = 5) -> List[Dict]:
        """使用 scholarly 库在 Google Scholar 上搜索。"""
        loop = asyncio.get_event_loop()
        
        def _search():
            results = []
            search_query = scholarly.search_pubs(query)
            for i in range(min(num_results, 10)):  # scholarly 可能会被限制，所以限制最大结果数
                try:
                    pub = next(search_query)
                    results.append({
                        "title": pub.get("bib", {}).get("title", ""),
                        "authors": pub.get("bib", {}).get("author", ""),
                        "year": pub.get("bib", {}).get("pub_year", ""),
                        "abstract": pub.get("bib", {}).get("abstract", ""),
                        "url": pub.get("pub_url", ""),
                        "citations": pub.get("num_citations", 0),
                    })
                except StopIteration:
                    break
                except Exception as e:
                    print(f"Error fetching publication: {e}")
            return results
        
        return await loop.run_in_executor(None, _search)

    async def _search_with_serpapi(self, query: str, num_results: int = 5, year_from: Optional[int] = None, year_to: Optional[int] = None) -> List[Dict]:
        """使用 SerpAPI 在 Google Scholar 上搜索。"""
        api_key = os.environ.get("SERPAPI_API_KEY")
        if not api_key:
            raise ValueError("SERPAPI_API_KEY 环境变量未设置。请设置 SERPAPI_API_KEY 环境变量。")
        
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": api_key,
            "num": num_results
        }
        
        if year_from and year_to:
            params["as_ylo"] = year_from
            params["as_yhi"] = year_to
        
        loop = asyncio.get_event_loop()
        
        def _search():
            search = GoogleSearch(params)
            results = search.get_dict()
            organic_results = results.get("organic_results", [])
            
            formatted_results = []
            for result in organic_results[:num_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "authors": result.get("publication_info", {}).get("authors", []),
                    "year": result.get("publication_info", {}).get("year", ""),
                    "abstract": result.get("snippet", ""),
                    "url": result.get("link", ""),
                    "citations": result.get("cited_by", {}).get("value", 0),
                })
            
            return formatted_results
        
        return await loop.run_in_executor(None, _search)

    async def _summarize_results(self, results: List[Dict]) -> str:
        """总结搜索结果。"""
        if not results:
            return "未找到相关学术文献。"
        
        # 准备要总结的文本
        text_to_summarize = "以下是搜索到的学术文献：\n\n"
        for i, result in enumerate(results, 1):
            text_to_summarize += f"{i}. 标题: {result['title']}\n"
            text_to_summarize += f"   作者: {result['authors']}\n"
            text_to_summarize += f"   年份: {result['year']}\n"
            text_to_summarize += f"   摘要: {result['abstract']}\n"
            text_to_summarize += f"   引用数: {result['citations']}\n"
            text_to_summarize += f"   链接: {result['url']}\n\n"
        
        text_to_summarize += "\n请总结这些学术文献的主要发现、方法和结论，并指出研究趋势和未来方向。"
        
        # 使用 LLM 总结文本
        # 这里我们假设已经有一个 chat_completion_tool 可以使用
        from react_agent.all_tools import chat_completion_tool
        
        # 如果文本太长，需要分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            chunk_overlap=200,
        )
        
        chunks = text_splitter.split_text(text_to_summarize)
        
        if len(chunks) == 1:
            # 如果只有一个块，直接总结
            summary = await chat_completion_tool.execute(prompt=chunks[0])
        else:
            # 如果有多个块，分别总结然后合并
            summaries = []
            for i, chunk in enumerate(chunks):
                chunk_summary = await chat_completion_tool.execute(
                    prompt=f"这是学术文献信息的第 {i+1}/{len(chunks)} 部分。请总结这部分内容：\n\n{chunk}"
                )
                summaries.append(chunk_summary)
            
            # 合并所有总结
            combined_summary = "\n\n".join(summaries)
            summary = await chat_completion_tool.execute(
                prompt=f"以下是对学术文献的分部分总结，请将它们整合为一个连贯的总结：\n\n{combined_summary}"
            )
        
        return summary

    async def execute(
        self,
        query: str,
        num_results: int = 5,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        summarize: bool = True,
        **kwargs: Any,
    ) -> str:
        """
        在 Google Scholar 上搜索学术文献并总结结果。

        参数:
            query (str): 要搜索的学术主题或关键词。
            num_results (int, optional): 要返回的搜索结果数量。默认为 5。
            year_from (int, optional): 搜索结果的起始年份。默认为 None。
            year_to (int, optional): 搜索结果的结束年份。默认为 None。
            summarize (bool, optional): 是否对搜索结果进行总结。默认为 True。
            **kwargs: 其他参数。

        返回:
            str: 搜索结果或总结。
        """
        try:
            # 尝试使用 SerpAPI 搜索
            try:
                results = await self._search_with_serpapi(query, num_results, year_from, year_to)
            except Exception as e:
                # 如果 SerpAPI 失败，回退到 scholarly
                print(f"SerpAPI search failed: {e}. Falling back to scholarly.")
                results = await self._search_with_scholarly(query, num_results)
            
            if not results:
                return "未找到相关学术文献。"
            
            if summarize:
                # 总结搜索结果
                summary = await self._summarize_results(results)
                return summary
            else:
                # 返回原始搜索结果
                return json.dumps(results, ensure_ascii=False, indent=2)
        
        except Exception as e:
            return f"搜索学术文献时出错: {str(e)}" 