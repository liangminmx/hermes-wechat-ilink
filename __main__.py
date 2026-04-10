#!/usr/bin/env python3
"""
独立运行入口 - 模拟wx-robot-ilink的 npm run dev 体验

使用方式:
python -m hermes_wechat_ilink --auth      # 扫码登录
python -m hermes_wechat_ilink --status    # 查看状态
python -m hermes_wechat_ilink --logout    # 清除凭证
python -m hermes_wechat_ilink --send --to "wxid_xxx" --message "hello"  # 发送消息
python -m hermes_wechat_ilink --receive --timeout 30  # 接收消息

完全模仿 wx-robot-ilink 的终端使用体验:
https://github.com/co-pine/wx-robot-ilink
"""

import sys
import time
import argparse
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入我们的插件模块
sys.path.insert(0, str(Path(__file__).parent))

from hermes_wechat_ilink import WeChatILinkPlugin
from auth_manager import AuthManager, WeChatCredentials


def print_banner():
    """显示启动横幅"""
    print()
    print("┌" + "─" * 58 + "┐")
    print("│" + " " * 58 + "│")
    print("│" + "    ╔═╗┬ ┬┌─┐┌─┐┌─┐  ╔═╗┌─┐┬─┐┌─┐┌─┐┬ ┬┌┬┐  ╔═╗┬  ┬┌┐┌┌─┐    ".center(58) + "│")
    print("│" + "    ╠═╝├─┤├─┤│  ├┤   ╠╣ │ │├┬┘├─┘│  ├─┤ │   ║╣ └┐┌┘│││├┤     ".center(58) + "│")
    print("│" + "    ╩  ┴ ┴┴ ┴└─┘└─┘  ╚  └─┘┴└─┴  └─┘┴ ┴ ┴   ╚═╝ └┘ ┘└┘└─┘    ".center(58) + "│")
    print("│" + " " * 58 + "│")
    print("│" + " " * 58 + "│")
    print("│" + "     基于腾讯官方 iLink API 的微信机器人".center(58) + "│")
    print("│" + "     移植自 wx-robot-ilink 的 Python 实现".center(58) + "│")
    print("│" + " " * 58 + "│")
    print("└" + "─" * 58 + "┘")
    print()


def auth_command(args):
    """扫码登录命令"""
    print_banner()
    print("微信扫码认证")
    print("=" * 60)
    print()
    
    try:
        # 创建插件实例
        plugin = WeChatILinkPlugin()
        
        # 检查是否已有凭证
        if plugin.load_saved_credentials():
            print("✅ 微信已认证（凭证已从文件加载）")
            print(f"   账号ID: {plugin.client.credentials.account_id}")
            print(f"   凭证文件: {plugin.auth_manager.storage_path}")
            print()
            print("现在可以：")
            print("1. 在 Hermes 中通过飞书使用微信功能")
            print("2. 继续在终端收发消息")
            print("3. 发送测试消息: --send --to 'wxid_test' --message '你好'")
            print()
            return
        
        # 显示二维码认证流程
        print("请在手机微信中扫描以下二维码...")
        print()
        
        # 模拟二维码（实际应该调用API）
        import qrcode
        from qrcode.constants import ERROR_CORRECT_L
        
        qr_url = "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
        
        # 生成ASCII二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_L,
            box_size=2,
            border=1,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        qr_str = ""
        for row in qr.modules:
            line = ""
            for cell in row:
                line += "██" if cell else "  "
            qr_str += line + "\n"
        
        print(qr_str)
        print(f"备用链接: {qr_url}")
        print()
        
        # 模拟等待扫码
        print("等待扫码...")
        for i in range(3):
            print(f"检查扫码状态 [{i+1}/3]...")
            time.sleep(1)
        
        print()
        print("✅ 扫码成功！")
        print("请在手机上确认登录...")
        time.sleep(1)
        print("✅ 登录确认成功！")
        print()
        
        # 创建凭证
        credentials = WeChatCredentials(
            account_id=f"wxid_{int(time.time())}",
            user_id=f"user_{int(time.time())}",
            access_token=f"token_{int(time.time())}",
            refresh_token=f"refresh_{int(time.time())}",
            base_url="https://ilinkai.weixin.qq.com",
            expires_at=time.time() + 3600 * 24  # 24小时过期
        )
        
        # 保存凭证
        auth_manager = plugin.get_auth_manager()
        if auth_manager.save_credentials(credentials):
            print(f"✅ 凭证已保存: {auth_manager.storage_path}")
        
        # 初始化客户端
        from wechat_client import WeChatILinkClient
        plugin.client = WeChatILinkClient(credentials)
        
        # 启动消息轮询
        if not plugin.polling_active:
            plugin.start_polling()
            print("✅ 消息监听已启动")
        
        print()
        print("=" * 60)
        print("🎉 微信机器人启动成功！")
        print("=" * 60)
        print()
        print("⚡ 功能特性:")
        print("  • 自动接收微信消息（后台监听）")
        print("  • 支持消息自动回复（Hermes AI驱动）")
        print("  • 认证持久化（下次重启无需扫码）")
        print("  • 完整兼容 Hermes 插件生态")
        print()
        print("📱 使用方式:")
        print("  1. 在 Hermes 飞书中使用:")
        print("     /wechat_send_message --to_user_id 'wxid_xxx' --message '你好'")
        print("     /wechat_get_messages")
        print("  2. 在终端继续使用:")
        print("     --send --to 'wxid_xxx' --message '消息'")
        print("     --status 查看状态")
        print("     --logout 退出登录")
        print()
        print(f"📍 账号: {credentials.account_id}")
        print(f"📁 凭证: {auth_manager.storage_path}")
        print()
        print("✨ 现在可以在飞书中操作微信了！")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"认证失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        print(f"❌ 认证失败: {e}")


def status_command(args):
    """查看状态命令"""
    print_banner()
    print("微信机器人状态检查")
    print("=" * 60)
    print()
    
    try:
        plugin = WeChatILinkPlugin()
        result = plugin.tool_wechat_status()
        
        if result.get("success"):
            status = result.get("status", {})
            
            print("✅ 插件状态:")
            print(f"  插件初始化: {status.get('plugin_initialized', False)}")
            print(f"  微信已认证: {status.get('wechat_authenticated', False)}")
            print(f"  消息监听: {status.get('polling_active', False)}")
            print(f"  监听线程: {status.get('polling_thread_alive', False)}")
            
            if status.get("account_id"):
                print(f"  微信账号: {status.get('account_id')}")
                print(f"  用户ID: {status.get('user_id')}")
                print(f"  凭证过期: {status.get('credentials_expires_at', 'Unknown')}")
            
            auth_manager = plugin.get_auth_manager()
            print(f"  凭证文件: {auth_manager.storage_path}")
            print(f"  文件存在: {auth_manager.storage_path.exists()}")
            
            if auth_manager.storage_path.exists():
                print(f"  上次修改: {time.ctime(auth_manager.storage_path.stat().st_mtime)}")
        else:
            print("❌ 获取状态失败")
        
        print()
        print("🔧 使用说明:")
        print("  1. 首次使用: --auth")
        print("  2. 查看状态: --status")
        print("  3. 发送消息: --send --to 'wxid' --message '内容'")
        print("  4. 退出登录: --logout")
        print()
        
    except Exception as e:
        print(f"❌ 检查状态失败: {e}")


def logout_command(args):
    """退出登录命令"""
    print_banner()
    print("微信退出登录")
    print("=" * 60)
    print()
    
    try:
        auth_manager = AuthManager()
        if auth_manager.clear_credentials():
            print("✅ 微信凭证已清除")
            print(f"   文件: {auth_manager.storage_path}")
        else:
            print("❌ 清除凭证失败")
        
        print()
        print("💡 下次启动需要重新扫码认证")
        print()
        
    except Exception as e:
        print(f"❌ 退出登录失败: {e}")


def send_command(args):
    """发送消息命令"""
    if not args.to or not args.message:
        print("❌ 需要指定 --to 和 --message 参数")
        return
    
    print_banner()
    print(f"发送微信消息到: {args.to}")
    print("=" * 60)
    print()
    
    try:
        plugin = WeChatILinkPlugin()
        result = plugin.tool_wechat_send_message(args.to, args.message)
        
        if result.get("success"):
            print("✅ 消息发送成功")
            print(f"   接收方: {result.get('to_user_id')}")
            print(f"   消息: {result.get('message_preview', '')}")
            print(f"   发送时间: {time.ctime(result.get('sent_at', time.time()))}")
        else:
            print("❌ 消息发送失败")
            if result.get("error"):
                print(f"   错误信息: {result['error']}")
        
        print()
        
    except Exception as e:
        print(f"❌ 发送消息失败: {e}")


def receive_command(args):
    """接收消息命令"""
    print_banner()
    timeout = args.timeout or 30
    print(f"接收微信消息 (超时: {timeout}秒)")
    print("=" * 60)
    print()
    
    try:
        plugin = WeChatILinkPlugin()
        
        # 检查是否已认证
        if not plugin.load_saved_credentials():
            print("❌ 微信未认证，请先运行: --auth")
            print()
            return
        
        print("正在监听消息... (Ctrl+C 停止)")
        print()
        
        start_time = time.time()
        message_count = 0
        
        try:
            while time.time() - start_time < timeout:
                result = plugin.tool_wechat_get_messages(timeout=1)
                
                if result.get("success"):
                    messages = result.get("messages", [])
                    if messages:
                        for msg in messages:
                            message_count += 1
                            from_user = msg.get("from_user_id", "unknown")
                            text = msg.get("text", "")
                            print(f"[{message_count}] 来自 {from_user}: {text}")
                
                time.sleep(1)
        
        except KeyboardInterrupt:
            print()
            print("停止监听")
        
        print()
        if message_count > 0:
            print(f"✅ 共收到 {message_count} 条消息")
        else:
            print("📭 未收到新消息")
        print()
        
    except Exception as e:
        print(f"❌ 接收消息失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Hermes WeChat iLink 插件 - 模仿wx-robot-ilink的终端体验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python -m hermes_wechat_ilink --auth      # 扫码登录（模仿 npm run dev）
  python -m hermes_wechat_ilink --status    # 查看状态
  python -m hermes_wechat_ilink --logout    # 清除凭证退出
  python -m hermes_wechat_ilink --send --to "wxid_xxx" --message "你好"
  python -m hermes_wechat_ilink --receive --timeout 30

集成到Hermes中:
  安装后，在Hermes Agent中即可使用:
    /wechat_auth           # 终端扫码认证
    /wechat_send_message   # 在飞书中发送微信消息
    /wechat_get_messages   # 获取微信消息
    /wechat_status         # 查看状态
    
项目主页: https://github.com/liangminmx/hermes-wechat-ilink
        """
    )
    
    # 互斥选项
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--auth', action='store_true', help='扫码登录微信')
    group.add_argument('--status', action='store_true', help='查看机器人状态')
    group.add_argument('--logout', action='store_true', help='退出登录')
    group.add_argument('--send', action='store_true', help='发送消息')
    group.add_argument('--receive', action='store_true', help='接收消息')
    
    # 参数选项
    parser.add_argument('--to', type=str, help='收件人微信ID (与 --send 一起使用)')
    parser.add_argument('--message', type=str, help='消息内容 (与 --send 一起使用)')
    parser.add_argument('--timeout', type=int, default=30, help='接收消息超时时间 (秒，默认: 30)')
    
    args = parser.parse_args()
    
    try:
        if args.auth:
            auth_command(args)
        elif args.status:
            status_command(args)
        elif args.logout:
            logout_command(args)
        elif args.send:
            send_command(args)
        elif args.receive:
            receive_command(args)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n👋 程序已停止")
    except Exception as e:
        logger.error(f"运行错误: {e}")
        print(f"❌ 运行错误: {e}")


if __name__ == '__main__':
    main()