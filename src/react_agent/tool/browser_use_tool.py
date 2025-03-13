import asyncio
import json
import logging
import os
import sys
from typing import Optional, Dict, Any, List, Union

from browser_use import Browser as BrowserUseBrowser
from browser_use import BrowserConfig
from browser_use.browser.context import BrowserContext
from browser_use.dom.service import DomService
from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from react_agent.tool.base import BaseTool, ToolResult

# 配置日志记录
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

_BROWSER_DESCRIPTION = """
Interact with a web browser to perform various actions such as navigation, element interaction,
content extraction, and tab management. Supported actions include:
- 'navigate': Go to a specific URL
- 'click': Click an element by index
- 'input_text': Input text into an element
- 'screenshot': Capture a screenshot
- 'get_html': Get page HTML content
- 'get_text': Get text content of the page
- 'read_links': Get all links on the page
- 'execute_js': Execute JavaScript code
- 'scroll': Scroll the page
- 'switch_tab': Switch to a specific tab
- 'new_tab': Open a new tab
- 'close_tab': Close the current tab
- 'refresh': Refresh the current page
- 'search': Search using the page's search functionality
"""


class BrowserUseTool(BaseTool):
    """浏览器工具。"""
    
    def __init__(self, **data):
        """初始化BrowserUseTool工具。"""
        super().__init__(
            name="browser_use",
            description="使用浏览器访问网页并执行任务。",
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "要访问的网页URL"
                    },
                    "task": {
                        "type": "string",
                        "description": "要执行的任务描述"
                    },
                    "action": {
                        "type": "string",
                        "description": "浏览器动作类型，如browse、click、fill、search等",
                        "default": "browse"
                    },
                    "search_query": {
                        "type": "string",
                        "description": "搜索查询词，用于search动作"
                    }
                },
                "required": ["url", "task"]
            },
            **data
        )
        # 不在初始化时调用异步方法，而是在第一次使用时检查
        self.playwright_checked = False
    
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)
    browser: Optional[BrowserUseBrowser] = Field(default=None, exclude=True)
    context: Optional[BrowserContext] = Field(default=None, exclude=True)
    dom_service: Optional[DomService] = Field(default=None, exclude=True)
    browser_initialized: bool = Field(default=False, exclude=True)
    initialization_error: Optional[str] = Field(default=None, exclude=True)
    initialization_attempts: int = Field(default=0, exclude=True)
    max_initialization_attempts: int = Field(default=3, exclude=True)
    playwright_checked: bool = Field(default=False, exclude=True)

    async def _ensure_playwright_installed_async(self):
        """异步方式确保Playwright已安装并下载浏览器。"""
        if self.playwright_checked:
            return
            
        try:
            # 使用子进程运行playwright install命令
            import subprocess
            import sys
            
            logger.info("检查Playwright浏览器是否已安装...")
            # 使用异步子进程运行命令
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "playwright", "install", "chromium",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                logger.info("Playwright浏览器已安装并可用")
            else:
                logger.warning(f"Playwright浏览器安装可能有问题: {stderr.decode()}")
            
            self.playwright_checked = True
        except Exception as e:
            logger.error(f"检查Playwright安装时出错: {str(e)}")
            self.playwright_checked = True  # 即使出错也标记为已检查，避免重复检查

    @field_validator("parameters", mode="before")
    def validate_parameters(cls, v: dict, info: ValidationInfo) -> dict:
        if not v:
            raise ValueError("Parameters cannot be empty")
        return v

    async def _ensure_browser_initialized(self) -> Optional[BrowserContext]:
        """确保浏览器和上下文已初始化。"""
        # 首先确保Playwright已安装
        await self._ensure_playwright_installed_async()
        
        if self.initialization_error and self.initialization_attempts >= self.max_initialization_attempts:
            logger.error(f"浏览器初始化失败次数过多: {self.initialization_error}")
            return None
            
        if not self.browser_initialized:
            self.initialization_attempts += 1
            try:
                logger.info(f"正在初始化浏览器 (尝试 {self.initialization_attempts}/{self.max_initialization_attempts})...")
                
                # 尝试不同的浏览器配置
                browser_configs = [
                    # 首先尝试无头模式
                    {"headless": True},
                    # 然后尝试有头模式
                    {"headless": False},
                    # 最后尝试无头模式但禁用GPU
                    {"headless": True, "args": ["--disable-gpu"]}
                ]
                
                last_error = None
                for config_dict in browser_configs:
                    try:
                        logger.info(f"尝试使用配置初始化浏览器: {config_dict}")
                        config = BrowserConfig(**config_dict)
                        self.browser = BrowserUseBrowser(config)
                        logger.info(f"成功初始化浏览器，配置: {config_dict}")
                        break
                    except Exception as e:
                        last_error = e
                        logger.warning(f"浏览器初始化失败，配置 {config_dict}: {str(e)}")
                        # 继续尝试下一个配置
                
                if not self.browser:
                    if last_error:
                        raise last_error
                    else:
                        raise Exception("所有浏览器配置都失败，但没有具体错误")
                
                # 创建上下文
                self.context = await self.browser.new_context()
                self.dom_service = DomService(await self.context.get_current_page())
                self.browser_initialized = True
                self.initialization_error = None
                logger.info("浏览器上下文初始化成功")
            except Exception as e:
                error_msg = f"浏览器初始化失败: {str(e)}"
                logger.error(error_msg)
                self.initialization_error = error_msg
                return None
        
        return self.context

    async def _find_search_input(self, context: BrowserContext) -> Optional[Dict[str, Any]]:
        """查找页面上的搜索输入框。"""
        try:
            # 尝试多种方式查找搜索框
            search_selectors = [
                # 百度特定
                "input#kw",
                "#kw",
                "input[name='wd']",
                # 常见搜索框选择器
                "input[type='search']",
                "input[name='q']",
                "input[name='query']",
                "input[name='search']",
                "input[name='keyword']",
                # 通用输入框
                "input[type='text']"
            ]
            
            for selector in search_selectors:
                logger.info(f"尝试查找搜索框: {selector}")
                
                # 使用简单的JavaScript查找元素
                js_code = """
                (function() {
                    var elements = document.querySelectorAll("%s");
                    if (elements.length > 0) {
                        var el = elements[0];
                        return {
                            index: 0,
                            id: el.id || "",
                            name: el.name || "",
                            type: el.type || "",
                            visible: true,
                            selector: "%s"
                        };
                    }
                    return null;
                })()
                """ % (selector, selector)
                
                element = await context.execute_javascript(js_code)
                
                if element:
                    logger.info(f"找到搜索框: {element}")
                    return element
            
            # 如果上面的方法都失败，尝试使用更通用的方法
            logger.info("尝试使用更通用的方法查找搜索框")
            js_code = """
            (function() {
                // 查找所有输入框
                var inputs = document.querySelectorAll('input');
                for (var i = 0; i < inputs.length; i++) {
                    var input = inputs[i];
                    // 检查是否可见
                    if (input.offsetWidth > 0 && input.offsetHeight > 0 && !input.disabled) {
                        return {
                            index: i,
                            id: input.id || "",
                            name: input.name || "",
                            type: input.type || "",
                            visible: true,
                            selector: "input"
                        };
                    }
                }
                return null;
            })()
            """
            
            element = await context.execute_javascript(js_code)
            if element:
                logger.info(f"使用通用方法找到搜索框: {element}")
                return element
            
            logger.warning("未找到搜索框")
            return None
        except Exception as e:
            logger.error(f"查找搜索框时出错: {str(e)}")
            return None

    async def _find_search_button(self, context: BrowserContext) -> Optional[Dict[str, Any]]:
        """查找页面上的搜索按钮。"""
        try:
            # 尝试多种方式查找搜索按钮
            button_selectors = [
                # 百度特定
                "input#su",
                "#su",
                # 常见搜索按钮选择器
                "button[type='submit']",
                "input[type='submit']",
                "button.search-btn",
                "button#search-button",
                "button.search"
            ]
            
            for selector in button_selectors:
                logger.info(f"尝试查找搜索按钮: {selector}")
                
                # 使用简单的JavaScript查找元素
                js_code = """
                (function() {
                    var elements = document.querySelectorAll("%s");
                    if (elements.length > 0) {
                        var el = elements[0];
                        return {
                            index: 0,
                            id: el.id || "",
                            type: el.type || "",
                            text: el.innerText || el.value || "",
                            visible: true,
                            selector: "%s"
                        };
                    }
                    return null;
                })()
                """ % (selector, selector)
                
                element = await context.execute_javascript(js_code)
                
                if element:
                    logger.info(f"找到搜索按钮: {element}")
                    return element
            
            # 如果上面的方法都失败，尝试查找表单并获取提交按钮
            logger.info("尝试查找表单的提交按钮")
            js_code = """
            (function() {
                // 查找所有表单
                var forms = document.querySelectorAll('form');
                for (var i = 0; i < forms.length; i++) {
                    var form = forms[i];
                    // 查找表单中的提交按钮
                    var submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                    if (submitButton && submitButton.offsetWidth > 0 && submitButton.offsetHeight > 0) {
                        return {
                            index: i,
                            id: submitButton.id || "",
                            type: submitButton.type || "",
                            text: submitButton.innerText || submitButton.value || "",
                            visible: true,
                            selector: "form button[type='submit'], form input[type='submit']"
                        };
                    }
                }
                return null;
            })()
            """
            
            element = await context.execute_javascript(js_code)
            if element:
                logger.info(f"在表单中找到提交按钮: {element}")
                return element
            
            logger.warning("未找到搜索按钮")
            return None
        except Exception as e:
            logger.error(f"查找搜索按钮时出错: {str(e)}")
            return None

    async def _perform_search(self, context: BrowserContext, query: str) -> str:
        """执行搜索操作。"""
        try:
            # 等待页面加载完成
            await asyncio.sleep(1)
            
            # 查找搜索框
            search_input = await self._find_search_input(context)
            if not search_input:
                return f"无法找到搜索框，无法执行搜索: {query}"
            
            # 输入搜索词
            selector = search_input.get("selector")
            logger.info(f"向搜索框 {selector} 输入: {query}")
            
            # 使用简单的JavaScript输入文本
            js_code = """
            (function() {
                var inputs = document.querySelectorAll("%s");
                if (inputs.length > 0) {
                    var input = inputs[0];
                    // 清空输入框
                    input.value = "";
                    // 设置新值
                    input.value = "%s";
                    // 触发事件
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                    return true;
                }
                return false;
            })()
            """ % (selector, query)
            
            input_result = await context.execute_javascript(js_code)
            if not input_result:
                return f"无法在搜索框中输入文本: {query}"
            
            # 查找搜索按钮
            search_button = await self._find_search_button(context)
            
            if search_button:
                # 点击搜索按钮
                selector = search_button.get("selector")
                logger.info(f"点击搜索按钮: {selector}")
                
                # 使用简单的JavaScript点击按钮
                js_code = """
                (function() {
                    var buttons = document.querySelectorAll("%s");
                    if (buttons.length > 0) {
                        buttons[0].click();
                        return true;
                    }
                    return false;
                })()
                """ % selector
                
                click_result = await context.execute_javascript(js_code)
                if not click_result:
                    logger.warning(f"无法点击搜索按钮: {selector}")
            else:
                # 如果没有找到搜索按钮，尝试提交表单
                logger.info("未找到搜索按钮，尝试提交表单")
                
                # 使用简单的JavaScript提交表单
                js_code = """
                (function() {
                    var inputs = document.querySelectorAll("%s");
                    if (inputs.length > 0) {
                        var form = inputs[0].closest('form');
                        if (form) {
                            form.submit();
                            return true;
                        } else {
                            // 模拟回车键
                            var event = new KeyboardEvent('keydown', {
                                key: 'Enter',
                                code: 'Enter',
                                keyCode: 13,
                                which: 13,
                                bubbles: true
                            });
                            inputs[0].dispatchEvent(event);
                            return true;
                        }
                    }
                    return false;
                })()
                """ % search_input.get("selector")
                
                submit_result = await context.execute_javascript(js_code)
                if not submit_result:
                    logger.warning("无法提交表单或模拟回车键")
            
            # 等待页面加载
            logger.info("等待搜索结果加载...")
            await asyncio.sleep(3)
            
            # 获取搜索结果
            title = await context.execute_javascript("document.title")
            content = await context.execute_javascript("document.body.innerText")
            
            return f"已执行搜索: {query}\n标题: {title}\n\n搜索结果:\n{content[:500]}..."
        except Exception as e:
            logger.error(f"执行搜索时出错: {str(e)}")
            return f"执行搜索 '{query}' 时出错: {str(e)}"

    async def execute(self, url: str, task: str, action: str = "browse", parameters: Optional[Dict[str, Any]] = None) -> str:
        """执行浏览器操作。"""
        if not url:
            return "需要提供URL才能执行浏览器操作"
        
        # 如果URL不是以http或https开头，添加https://
        if url and not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            logger.info(f"URL已修正为: {url}")
        
        # 初始化浏览器上下文
        context = await self._ensure_browser_initialized()
        if not context:
            return "浏览器初始化失败，无法执行操作"
        
        # 提取参数
        parameters = parameters or {}
        search_query = parameters.get("search_query")
        
        try:
            # 根据action执行不同操作
            # 默认操作：浏览网页
            if action == "browse" or not action:
                if not url:
                    return "需要提供URL才能浏览网页"
                
                logger.info(f"正在导航到URL: {url}")
                try:
                    await context.navigate_to(url)
                    logger.info(f"成功导航到: {url}")
                except Exception as e:
                    logger.error(f"导航到 {url} 失败: {str(e)}")
                    return f"无法访问网页 {url}: {str(e)}。请检查URL是否正确，或者尝试使用其他工具。"
                
                # 获取页面标题和内容摘要
                try:
                    title = await context.execute_javascript("document.title")
                    logger.info(f"获取到页面标题: {title}")
                except Exception as e:
                    logger.warning(f"获取页面标题失败: {str(e)}")
                    title = "无法获取标题"
                
                try:
                    content = await context.execute_javascript(
                        "Array.from(document.querySelectorAll('p')).slice(0, 5).map(p => p.textContent).join(' ')"
                    )
                    logger.info(f"获取到页面内容摘要，长度: {len(content) if content else 0}")
                except Exception as e:
                    logger.warning(f"获取页面内容摘要失败: {str(e)}")
                    content = "无法获取内容摘要"
                
                # 获取页面上的链接
                try:
                    links_js = """
                    Array.from(document.querySelectorAll('a[href]'))
                        .slice(0, 5)
                        .map(a => ({text: a.innerText.trim(), href: a.href}))
                        .filter(link => link.text)
                    """
                    links = await context.execute_javascript(links_js)
                    logger.info(f"获取到页面链接，数量: {len(links) if links else 0}")
                except Exception as e:
                    logger.warning(f"获取页面链接失败: {str(e)}")
                    links = []
                
                # 格式化结果
                result = f"已浏览网页: {url}\n标题: {title}\n\n内容摘要:\n{content[:300]}...\n\n"
                
                if links and isinstance(links, list):
                    result += "页面上的链接:\n"
                    for i, link in enumerate(links):
                        if isinstance(link, dict) and 'text' in link and 'href' in link:
                            result += f"{i+1}. {link['text']}: {link['href']}\n"
                
                # 检查页面是否有搜索框
                search_input = await self._find_search_input(context)
                if search_input:
                    result += "\n该页面有搜索功能，您可以使用 action='search' 和 parameters={'search_query': '您的搜索词'} 进行搜索。"
                
                return result
            
            # 搜索操作
            elif action == "search":
                if not search_query:
                    return "需要提供search_query参数才能执行搜索操作"
                
                # 先导航到URL
                logger.info(f"正在导航到URL: {url}")
                try:
                    await context.navigate_to(url)
                    logger.info(f"成功导航到: {url}")
                except Exception as e:
                    logger.error(f"导航到 {url} 失败: {str(e)}")
                    return f"无法访问网页 {url}: {str(e)}。请检查URL是否正确，或者尝试使用其他工具。"
                
                # 执行搜索
                result = await self._perform_search(context, search_query)
                return result
            
            # 点击操作
            elif action == "click":
                # 实现点击操作的代码
                return "点击操作尚未实现"
            
            # 填写表单操作
            elif action == "fill":
                # 实现填写表单操作的代码
                return "填写表单操作尚未实现"
            
            # 未知操作
            else:
                return f"未知的浏览器操作: {action}。支持的操作: browse, search, click, fill"
        
        except Exception as e:
            logger.error(f"执行浏览器操作时出错: {str(e)}")
            return f"执行浏览器操作时出错: {str(e)}"
        
        finally:
            # 确保资源被清理
            try:
                await context.close()
            except Exception as e:
                logger.error(f"关闭浏览器上下文时出错: {str(e)}")

    async def get_current_state(self) -> Dict[str, Any]:
        """获取当前浏览器状态。"""
        async with self.lock:
            try:
                context = await self._ensure_browser_initialized()
                if not context:
                    return {"error": "浏览器未初始化"}
                
                state = await context.get_state()
                state_info = {
                    "url": state.url,
                    "title": state.title,
                    "tabs": [tab.model_dump() for tab in state.tabs],
                    "interactive_elements": state.element_tree.clickable_elements_to_string(),
                }
                return state_info
            except Exception as e:
                logger.error(f"获取浏览器状态失败: {str(e)}")
                return {"error": f"获取浏览器状态失败: {str(e)}"}

    async def cleanup(self):
        """清理浏览器资源。"""
        async with self.lock:
            logger.info("正在清理浏览器资源...")
            if self.context is not None:
                try:
                    await self.context.close()
                except Exception as e:
                    logger.error(f"关闭浏览器上下文失败: {str(e)}")
                finally:
                    self.context = None
                    self.dom_service = None
            
            if self.browser is not None:
                try:
                    await self.browser.close()
                except Exception as e:
                    logger.error(f"关闭浏览器失败: {str(e)}")
                finally:
                    self.browser = None
            
            self.browser_initialized = False
            logger.info("浏览器资源清理完成")

    def __del__(self):
        """确保对象销毁时清理资源。"""
        if self.browser is not None or self.context is not None:
            try:
                asyncio.run(self.cleanup())
            except RuntimeError:
                try:
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(self.cleanup())
                    loop.close()
                except Exception as e:
                    logger.error(f"在析构函数中清理浏览器资源失败: {str(e)}")
