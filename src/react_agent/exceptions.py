"""
定义项目中使用的异常类。
"""

class ToolError(Exception):
    """工具执行过程中发生的错误。"""
    pass


class AuthenticationError(Exception):
    """认证过程中发生的错误。"""
    pass


class ConfigurationError(Exception):
    """配置过程中发生的错误。"""
    pass


class ValidationError(Exception):
    """数据验证过程中发生的错误。"""
    pass


class APIError(Exception):
    """API调用过程中发生的错误。"""
    pass


class FileError(Exception):
    """文件操作过程中发生的错误。"""
    pass 