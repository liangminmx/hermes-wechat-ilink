"""
WeChat iLink Plugin for Hermes - Pure Python implementation of wx-robot-ilink.

This plugin provides direct WeChat integration using Tencent's official iLink API.
No need for webhook bridges or third-party services - connects directly to WeChat.

Based on the architecture of: https://github.com/co-pine/wx-robot-ilink
Implements protocol: https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin

Features:
- Direct WeChat messaging via official Tencent API
- Long polling for real-time message reception
- Context-aware conversations with users
- Persistence of authentication state
- Hermes tool integration

Usage:
1. Call `wechat_auth` to authenticate with QR code
2. Use `wechat_send_message` to send messages
3. Use `wechat_get_messages` to poll for new messages
4. Use `wechat_webhook_server` to expose a webhook interface
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Set
from contextlib import asynccontextmanager

from agent.memory_provider import MemoryProvider
from tools.registry import tool_error

# Import our WeChat client
from .wechat_client import (
    WeChatILinkClient,
    AuthCredentials,
    AuthManager,
    GetUpdatesResponse,
    MessageType,
    MessageItemType,
    MessageState,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool schemas for Hermes integration
# ---------------------------------------------------------------------------

WECHAT_AUTH_SCHEMA = {
    "name": "wechat_auth",
    "description": (
        "Authenticate with WeChat using QR code. "
        "This provides a QR code that you scan with WeChat to log in. "
        "Once authenticated, you can send and receive messages directly through WeChat."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "server_url": {
                "type": "string",
                "description": "WeChat iLink server URL (default: discovered automatically)",
            },
            "qr_only": {
                "type": "boolean",
                "description": "Only show QR code, don't start background polling",
                "default": False,
            },
        },
        "required": [],
    },
}

WECHAT_SEND_MESSAGE_SCHEMA = {
    "name": "wechat_send_message",
    "description": (
        "Send a message directly to a WeChat user. "
        "Requires previous authentication with wechat_auth. "
        "Messages are sent through Tencent's official iLink API."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "to_user_id": {
                "type": "string",
                "description": "WeChat user ID to send message to",
            },
            "message": {
                "type": "string",
                "description": "Message text to send",
            },
            "context_token": {
                "type": "string",
                "description": "Optional context token for conversation tracking",
            },
        },
        "required": ["to_user_id", "message"],
    },
}

WECHAT_GET_MESSAGES_SCHEMA = {
    "name": "wechat_get_messages",
    "description": (
        "Get new messages from WeChat. "
        "Uses long-polling to wait for new messages from authenticated WeChat account. "
        "Returns both raw message data and extracted text content."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "timeout": {
                "type": "integer",
                "description": "Long polling timeout in seconds (default: 30)",
                "default": 30,
            },
            "extract_text": {
                "type": "boolean",
                "description": "Extract text content from messages (default: true)",
                "default": True,
            },
            "only_unread": {
                "type": "boolean",
                "description": "Only return unread messages (default: true)",
                "default": True,
            },
        },
        "required": [],
    },
}

WECHAT_STATUS_SCHEMA = {
    "name": "wechat_status",
    "description": (
        "Get current WeChat plugin status. "
        "Shows authentication status, connection health, and recent activity."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

WECHAT_WEBHOOK_SERVER_SCHEMA = {
    "name": "wechat_webhook_server",
    "description": (
        "Start a webhook server that forwards messages between Hermes and WeChat. "
        "Provides HTTP endpoints similar to ClawBot for external integration. "
        "Once running, messages from WeChat are forwarded to Hermes for processing."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "port": {
                "type": "integer",
                "description": "Port to run the server on (default: 8080)",
                "default": 8080,
            },
            "host": {
                "type": "string",
                "description": "Host interface to bind to (default: 0.0.0.0)",
                "default": "0.0.0.0",
            },
            "webhook_path": {
                "type": "string",
                "description": "Path for receiving webhook messages (default: /wechat/webhook)",
                "default": "/wechat/webhook",
            },
        },
        "required": [],
    },
}

ALL_TOOL_SCHEMAS = [
    WECHAT_AUTH_SCHEMA,
    WECHAT_SEND_MESSAGE_SCHEMA,
    WECHAT_GET_MESSAGES_SCHEMA,
    WECHAT_STATUS_SCHEMA,
    WECHAT_WEBHOOK_SERVER_SCHEMA,
]

# ---------------------------------------------------------------------------
# Message queue for incoming WeChat messages
# ---------------------------------------------------------------------------

class WeChatMessageQueue:
    """Thread-safe queue for storing incoming WeChat messages."""
    
    def __init__(self, max_size: int = 1000):
        self.messages: List[Dict[str, Any]] = []
        self.max_size = max_size
        self.lock = threading.Lock()
        self.condition = threading.Condition()
        self.context_tokens: Dict[str, str] = {}  # user_id -> context_token
    
    def add_message(self, msg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new message to the queue."""
        with self.lock:
            # Add timestamp and ID
            msg = {
                **msg_data,
                "received_at": time.time(),
                "id": len(self.messages) + 1,
                "processed": False,
            }
            
            self.messages.append(msg)
            
            # Keep queue size limited
            if len(self.messages) > self.max_size:
                self.messages = self.messages[-self.max_size:]
            
            # Store context token if available
            user_id = msg.get("from_user_id")
            context_token = msg.get("context_token")
            if user_id and context_token:
                self.context_tokens[user_id] = context_token
        
        # Notify waiting threads
        with self.condition:
            self.condition.notify_all()
        
        logger.debug(f"Added WeChat message from {user_id}")
        return msg
    
    def get_messages(self, unread_only: bool = True, limit: int = 100) -> List[Dict[str, Any]]:
        """Get messages from the queue."""
        with self.lock:
            if unread_only:
                messages = [m for m in self.messages if not m.get("processed")]
            else:
                messages = self.messages.copy()
            
            messages = messages[-limit:]  # Most recent first
            
            # Mark as processed
            if unread_only:
                for msg in messages:
                    msg["processed"] = True
            
            return messages
    
    def wait_for_messages(self, timeout: float = 30.0) -> List[Dict[str, Any]]:
        """Wait for new messages with timeout."""
        with self.condition:
            # Check if there are already unread messages
            unread = self.get_messages(unread_only=True)
            if unread:
                return unread
            
            # Wait for new messages
            self.condition.wait(timeout)
            return self.get_messages(unread_only=True)
    
    def get_context_token(self, user_id: str) -> Optional[str]:
        """Get saved context token for a user."""
        with self.lock:
            return self.context_tokens.get(user_id)
    
    def clear_messages(self):
        """Clear all messages from the queue."""
        with self.lock:
            self.messages = []


# ---------------------------------------------------------------------------
# Main WeChat iLink Plugin
# ---------------------------------------------------------------------------

class WeChatILinkPlugin:
    """Main WeChat iLink plugin for Hermes."""
    
    def __init__(self):
        self.message_queue = WeChatMessageQueue()
        self.client: Optional[WeChatILinkClient] = None
        self.auth_manager = AuthManager()
        self.polling_task: Optional[asyncio.Task] = None
        self.polling_running = False
        self.pending_messages: Dict[str, List[str]] = {}
        
        # Load saved credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load saved authentication credentials."""
        # Set storage path
        hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
        creds_path = os.path.join(hermes_home, "wechat_credentials.json")
        self.auth_manager.storage_path = creds_path
        
        if self.auth_manager.load_credentials():
            self.client = WeChatILinkClient(self.auth_manager.credentials)
            logger.info(f"Loaded WeChat credentials for account: {self.auth_manager.credentials.account_id}")
    
    def _save_credentials(self):
        """Save authentication credentials."""
        self.auth_manager.save_credentials()
    
    def _start_polling(self):
        """Start background polling for WeChat messages."""
        if self.polling_running:
            return
        
        if not self.client:
            logger.error("Cannot start polling: not authenticated")
            return
        
        self.polling_running = True
        self.polling_task = asyncio.create_task(self._poll_messages())
        logger.info("Started WeChat message polling")
    
    def _stop_polling(self):
        """Stop background polling."""
        self.polling_running = False
        if self.polling_task:
            self.polling_task.cancel()
            self.polling_task = None
        logger.info("Stopped WeChat message polling")
    
    async def _poll_messages(self):
        """Background task to poll for new WeChat messages."""
        get_updates_buf = ""
        
        while self.polling_running and self.client:
            try:
                response = await self.client.get_updates(
                    get_updates_buf=get_updates_buf,
                    timeout=30.0
                )
                
                if response.success:
                    # Update continuation buffer
                    if response.get_updates_buf:
                        get_updates_buf = response.get_updates_buf
                    
                    # Process new messages
                    for msg_data in response.msgs or []:
                        if self.client.is_user_message(msg_data):
                            self.message_queue.add_message(msg_data)
                            user_id = self.client.get_sender_id(msg_data)
                            text = self.client.extract_text_from_message(msg_data)
                            if user_id and text:
                                logger.info(f"Received message from {user_id}: {text[:100]}")
                else:
                    logger.error(f"getUpdates failed: {response.errcode} - {response.errmsg}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in poll_messages: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    # -----------------------------------------------------------------------
    # Tool handlers (called by Hermes)
    # -----------------------------------------------------------------------
    
    def tool_wechat_auth(self, server_url: str = None, qr_only: bool = False) -> dict:
        """Authenticate with WeChat via QR code."""
        try:
            # TODO: Implement full QR code authentication flow
            # This requires:
            # 1. Requesting QR code from iLink API
            # 2. Displaying QR for user to scan (console or web)
            # 3. Polling for authentication status
            # 4. Saving credentials
            
            # For now, return a placeholder
            result = {
                "status": "pending_implementation",
                "message": "Full QR code authentication not yet implemented.",
                "implementation_notes": [
                    "Based on wx-robot-ilink auth.ts",
                    "Requires: QR code display and status polling",
                    "Will save token, base_url, account_id",
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in wechat_auth: {e}")
            return tool_error(f"Authentication failed: {str(e)}")
    
    def tool_wechat_send_message(self, to_user_id: str, message: str, context_token: str = None) -> dict:
        """Send a message to a WeChat user."""
        try:
            if not self.client:
                return tool_error("Not authenticated. Please run wechat_auth first.")
            
            # Get context token from saved state if not provided
            if not context_token:
                context_token = self.message_queue.get_context_token(to_user_id)
            
            # Send message
            success = asyncio.run(self.client.send_text_message(
                to_user_id=to_user_id,
                text=message,
                context_token=context_token
            ))
            
            if success:
                return {
                    "success": True,
                    "to_user_id": to_user_id,
                    "sent_at": time.time(),
                    "message_preview": message[:100] + ("..." if len(message) > 100 else ""),
                }
            else:
                return tool_error("Failed to send message")
                
        except Exception as e:
            logger.error(f"Error in wechat_send_message: {e}")
            return tool_error(f"Failed to send message: {str(e)}")
    
    def tool_wechat_get_messages(self, timeout: int = 30, extract_text: bool = True, only_unread: bool = True) -> dict:
        """Get new messages from WeChat."""
        try:
            messages = self.message_queue.wait_for_messages(timeout=timeout)
            
            if not messages:
                return {
                    "success": True,
                    "messages": [],
                    "count": 0,
                    "timestamp": time.time(),
                }
            
            # Process messages
            processed_messages = []
            for msg in messages:
                processed = {
                    "id": msg.get("id"),
                    "from_user_id": msg.get("from_user_id"),
                    "message_id": msg.get("message_id"),
                    "received_at": msg.get("received_at"),
                }
                
                if extract_text:
                    processed["text"] = self.client.extract_text_from_message(msg) if self.client else ""
                
                processed_messages.append(processed)
            
            return {
                "success": True,
                "messages": processed_messages,
                "count": len(processed_messages),
                "timestamp": time.time(),
            }
            
        except Exception as e:
            logger.error(f"Error in wechat_get_messages: {e}")
            return tool_error(f"Failed to get messages: {str(e)}")
    
    def tool_wechat_status(self) -> dict:
        """Get current plugin status."""
        try:
            status = {
                "authenticated": bool(self.client),
                "polling_active": self.polling_running,
                "queue_size": len(self.message_queue.get_messages(unread_only=False)),
                "unread_messages": len(self.message_queue.get_messages(unread_only=True)),
                "timestamp": time.time(),
            }
            
            if self.client and self.auth_manager.credentials:
                status.update({
                    "account_id": self.auth_manager.credentials.account_id,
                    "base_url": self.auth_manager.credentials.base_url,
                    "user_id": self.auth_manager.credentials.user_id,
                })
            
            return {
                "success": True,
                "status": status,
            }
            
        except Exception as e:
            logger.error(f"Error in wechat_status: {e}")
            return tool_error(f"Failed to get status: {str(e)}")
    
    def tool_wechat_webhook_server(self, port: int = 8080, host: str = "0.0.0.0", webhook_path: str = "/wechat/webhook") -> dict:
        """Start a webhook server for external integration."""
        try:
            # TODO: Implement FastAPI webhook server similar to webhook-bridge plugin
            # but tailored for WeChat integration
            
            result = {
                "status": "planned_feature",
                "message": "Webhook server implementation coming soon.",
                "planned_features": [
                    f"HTTP server on {host}:{port}",
                    f"Webhook endpoint: {webhook_path}",
                    "ClawBot-compatible endpoints",
                    "Real-time message forwarding to Hermes",
                ]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in wechat_webhook_server: {e}")
            return tool_error(f"Failed to start webhook server: {str(e)}")


# ---------------------------------------------------------------------------
# MemoryProvider wrapper for plugin discovery
# ---------------------------------------------------------------------------

class WeChatILinkMemoryProvider(MemoryProvider):
    """MemoryProvider wrapper for WeChatILinkPlugin."""
    
    def __init__(self):
        self.plugin = WeChatILinkPlugin()
        self.tool_map = {
            "wechat_auth": self.plugin.tool_wechat_auth,
            "wechat_send_message": self.plugin.tool_wechat_send_message,
            "wechat_get_messages": self.plugin.tool_wechat_get_messages,
            "wechat_status": self.plugin.tool_wechat_status,
            "wechat_webhook_server": self.plugin.tool_wechat_webhook_server,
        }
    
    def get_tool_schemas(self) -> List[dict]:
        """Return tool schemas for this provider."""
        return ALL_TOOL_SCHEMAS
    
    async def call_tool(self, tool_name: str, **kwargs) -> dict:
        """Call a tool by name."""
        if tool_name in self.tool_map:
            return self.tool_map[tool_name](**kwargs)
        else:
            return tool_error(f"Unknown tool: {tool_name}")
    
    async def get_memory_context(self, query: str = None) -> str:
        """Get memory context for injection into prompts."""
        if not self.plugin.client:
            return "WeChat plugin: Not authenticated. Use wechat_auth to log in."
        
        unread = self.plugin.message_queue.get_messages(limit=3)
        
        if not unread:
            return "WeChat plugin: Authenticated, no recent messages."
        
        lines = ["WeChat plugin: Recent messages:"]
        for msg in unread[-3:]:
            user_id = msg.get("from_user_id", "unknown")
            text = self.plugin.client.extract_text_from_message(msg) if self.plugin.client else ""
            preview = text[:50] + ("..." if len(text) > 50 else "")
            lines.append(f"- {user_id}: {preview}")
        
        return "\n".join(lines)


# Factory function for plugin discovery
def create_memory_provider(config: dict = None) -> MemoryProvider:
    """Create a WeChatILinkMemoryProvider instance."""
    return WeChatILinkMemoryProvider()