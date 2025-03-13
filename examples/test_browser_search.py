#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
浏览器搜索功能测试脚本
"""

import asyncio
import logging
from react_agent.tool.browser_use_tool import BrowserUseTool

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_browser_search():
    """测试浏览器搜索功能"""
    logger.info("开始测试浏览器搜索功能")
    
    # 创建浏览器工具实例
    browser_tool = BrowserUseTool()
    
    try:
        # 测试百度搜索
        logger.info("测试百度搜索")
        result = await browser_tool.execute(
            url='https://www.baidu.com', 
            task='在百度搜索Python教程', 
            action='search', 
            parameters={'search_query': 'Python教程'}
        )
        logger.info(f"百度搜索结果: {result[:200]}...")
        
        # 测试GitHub搜索
        logger.info("测试GitHub搜索")
        result = await browser_tool.execute(
            url='https://github.com', 
            task='在GitHub搜索React', 
            action='search', 
            parameters={'search_query': 'React'}
        )
        logger.info(f"GitHub搜索结果: {result[:200]}...")
        
        # 测试Google搜索
        logger.info("测试Google搜索")
        result = await browser_tool.execute(
            url='https://www.google.com', 
            task='在Google搜索AI教程', 
            action='search', 
            parameters={'search_query': 'AI教程'}
        )
        logger.info(f"Google搜索结果: {result[:200]}...")
        
        logger.info("浏览器搜索功能测试完成")
        return True
    except Exception as e:
        logger.error(f"浏览器搜索功能测试失败: {str(e)}")
        return False
    finally:
        # 清理资源
        await browser_tool.cleanup()

async def test_browser_browse_with_search_hint():
    """测试浏览器浏览功能，检查是否提示搜索功能"""
    logger.info("开始测试浏览器浏览功能，检查是否提示搜索功能")
    
    # 创建浏览器工具实例
    browser_tool = BrowserUseTool()
    
    try:
        # 浏览百度首页
        logger.info("浏览百度首页")
        result = await browser_tool.execute(
            url='https://www.baidu.com', 
            task='浏览百度首页', 
            action='browse'
        )
        logger.info(f"百度首页浏览结果: {result[:200]}...")
        
        # 检查结果中是否包含搜索提示
        if "该页面有搜索功能" in result:
            logger.info("成功检测到搜索提示")
            return True
        else:
            logger.warning("未检测到搜索提示")
            return False
    except Exception as e:
        logger.error(f"浏览器浏览功能测试失败: {str(e)}")
        return False
    finally:
        # 清理资源
        await browser_tool.cleanup()

async def main():
    """主函数"""
    logger.info("开始执行浏览器搜索功能测试")
    
    # 测试浏览器搜索功能
    search_result = await test_browser_search()
    
    # 测试浏览器浏览功能，检查是否提示搜索功能
    browse_result = await test_browser_browse_with_search_hint()
    
    # 输出测试结果
    logger.info("测试结果汇总:")
    logger.info(f"浏览器搜索功能测试: {'成功' if search_result else '失败'}")
    logger.info(f"浏览器浏览功能测试: {'成功' if browse_result else '失败'}")
    
    logger.info("测试完成")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 