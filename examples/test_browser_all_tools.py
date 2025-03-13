#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试all_tools中的browser_use函数
"""

import asyncio
import logging
from react_agent.all_tools import browser_use

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_browser_use_search():
    """测试browser_use函数的搜索功能"""
    logger.info("开始测试browser_use函数的搜索功能")
    
    try:
        # 测试百度搜索
        logger.info("测试百度搜索")
        # 直接调用函数而不是工具
        result = await browser_use(
            url="https://www.baidu.com",
            task="在百度搜索Python教程",
            action="search",
            search_query="Python教程"
        )
        logger.info(f"百度搜索结果: {result[:200]}...")
        
        return True
    except Exception as e:
        logger.error(f"browser_use函数搜索功能测试失败: {str(e)}")
        return False

async def test_browser_use_browse():
    """测试browser_use函数的浏览功能"""
    logger.info("开始测试browser_use函数的浏览功能")
    
    try:
        # 浏览百度首页
        logger.info("浏览百度首页")
        # 直接调用函数而不是工具
        result = await browser_use(
            url="https://www.baidu.com",
            task="浏览百度首页",
            action="browse"
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
        logger.error(f"browser_use函数浏览功能测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    logger.info("开始执行browser_use函数测试")
    
    # 测试browser_use函数的搜索功能
    search_result = await test_browser_use_search()
    
    # 测试browser_use函数的浏览功能
    browse_result = await test_browser_use_browse()
    
    # 输出测试结果
    logger.info("测试结果汇总:")
    logger.info(f"browser_use函数搜索功能测试: {'成功' if search_result else '失败'}")
    logger.info(f"browser_use函数浏览功能测试: {'成功' if browse_result else '失败'}")
    
    logger.info("测试完成")

if __name__ == "__main__":
    # 运行测试
    asyncio.run(main()) 