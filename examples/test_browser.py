import asyncio
import logging
import sys

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("browser_test")

# 导入浏览器工具
from react_agent.tool.browser_use_tool import BrowserUseTool
from react_agent.all_tools import TOOLS

async def test_browser_initialization():
    """测试浏览器初始化"""
    logger.info("=== 测试浏览器初始化 ===")
    browser_tool = BrowserUseTool()
    
    # 测试浏览器初始化
    context = await browser_tool._ensure_browser_initialized()
    if context:
        logger.info("✅ 浏览器初始化成功")
    else:
        logger.error("❌ 浏览器初始化失败")
    
    # 清理资源
    await browser_tool.cleanup()
    return context is not None

async def test_browser_navigation(url="https://www.baidu.com"):
    """测试浏览器导航功能"""
    logger.info(f"=== 测试浏览器导航到 {url} ===")
    browser_tool = BrowserUseTool()
    
    try:
        # 执行浏览操作
        result = await browser_tool.execute(url=url, task="访问网页", action="browse")
        logger.info(f"导航结果: {result[:100]}...")
        success = "无法" not in result and "失败" not in result
        if success:
            logger.info(f"✅ 成功导航到 {url}")
        else:
            logger.error(f"❌ 导航到 {url} 失败")
        
        # 清理资源
        await browser_tool.cleanup()
        return success
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        await browser_tool.cleanup()
        return False

async def test_browser_use_function(url="https://www.baidu.com"):
    """测试browser_use函数"""
    logger.info(f"=== 测试browser_use函数访问 {url} ===")
    
    try:
        # 直接使用BrowserUseTool实例
        browser_tool = BrowserUseTool()
        
        # 直接调用execute方法
        result = await browser_tool.execute(url=url, task="搜索信息")
        
        logger.info(f"函数结果: {result[:100]}...")
        success = "无法" not in result and "失败" not in result
        if success:
            logger.info(f"✅ browser_use函数成功访问 {url}")
        else:
            logger.error(f"❌ browser_use函数访问 {url} 失败")
            
        # 清理资源
        await browser_tool.cleanup()
        return success
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        return False

async def test_browser_actions():
    """测试浏览器的各种操作"""
    logger.info("=== 测试浏览器的各种操作 ===")
    browser_tool = BrowserUseTool()
    
    try:
        # 1. 导航到百度
        await browser_tool.execute(url="https://www.baidu.com", task="访问百度", action="browse")
        
        # 2. 获取页面文本
        text_result = await browser_tool.execute(
            url="https://www.baidu.com", 
            task="获取页面文本", 
            action="get_text"
        )
        logger.info(f"页面文本: {text_result[:100]}...")
        
        # 3. 获取页面链接
        links_result = await browser_tool.execute(
            url="https://www.baidu.com", 
            task="获取页面链接", 
            action="read_links"
        )
        logger.info(f"页面链接: {links_result[:100]}...")
        
        # 4. 执行JavaScript
        js_result = await browser_tool.execute(
            url="https://www.baidu.com", 
            task="获取页面标题", 
            action="execute_js",
            parameters={"script": "document.title"}
        )
        logger.info(f"JavaScript执行结果: {js_result}")
        
        # 清理资源
        await browser_tool.cleanup()
        logger.info("✅ 浏览器操作测试完成")
        return True
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        await browser_tool.cleanup()
        return False

async def run_all_tests():
    """运行所有测试"""
    logger.info("开始运行浏览器工具测试...")
    
    # 测试结果
    results = {
        "初始化测试": await test_browser_initialization(),
        "导航测试 (百度)": await test_browser_navigation("https://www.baidu.com"),
        "导航测试 (GitHub)": await test_browser_navigation("https://github.com"),
        "browser_use函数测试": await test_browser_use_function(),
        "浏览器操作测试": await test_browser_actions()
    }
    
    # 打印测试结果摘要
    logger.info("\n=== 测试结果摘要 ===")
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{test_name}: {status}")
    
    # 计算通过率
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    pass_rate = (passed / total) * 100
    logger.info(f"通过率: {pass_rate:.1f}% ({passed}/{total})")
    
    return results

if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_all_tests())
