"""
WeChat iLink API Client for Hermes - based on wx-robot-ilink protocol.

This module implements the WeChat iLink protocol to communicate with WeChat
via Tencent's official OpenClaw gateway.

Protocol endpoints:
- POST /ilink/bot/getupdates   - Long polling for new messages
- POST /ilink/bot/sendmessage  - Send message to user

Based on: https://github.com/co-pine/wx-robot-ilink
"""

import asyncio
import aiohttp
import base64
import hashlib
import json
import logging
import secrets
import time
from typing import Dict, List, Optional, Any, Union
from enum import IntEnum

logger = logging.getLogger(__name__)


class MessageType(IntEnum):
    """Message types in WeChat iLink protocol."""
    USER = 1      # Message from user
    BOT = 2       # Message from bot


class MessageItemType(IntEnum):
    """Message item types."""
    TEXT = 1
    IMAGE = 2
    VOICE = 3
    FILE = 4
    VIDEO = 5


class MessageState(IntEnum):
    """Message states."""
    NEW = 0
    GENERATING = 1
    FINISH = 2


# Type definitions
class TextItem:
    """Text message item."""
    def __init__(self, text: str = ""):
        self.text = text
    
    def to_dict(self) -> Dict[str, Any]:
        return {"text": self.text}


class MessageItem:
    """Message content item."""
    def __init__(self, item_type: MessageItemType = MessageItemType.TEXT, 
                 text: Optional[str] = None):
        self.type = item_type
        self.text_item = TextItem(text) if text else None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {"type": self.type}
        if self.text_item:
            result["text_item"] = self.text_item.to_dict()
        return result


class WeixinMessage:
    """WeChat message structure."""
    def __init__(self, 
                 from_user_id: str = "",
                 to_user_id: str = "",
                 message_type: MessageType = MessageType.USER,
                 message_state: MessageState = MessageState.NEW,
                 items: Optional[List[MessageItem]] = None,
                 context_token: Optional[str] = None):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.message_type = message_type
        self.message_state = message_state
        self.item_list = items or []
        self.context_token = context_token
        self.client_id = f"bot-{int(time.time() * 1000)}-{secrets.token_hex(4)}"
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "client_id": self.client_id,
            "message_type": self.message_type,
            "message_state": self.message_state,
        }
        
        if self.item_list:
            result["item_list"] = [item.to_dict() for item in self.item_list]
        
        if self.context_token:
            result["context_token"] = self.context_token
        
        return result


class GetUpdatesResponse:
    """Response from getUpdates endpoint."""
    def __init__(self, 
                 ret: int = 0,
                 errcode: Optional[int] = None,
                 errmsg: Optional[str] = None,
                 msgs: Optional[List[Dict[str, Any]]] = None,
                 get_updates_buf: Optional[str] = None):
        self.ret = ret
        self.errcode = errcode
        self.errmsg = errmsg
        self.msgs = msgs or []
        self.get_updates_buf = get_updates_buf
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GetUpdatesResponse":
        return cls(
            ret=data.get("ret", 0),
            errcode=data.get("errcode"),
            errmsg=data.get("errmsg"),
            msgs=data.get("msgs", []),
            get_updates_buf=data.get("get_updates_buf")
        )
    
    @property
    def success(self) -> bool:
        return self.ret == 0
    
    @property
    def has_messages(self) -> bool:
        return bool(self.msgs)


class AuthCredentials:
    """Authentication credentials for WeChat."""
    def __init__(self, 
                 token: str,
                 base_url: str,
                 account_id: str,
                 user_id: Optional[str] = None):
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.account_id = account_id
        self.user_id = user_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "base_url": self.base_url,
            "account_id": self.account_id,
            "user_id": self.user_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AuthCredentials":
        return cls(
            token=data["token"],
            base_url=data["base_url"],
            account_id=data["account_id"],
            user_id=data.get("user_id")
        )


class WeChatILinkClient:
    """Main client for WeChat iLink API."""
    
    DEFAULT_TIMEOUT = 15.0
    LONG_POLL_TIMEOUT = 35.0
    
    def __init__(self, credentials: Optional[AuthCredentials] = None):
        self.credentials = credentials
        self.session: Optional[aiohttp.ClientSession] = None
        self._random_uin = None
    
    def _random_wechat_uin(self) -> str:
        """Generate random X-WECHAT-UIN header value."""
        if not self._random_uin:
            random_bytes = secrets.token_bytes(4)
            random_int = int.from_bytes(random_bytes[:4], 'big')
            self._random_uin = base64.b64encode(str(random_int).encode()).decode()
        return self._random_uin
    
    def _build_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Build request headers for iLink API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization-Type": "ilink_bot_token",
            "X-WECHAT-UIN": self._random_wechat_uin(),
        }
        
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    async def _request(self, 
                      endpoint: str, 
                      data: Dict[str, Any],
                      timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
        """Make HTTP request to iLink API."""
        if not self.credentials:
            raise ValueError("Credentials not set")
        
        url = f"{self.credentials.base_url}/{endpoint.lstrip('/')}"
        
        headers = self._build_headers(self.credentials.token)
        body = json.dumps(data).encode("utf-8")
        headers["Content-Length"] = str(len(body))
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    headers=headers,
                    data=body,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        logger.error(f"API request failed: {response.status} - {response_text}")
                        raise Exception(f"HTTP {response.status}: {response_text}")
                    
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON response: {response_text}")
                        raise Exception(f"Invalid JSON response")
                        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {timeout}s")
            raise
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    async def get_updates(self, 
                         get_updates_buf: str = "",
                         timeout: float = LONG_POLL_TIMEOUT) -> GetUpdatesResponse:
        """
        Long polling for new messages.
        
        Args:
            get_updates_buf: Continuation buffer from previous request
            timeout: Long polling timeout in seconds
            
        Returns:
            GetUpdatesResponse containing new messages
        """
        try:
            response_data = await self._request(
                "ilink/bot/getupdates",
                {"get_updates_buf": get_updates_buf},
                timeout=timeout
            )
            return GetUpdatesResponse.from_dict(response_data)
            
        except asyncio.TimeoutError:
            # Long polling timeout is normal
            return GetUpdatesResponse(get_updates_buf=get_updates_buf)
        except Exception as e:
            logger.error(f"getUpdates failed: {e}")
            return GetUpdatesResponse(ret=-1, errmsg=str(e))
    
    async def send_text_message(self, 
                               to_user_id: str, 
                               text: str,
                               context_token: Optional[str] = None) -> bool:
        """
        Send text message to a user.
        
        Args:
            to_user_id: Target user ID
            text: Message text
            context_token: Context token for conversation
            
        Returns:
            True if successful
        """
        try:
            items = []
            if text:
                items.append(MessageItem(MessageItemType.TEXT, text))
            
            message = WeixinMessage(
                from_user_id="",
                to_user_id=to_user_id,
                message_type=MessageType.BOT,
                message_state=MessageState.FINISH,
                items=items,
                context_token=context_token
            )
            
            await self._request(
                "ilink/bot/sendmessage",
                {"msg": message.to_dict()}
            )
            
            logger.info(f"Sent message to {to_user_id}: {text[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"send_message failed: {e}")
            return False
    
    @staticmethod
    def extract_text_from_message(msg_data: Dict[str, Any]) -> str:
        """Extract text content from WeChat message."""
        items = msg_data.get("item_list", [])
        if not items:
            return ""
        
        for item in items:
            if item.get("type") == MessageItemType.TEXT and item.get("text_item", {}).get("text"):
                text = item["text_item"]["text"]
                ref = item.get("ref_msg")
                
                if not ref:
                    return text
                
                parts = []
                if ref.get("title"):
                    parts.append(ref["title"])
                
                if parts:
                    return f"[引用: {' | '.join(parts)}]\n{text}"
                else:
                    return text
        
        return ""
    
    @staticmethod
    def is_user_message(msg_data: Dict[str, Any]) -> bool:
        """Check if message is from a user."""
        return msg_data.get("message_type") == MessageType.USER
    
    @staticmethod
    def get_sender_id(msg_data: Dict[str, Any]) -> Optional[str]:
        """Get sender user ID from message."""
        return msg_data.get("from_user_id")


class AuthManager:
    """Manage authentication and QR code login."""
    
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.credentials: Optional[AuthCredentials] = None
    
    def load_credentials(self) -> bool:
        """Load credentials from storage."""
        if not self.storage_path:
            return False
        
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.credentials = AuthCredentials.from_dict(data)
                logger.info(f"Loaded credentials for account: {self.credentials.account_id}")
                return True
        except FileNotFoundError:
            logger.info("No saved credentials found")
            return False
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            return False
    
    def save_credentials(self) -> bool:
        """Save credentials to storage."""
        if not self.credentials or not self.storage_path:
            return False
        
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.credentials.to_dict(), f, indent=2)
            logger.info(f"Saved credentials for account: {self.credentials.account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
            return False
    
    def clear_credentials(self) -> bool:
        """Clear stored credentials."""
        if not self.storage_path:
            return False
        
        try:
            if os.path.exists(self.storage_path):
                os.remove(self.storage_path)
                self.credentials = None
                logger.info("Cleared credentials")
                return True
        except Exception as e:
            logger.error(f"Failed to clear credentials: {e}")
        
        return False
    
    # Note: QR code login implementation would require web UI interaction
    # In a full implementation, this would:
    # 1. Request QR code from iLink API
    # 2. Display QR for user to scan
    # 3. Poll for authentication status
    # 4. Save credentials