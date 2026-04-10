#!/usr/bin/env python3
"""
基本使用示例 - 展示如何直接使用微信iLink客户端
类似wx-robot-ilink的独立使用方式

使用方法:
1. python examples/basic_usage.py --auth       # 登录认证
2. python examples/basic_usage.py --send       # 发送消息
3. python examples/basic_usage.py --receive    # 接收消息
"""

import asyncio
import argparse
import sys
import os

# 添加插件路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hermes_wechat_ilink.wechat_client import (
    WeChatILinkClient,
    AuthManager,
    WeChatMessage
)

async def authenticate():
    """认证流程示例"""
    print("=== 微信认证流程 ===")
    print("1. 进行微信扫码认证...")
    
    auth_manager = AuthManager()
    
    # 检查是否已有凭证
    if auth_manager.load_credentials():
        print(f"✓ 已加载认证凭证")
        print(f"   账户ID: {auth_manager.credentials.account_id}")
        print(f"   用户ID: {auth_manager.credentials.user_id}")
        print(f"   服务器: {auth_manager.credentials.base_url}")
        return auth_manager.credentials
    
    # 无凭证，需要认证
    print("! 未找到认证凭证，需要重新登录")
    
    # TODO: 这里应该实现二维码生成和扫码登录
    # 基于wx-robot-ilink的auth.ts实现
    
    print("生成二维码并扫码登录的功能开发中...")
    print("请先通过 Hermes 执行 /wechat_auth 完成认证")
    
    return None

async def send_message(client, to_user_id, message):
    """发送消息示例"""
    print(f"=== 发送消息给: {to_user_id} ===")
    print(f"消息内容: {message}")
    
    success = await client.send_text_message(
        to_user_id=to_user_id,
        text=message,
        context_token=None
    )
    
    if success:
        print("✓ 消息发送成功")
        return True
    else:
        print("✗ 消息发送失败")
        return False

async def receive_messages(client, timeout=30):
    """接收消息示例"""
    print(f"=== 接收消息 (超时: {timeout}s) ===")
    
    get_updates_buf = ""
    print("开始轮询消息...")
    
    try:
        response = await client.get_updates(
            get_updates_buf=get_updates_buf,
            timeout=timeout
        )
        
        if response.success and response.msgs:
            print(f"✓ 收到 {len(response.msgs)} 条消息")
            for i, msg in enumerate(response.msgs):
                sender = client.get_sender_id(msg)
                text = client.extract_text_from_message(msg)
                timestamp = msg.get("timestamp", 0)
                
                print(f"\n消息 #{i+1}:")
                print(f"  发件人: {sender}")
                print(f"  内容: {text}")
                print(f"  时间: {timestamp}")
                
                # 解析消息类型
                if msg.get("content_type") == 1:
                    print(f"  类型: 文本消息")
                elif msg.get("content_type") == 2:
                    print(f"  类型: 图片消息")
                elif msg.get("content_type") == 3:
                    print(f"  类型: 语音消息")
        else:
            print("! 未收到新消息")
            
        # 更新缓冲区
        if response.get_updates_buf:
            print(f"更新缓冲区: {response.get_updates_buf[:50]}...")
            
    except Exception as e:
        print(f"✗ 接收消息出错: {e}")
        return False
    
    return True

async def check_status(client):
    """检查状态示例"""
    print("=== 插件状态检查 ===")
    
    # TODO: 实现完整的状态检查
    # 基于wx-robot-ilink的状态查询
    
    print("客户端状态检查功能开发中...")
    print("建议使用 /wechat_status 查看完整状态")
    
    return True

async def main():
    parser = argparse.ArgumentParser(description="微信iLink插件示例")
    parser.add_argument("--auth", action="store_true", help="登录认证")
    parser.add_argument("--send", action="store_true", help="发送消息")
    parser.add_argument("--receive", action="store_true", help="接收消息")
    parser.add_argument("--status", action="store_true", help="检查状态")
    parser.add_argument("--to", type=str, help="接收消息的用户ID")
    parser.add_argument("--message", type=str, help="要发送的消息内容")
    parser.add_argument("--timeout", type=int, default=30, help="接收超时时间")
    parser.add_argument("--logout", action="store_true", help="清除凭证")
    
    args = parser.parse_args()
    
    if args.logout:
        print("=== 清除登录凭证 ===")
        auth_manager = AuthManager()
        auth_manager.clear_credentials()
        print("✓ 凭证已清除")
        return
    
    # 没有指定任何操作时显示帮助
    if not any([args.auth, args.send, args.receive, args.status]):
        parser.print_help()
        print("\n示例:")
        print("  python examples/basic_usage.py --auth")
        print("  python examples/basic_usage.py --send --to wxid_xxx --message '你好'")
        print("  python examples/basic_usage.py --receive --timeout 10")
        print("  python examples/basic_usage.py --logout")
        return
    
    # 认证或加载凭证
    credentials = None
    if args.auth:
        credentials = await authenticate()
    else:
        auth_manager = AuthManager()
        if auth_manager.load_credentials():
            credentials = auth_manager.credentials
            print(f"✓ 使用已保存凭证: {credentials.account_id}")
        else:
            print("! 未找到认证凭证，请先运行 --auth 登录")
            print("  或通过 Hermes 执行 /wechat_auth")
            return
    
    if not credentials:
        print("✗ 认证失败，无法继续")
        return
    
    # 创建客户端
    client = WeChatILinkClient(credentials)
    
    # 执行指定操作
    if args.send:
        if not args.to or not args.message:
            print("! 发送消息需要 --to 和 --message 参数")
            return
        await send_message(client, args.to, args.message)
    
    elif args.receive:
        await receive_messages(client, timeout=args.timeout)
    
    elif args.status:
        await check_status(client)

if __name__ == "__main__":
    asyncio.run(main())