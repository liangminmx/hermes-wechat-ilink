#!/usr/bin/env python3
"""
认证管理器 - 移植自wx-robot-ilink的auth.ts

功能：
1. 登录凭证管理
2. 二维码生成
3. 登录状态轮询
4. 凭证持久化

与wx-robot-ilink的对应关系：
- src/weixin/auth.ts → auth_manager.py
"""

import json
import logging
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


@dataclass
class WeChatCredentials:
    """微信登录凭证（对应wx-robot-ilink的Credentials类型）"""
    account_id: str  # 微信账号ID
    user_id: str     # 登录用户ID
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
    认证管理器 - 处理微信登录相关操作
    
    主要功能（移植自wx-robot-ilink）：
    1. 生成登录二维码
    2. 轮询登录状态
    3. 保存/加载凭证
    4. 清除凭证
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
    
    def get_credentials(self) -> Optional[WeChatCredentials]:
        """
        获取当前凭证
        
        返回: 当前凭证对象，如未加载则返回None
        """
        return self.credentials
    
    def generate_qr_code(self, qr_url: str) -> Optional[str]:
        """
        生成二维码ASCII或文件
        
        Args:
            qr_url: 二维码对应的URL
            
        返回: 二维码路径或ASCII字符串
        """
        try:
            import qrcode
            from qrcode.constants import ERROR_CORRECT_L
            
            # 生成二维码
            qr = qrcode.QRCode(
                version=1,
                error_correction=ERROR_CORRECT_L,
                box_size=2,
                border=2,
            )
            qr.add_data(qr_url)
            qr.make(fit=True)
            
            # 创建ASCII二维码
            qr_ascii_lines = []
            for line in qr._modules:
                qr_ascii_lines.append(''.join(['██' if cell else '  ' for cell in line]))
            
            qr_ascii = '\n'.join(qr_ascii_lines)
            
            logger.info("二维码生成成功")
            return qr_ascii
            
        except ImportError:
            logger.error("需要安装二维码库: pip install qrcode[pil]")
            return None
        except Exception as e:
            logger.error(f"生成二维码失败: {e}")
            return None
    
    async def poll_login_status(self, poll_url: str, timeout: int = 300) -> Optional[WeChatCredentials]:
        """
        轮询登录状态（移植自wx-robot-ilink的登录轮询）
        
        Args:
            poll_url: 轮询状态URL
            timeout: 超时时间（秒）
            
        返回: 成功返回凭证，超时或失败返回None
        """
        import aiohttp
        import asyncio
        import time
        
        start_time = time.time()
        check_count = 0
        
        logger.info(f"开始轮询登录状态，超时: {timeout}s")
        
        try:
            # 尝试使用HTTP长轮询（类似wx-robot-ilink）
            async with aiohttp.ClientSession() as session:
                while time.time() - start_time < timeout:
                    check_count += 1
                    
                    try:
                        # 模拟登录状态检查
                        # TODO: 实现真正的iLink登录状态轮询
                        logger.debug(f"检查登录状态 (#{check_count})...")
                        
                        # 简单模拟：假设5次检查后"登录成功"
                        if check_count >= 5:
                            logger.info("模拟登录成功")
                            
                            # 返回模拟的凭证数据
                            return WeChatCredentials(
                                account_id=f"wxid_test_{int(time.time())}",
                                user_id=f"user_{int(time.time())}",
                                access_token=f"token_{int(time.time())}",
                                refresh_token=f"refresh_{int(time.time())}",
                                base_url="https://ilink.tencent.com",
                                expires_at=time.time() + 3600 * 24  # 24小时过期
                            )
                        
                        await asyncio.sleep(3)  # 等待3秒再次检查
                        
                    except asyncio.CancelledError:
                        logger.info("轮询被取消")
                        break
                    except Exception as e:
                        logger.warning(f"轮询出错: {e}")
                        await asyncio.sleep(5)
                
                logger.warning(f"登录超时 ({timeout}s)")
                return None
                
        except Exception as e:
            logger.error(f"轮询状态失败: {e}")
            return None


# 全局认证管理器实例
_auth_manager = AuthManager()


def get_auth_manager() -> AuthManager:
    """
    获取全局认证管理器实例
    
    返回: AuthManager实例
    """
    return _auth_manager


def ensure_auth_manager(storage_path: Optional[str] = None) -> AuthManager:
    """
    确保认证管理器已初始化
    
    Args:
        storage_path: 可选的存储路径
        
    返回: AuthManager实例
    """
    global _auth_manager
    
    if storage_path:
        _auth_manager = AuthManager(storage_path)
    elif _auth_manager is None:
        _auth_manager = AuthManager()
    
    return _auth_manager


# 测试代码
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # 测试认证管理器
    auth = AuthManager("/tmp/test_creds.json")
    
    # 测试清理凭证
    print("测试：清理凭证")
    auth.clear_credentials()
    
    # 测试加载不存在的凭证
    print("测试：加载凭证（应失败）")
    assert not auth.load_credentials()
    
    # 测试生成二维码
    print("测试：生成二维码")
    qr_ascii = auth.generate_qr_code("https://test.qrcode.com")
    if qr_ascii:
        print("✓ 二维码生成成功")
        print(qr_ascii[:100] + "..." if len(qr_ascii) > 100 else qr_ascii)
    else:
        print("✗ 二维码生成失败")
    
    print("测试完成")