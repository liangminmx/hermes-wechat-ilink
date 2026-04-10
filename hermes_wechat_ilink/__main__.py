#!/usr/bin/env python3
"""
命令行入口点 - 类似wx-robot-ilink的独立运行方式

用法:
  python -m hermes_wechat_ilink [选项]
  
选项:
  --auth             启动认证流程（显示二维码）
  --send             发送消息
  --receive          接收消息
  --status           查看状态
  --logout           清除登录凭证
  --help             显示此帮助信息

示例:
  python -m hermes_wechat_ilink --auth
  python -m hermes_wechat_ilink --status
  python -m hermes_wechat_ilink --receive --timeout 30
  python -m hermes_wechat_ilink --send --to "wxid_xxx" --message "你好"
"""

import asyncio
import argparse
import sys
import os
from typing import Optional

from .wechat_client import WeChatILinkClient, AuthManager
from . import create_memory_provider

def print_banner():
    """打印欢迎信息"""
    print("=" * 60)
    print("Hermes WeChat iLink 插件 - 独立运行模式")
    print("=" * 60)
    print("基于 wx-robot-ilink 协议")
    print("GitHub: https://github.com/liangminmx/hermes-wechat-ilink")
    print()

def show_qr_code(qr_data: str) -> bool:
    """显示二维码（TODO: 实现二维码生成）"""
    try:
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L
        
        # 简单方案：终端显示
        print("=" * 60)
        print("微信登录二维码")
        print("=" * 60)
        print("请使用微信扫描以下二维码：")
        print()
        
        # 生成ASCII二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=2,
            border=2,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # 在终端显示
        qr.print_ascii()
        
        print()
        print("二维码将在5分钟后过期")
        print("扫码后请确认登录")
        print("=" * 60)
        return True
        
    except ImportError:
        print("错误: 需要安装二维码生成库")
        print("运行: pip install qrcode[pil]")
        return False

async def handle_auth(args) -> bool:
    """处理认证流程"""
    print("登录认证流程...")
    
    # TODO: 实现完整的认证流程
    # 基于wx-robot-ilink的auth.ts逻辑
    
    print("⚠️  完整认证流程开发中...")
    print("   如需使用，请通过 Hermes Agent:")
    print("   1. 启动 Hermes")
    print("   2. 执行 /wechat_auth")
    print("   3. 按提示扫码登录")
    
    return False

async def handle_status(args) -> bool:
    """查看状态"""
    # 使用插件本身的状态工具
    try:
        provider = create_memory_provider()
        result = await provider.call_tool("wechat_status")
        
        if isinstance(result, dict) and result.get("success"):
            status = result.get("status", {})
            print("=" * 60)
            print("插件状态")
            print("=" * 60)
            
            for key, value in status.items():
                if isinstance(value, bool):
                    display = "✓" if value else "✗"
                    print(f"{key:<20} {display}")
                else:
                    print(f"{key:<20} {value}")
            
            print("=" * 60)
            return True
        else:
            print("获取状态失败")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

async def handle_send(args) -> bool:
    """发送消息"""
    if not args.to or not args.message:
        print("错误: 需要 --to 和 --message 参数")
        return False
    
    print(f"发送消息给: {args.to}")
    print(f"消息内容: {args.message[:50]}...")
    
    # 使用插件工具发送
    try:
        provider = create_memory_provider()
        result = await provider.call_tool(
            "wechat_send_message",
            to_user_id=args.to,
            message=args.message,
            context_token=args.context
        )
        
        if isinstance(result, dict) and result.get("success"):
            print("✓ 消息发送成功")
            return True
        else:
            print("✗ 消息发送失败")
            print(f"错误: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

async def handle_receive(args) -> bool:
    """接收消息"""
    print("接收消息...")
    
    try:
        provider = create_memory_provider()
        result = await provider.call_tool(
            "wechat_get_messages",
            timeout=args.timeout,
            extract_text=True,
            only_unread=True
        )
        
        if isinstance(result, dict) and result.get("success"):
            messages = result.get("messages", [])
            count = result.get("count", 0)
            
            print("=" * 60)
            print(f"收到 {count} 条消息")
            print("=" * 60)
            
            if count > 0:
                for i, msg in enumerate(messages, 1):
                    print(f"\n消息 #{i}:")
                    print(f"  发件人: {msg.get('from_user_id')}")
                    print(f"  内容: {msg.get('text', '(非文本消息)')}")
                    print(f"  时间: {msg.get('received_at')}")
            else:
                print("暂无新消息")
            
            print("=" * 60)
            return True
        else:
            print("接收消息失败")
            return False
            
    except Exception as e:
        print(f"错误: {e}")
        return False

def handle_logout(args) -> bool:
    """清除登录凭证"""
    auth_manager = AuthManager()
    
    # 设置默认存储路径
    hermes_home = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
    creds_path = os.path.join(hermes_home, "wechat_credentials.json")
    auth_manager.storage_path = creds_path
    
    if auth_manager.clear_credentials():
        print("✓ 登录凭证已清除")
        return True
    else:
        print("✗ 清除凭证失败（可能不存在）")
        return True  # 认为成功，因为本来就没有凭证

def show_usage():
    """显示使用说明"""
    print_banner()
    print("使用方法:")
    print("  作为Hermes插件（推荐）:")
    print("    1. 将插件安装到Hermes的plugins/memory/目录")
    print("    2. 启动 Hermes Agent")
    print("    3. 使用 /wechat_auth, /wechat_send_message 等工具")
    print()
    print("  独立运行模式（用于测试）:")
    print("    运行: python -m hermes_wechat_ilink [选项]")
    print()
    print("选项:")
    print("  --auth             启动认证流程")
    print("  --send             发送消息（需要--to和--message）")
    print("  --receive          接收消息")
    print("  --status           查看插件状态")
    print("  --logout           清除登录凭证")
    print("  --to USER_ID       接收消息的用户ID")
    print("  --message TEXT     要发送的消息内容")
    print("  --context TOKEN    上下文令牌（可选）")
    print("  --timeout SECONDS  接收超时时间（默认30）")
    print("  --help             显示此帮助信息")
    print()
    print("示例:")
    print("  python -m hermes_wechat_ilink --auth")
    print("  python -m hermes_wechat_ilink --status")
    print("  python -m hermes_wechat_ilink --send --to wxid_xxx --message '你好'")
    print("  python -m hermes_wechat_ilink --receive --timeout 10")
    print("  python -m hermes_wechat_ilink --logout")
    print()

async def main_async():
    """主异步函数"""
    parser = argparse.ArgumentParser(description="Hermes WeChat iLink 插件")
    
    # 主要操作
    parser.add_argument("--auth", action="store_true", help="启动认证流程")
    parser.add_argument("--send", action="store_true", help="发送消息")
    parser.add_argument("--receive", action="store_true", help="接收消息")
    parser.add_argument("--status", action="store_true", help="查看插件状态")
    parser.add_argument("--logout", action="store_true", help="清除登录凭证")
    parser.add_argument("--install", action="store_true", help="安装到Hermes插件目录")
    
    # 参数
    parser.add_argument("--to", type=str, help="微信用户ID")
    parser.add_argument("--message", type=str, help="消息内容")
    parser.add_argument("--context", type=str, help="上下文令牌")
    parser.add_argument("--timeout", type=int, default=30, help="接收超时时间（秒）")
    
    args = parser.parse_args()
    
    # 如果没有指定操作，显示帮助
    if not any([args.auth, args.send, args.receive, args.status, args.logout, args.install]):
        show_usage()
        return 0
    
    # 执行相应操作
    success = True
    
    if args.logout:
        success = handle_logout(args)
    elif args.auth:
        success = await handle_auth(args)
    elif args.send:
        success = await handle_send(args)
    elif args.receive:
        success = await handle_receive(args)
    elif args.status:
        success = await handle_status(args)
    
    return 0 if success else 1

def main():
    """主函数"""
    try:
        return asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        return 130
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())