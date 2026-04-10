#!/usr/bin/env python3
"""
认证管理器 - 移植自wx-robot-ilink的auth.ts

功能：
1. 二维码生成和显示（模仿qrcode-terminal）
2. 登录凭证管理
3. 凭证持久化存储
4. 登录状态轮询

参考：wx-robot-ilink/src/weixin/auth.ts
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Optional, Dict, Any

import aiohttp
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class WeChatCredentials:
    """微信登录凭证（对应wx-robot-ilink的LoginCredentials）"""
    account_id: str  # 账号ID
    user_id: str     # 用户ID  
    access_token: str  # 访问令牌
    refresh_token: str  # 刷新令牌
    base_url: str    # 服务器地址
    expires_at: float  # 过期时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeChatCredentials':
        return cls(**data)
    
    def is_expired(self) -> bool:
        """检查凭证是否过期"""
        return time.time() >= self.expires_at


class AuthManager:
    """
    认证管理器 - 完全模仿wx-robot-ilink的终端认证体验
    
    主要流程（参考 wx-robot-ilink）:
    1. fetchQRCode() - 获取二维码URL
    2. displayQRCode() - 在终端显示二维码
    3. pollQRStatus() - 轮询扫码状态
    4. saveCredentials() - 保存登录凭证
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化认证管理器
        
        Args:
            storage_path: 凭证存储路径，默认 ~/.hermes/wechat_credentials.json
        """
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            hermes_home = os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
            self.storage_path = Path(hermes_home) / "wechat_credentials.json"
        
        self.credentials: Optional[WeChatCredentials] = None
        
    def load_credentials(self) -> bool:
        """
        从本地文件加载凭证
        
        返回: True=加载成功，False=无凭证或凭证无效
        """
        try:
            if not self.storage_path.exists():
                logger.debug(f"凭证文件不存在: {self.storage_path}")
                return False
            
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.credentials = WeChatCredentials.from_dict(data)
            
            # 检查凭证是否过期
            if self.credentials.is_expired():
                logger.warning("凭证已过期")
                return False
            
            logger.info(f"凭证加载成功: account_id={self.credentials.account_id}")
            return True
            
        except Exception as e:
            logger.error(f"加载凭证失败: {e}")
            return False
    
    def save_credentials(self, credentials: WeChatCredentials) -> bool:
        """
        保存凭证到本地文件
        
        Args:
            credentials: 微信登录凭证
            
        返回: True=保存成功，False=保存失败
        """
        try:
            # 确保目录存在
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存凭证
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(credentials.to_dict(), f, indent=2, ensure_ascii=False)
            
            self.credentials = credentials
            logger.info(f"凭证保存成功: {self.storage_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存凭证失败: {e}")
            return False
    
    def clear_credentials(self) -> bool:
        """
        清除登录凭证（登出）
        
        返回: True=清除成功，False=清除失败
        """
        try:
            if self.storage_path.exists():
                self.storage_path.unlink()
                logger.info("凭证文件已删除")
            
            self.credentials = None
            return True
            
        except Exception as e:
            logger.error(f"清除凭证失败: {e}")
            return False
    
    def generate_qrcode_ascii(self, qr_url: str) -> str:
        """
        生成ASCII二维码（模仿qrcode-terminal输出）
        
        Args:
            qr_url: 二维码URL
            
        返回: ASCII格式的二维码字符串
        """
        try:
            import qrcode
            from qrcode.constants import ERROR_CORRECT_L
            
            # 生成二维码（类似qrcode-terminal的小尺寸）
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_L,
                box_size=2,
                border=1,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # 生成ASCII二维码
            ascii_lines = []
            for row in qr.modules:
                line = ""
                for cell in row:
                    line += "██" if cell else "  "
                ascii_lines.append(line)
            
            # 添加边框和注释（类似wx-robot-ilink）
            result_lines = []
            if len(ascii_lines) > 0:
                width = len(ascii_lines[0])
                result_lines.append("┌" + "─" * width + "┐")
                for line in ascii_lines:
                    result_lines.append("│" + line + "│")
                result_lines.append("└" + "─" * width + "┘")
            
            return "\n".join(result_lines)
            
        except ImportError:
            return f"ERROR: Need qrcode[pil] to display QR. URL: {qr_url}"
        except Exception as e:
            logger.error(f"生成二维码失败: {e}")
            return f"Error generating QR: {e}"
    
    def display_terminal_login(self, qr_url: str, qr_ascii: str):
        """
        在终端显示登录界面（模仿wx-robot-ilink的npm run dev体验）
        
        Args:
            qr_url: 二维码URL
            qr_ascii: ASCII二维码
        """
        print()
        print("=" * 60)
        print("WE CHAT LOGIN")
        print("=" * 60)
        print()
        print("请使用微信扫描以下二维码：")
        print()
        print(qr_ascii)
        print()
        print(f"备用链接: {qr_url}")
        print()
        print("请在5分钟内完成扫码...")
        print("=" * 60)
        print()
    
    async def fetch_qrcode(self, base_url: str = "https://ilinkai.weixin.qq.com") -> Dict[str, Any]:
        """
        获取二维码（模拟 - 真实实现需要调用iLink API）
        
        Args:
            base_url: 服务器地址
            
        返回: 二维码数据
        """
        # TODO: 实现真实API调用
        # url = f"{base_url}/ilink/bot/get_bot_qrcode?bot_type=3"
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url) as response:
        #         return await response.json()
        
        # 模拟返回
        qrcode_str = f"https://ilink.qrcode.tencent.com/auth/{int(time.time())}"
        return {
            "qrcode": qrcode_str,
            "expires_in": 300,
            "created_at": int(time.time())
        }
    
    async def poll_login_status(self, qrcode_str: str, base_url: str = "https://ilinkai.weixin.qq.com") -> Dict[str, Any]:
        """
        轮询登录状态（模拟 - 真实实现需要调用iLink API）
        
        Args:
            qrcode_str: 二维码字符串
            base_url: 服务器地址
            
        返回: 登录状态
        """
        # TODO: 实现真实API调用
        # url = f"{base_url}/ilink/bot/get_qrcode_status?qrcode={encodeURIComponent(qrcode_str)}"
        # headers = {"iLink-App-ClientVersion": "1"}
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url, headers=headers) as response:
        #         return await response.json()
        
        # 模拟返回
        await asyncio.sleep(3)  # 模拟网络请求
        
        # 模拟登录成功（实际应该根据扫码状态返回）
        return {
            "status": "logged_in",
            "account_id": f"wxid_{int(time.time())}",
            "user_id": f"user_{int(time.time())}",
            "access_token": f"token_{int(time.time())}",
            "refresh_token": f"refresh_{int(time.time())}",
            "expires_in": 86400
        }


# 全局认证管理器实例
_auth_manager = AuthManager()


def get_auth_manager() -> AuthManager:
    """获取全局认证管理器实例"""
    return _auth_manager


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 测试代码
    auth = AuthManager("/tmp/test_credentials.json")
    
    # 测试二维码生成
    print("测试二维码生成:")
    qr_ascii = auth.generate_qrcode_ascii("https://example.com/qrcode")
    if qr_ascii:
        print("✓ 二维码生成成功")
        print(qr_ascii)
    else:
        print("✗ 二维码生成失败")
    
    # 测试终端显示
    print("\n测试终端显示:")
    auth.display_terminal_login("https://example.com/qrcode", qr_ascii)
    
    # 测试凭证管理
    print("\n测试凭证管理:")
    import time
    creds = WeChatCredentials(
        account_id="wxid_test_123",
        user_id="user_123",
        access_token="test_token",
        refresh_token="test_refresh",
        base_url="https://ilinkai.weixin.qq.com",
        expires_at=time.time() + 3600
    )
    
    # 保存凭证
    if auth.save_credentials(creds):
        print("✓ 凭证保存成功")
    
    # 加载凭证
    if auth.load_credentials():
        print("✓ 凭证加载成功")
        print(f"  账号: {auth.credentials.account_id}")
    
    # 清除凭证
    if auth.clear_credentials():
        print("✓ 凭证清除成功")
    
    print("\n测试完成 ✅")