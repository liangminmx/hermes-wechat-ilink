"""
Hermes WeChat iLink Plugin
A Hermes Agent plugin for direct WeChat integration via Tencent's official iLink API.

This is the main package entry point. The actual plugin implementation is in the 
hermes_wechat_ilink sub-package.
"""

# Version
__version__ = "0.1.0"

# Export the create_memory_provider function
from hermes_wechat_ilink import create_memory_provider

__all__ = ["create_memory_provider", "__version__"]