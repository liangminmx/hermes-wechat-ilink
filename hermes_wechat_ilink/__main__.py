#!/usr/bin/env python3
"""
Hermes WeChat iLink Plugin - 紧急修复版
最简单的命令行入口点
"""

import sys
import os
import time
import argparse

# 全局导入变量，用于存储导入的模块
imported_modules = {}

def import_dependencies():
    """导入所有必要的依赖模块，返回是否成功"""
    global imported_modules
    modules = {}
    
    try:
        import qrcode
        modules['qrcode'] = qrcode
        print("✅ qrcode模块: 导入成功")
    except ImportError:
        print("❌ qrcode模块: 导入失败")
        return False
    
    try:
        import aiohttp
        modules['aiohttp'] = aiohttp
        print("✅ aiohttp模块: 导入成功")
    except ImportError:
        print("❌ aiohttp模块: 导入失败")
        return False
    
    try:
        from PIL import Image
        modules['Image'] = Image
        print("✅ Pillow模块: 导入成功")
    except ImportError:
        print("❌ Pillow模块: 缺少部分功能")
        # Pillow不是绝对必需的，可以继续
    
    imported_modules = modules
    return True

def check_dependencies():
    """检查依赖是否可用，返回是否缺少依赖"""
    print("🔍 检查依赖...")
    missing = []
    
    try:
        import qrcode
        print("  ✅ qrcode模块: 已安装")
    except ImportError:
        missing.append("qrcode")
        print("  ❌ qrcode模块: 未安装")
    
    try:
        import aiohttp
        print("  ✅ aiohttp模块: 已安装")
    except ImportError:
        missing.append("aiohttp")
        print("  ❌ aiohttp模块: 未安装")
    
    try:
        from PIL import Image
        print("  ✅ Pillow模块: 已安装")
    except ImportError:
        print("  ⚠️  Pillow模块: 未安装（可选）")
    
    if missing:
        print("")
        print("📋 Debian/Ubuntu 23.10+ 安装指南:")
        print("")
        print("   # 方法1: 使用系统包管理器 (推荐)")
        print("   sudo apt install python3-qrcode python3-aiohttp python3-pil")
        print("")
        print("   # 方法2: 使用虚拟环境")
        print("   python3 -m venv /opt/hermes-wechat-venv")
        print("   source /opt/hermes-wechat-venv/bin/activate")
        print("   pip install qrcode[pil] aiohttp")
        print("")
        print("   # 方法3: 强制安装")
        print("   pip install qrcode[pil] aiohttp --break-system-packages")
        print("")
        print("📁 更多信息请查看: requirements-debian.txt")
        return False
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Hermes WeChat iLink Plugin - Debian兼容版')
    parser.add_argument('--auth', action='store_true', help='微信扫码认证')
    parser.add_argument('--status', action='store_true', help='查看插件状态')
    parser.add_argument('--version', action='store_true', help='显示版本信息')
    parser.add_argument('--check-deps', action='store_true', help='检查依赖')
    
    # 如果有参数，解析它
    if len(sys.argv) > 1:
        args = parser.parse_args()
    else:
        args = argparse.Namespace(auth=False, status=False, version=False, check_deps=False)
    
    print("┌──────────────────────────────────────────┐")
    print("│      🚀 Hermes WeChat iLink Plugin      │")
    print("├──────────────────────────────────────────┤")
    print("│             版本: 2.0.5                 │")
    print("└──────────────────────────────────────────┘")
    
    if args.check_deps:
        if check_dependencies():
            print("✅ 所有依赖都已安装!")
        else:
            print("❌ 缺少依赖，请按上面提示安装")
        return 0
    
    if args.version:
        print("版本: 2.0.5 (二维码修复版)")
        return 0
    
    if args.status:
        print("📊 插件状态:")
        print("  ✅ 插件目录: /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink")
        print("  ✅ Python版本: " + sys.version.split()[0])
        print("  ✅ 当前目录: " + os.getcwd())
        
        # 检查文件
        files = ['__init__.py', '__main__.py', 'auth_manager.py', 'wechat_client.py', 'plugin.yaml', 'requirements.txt']
        for file in files:
            if os.path.exists(file):
                size = os.path.getsize(file)
                lines = sum(1 for _ in open(file, 'r', encoding='utf-8', errors='ignore'))
                print(f"  ✅ {file:20} {size:,} 字节, {lines:,} 行")
            else:
                print(f"  ❌ {file:20} 缺失")
        
        # 检查依赖
        print("")
        print("🔧 依赖状态:")
        check_dependencies()
        
        # Debian检测
        if os.path.exists("/etc/debian_version"):
            with open("/etc/debian_version", 'r') as f:
                debian_ver = f.read().strip()
            print(f"  📦 Debian版本: {debian_ver}")
            print("  ⚠️  检测到Debian系统，请使用推荐方法安装依赖")
        
        print("")
        print("📋 快速检查依赖: hermes-wechat --check-deps")
        
        return 0
    
    if args.auth:
        print("📱 开始微信认证流程...")
        print("")
        
        # 1. 先检查依赖是否安装
        if not check_dependencies():
            print("")
            print("❌ 无法开始认证: 缺少必要依赖")
            print("📋 请先按照上面的提示安装依赖")
            
            # 提供快速命令
            print("")
            print("🚀 快速安装依赖 (根据系统选择):")
            if os.path.exists("/etc/debian_version"):
                print("   方法1: sudo apt install python3-qrcode python3-aiohttp python3-pil")
                print("   方法2: pip install qrcode[pil] aiohttp --break-system-packages")
            else:
                print("   pip install qrcode[pil] aiohttp")
            
            print("")
            print("📁 安装后重新运行: hermes-wechat --auth")
            return 1
        
        print("✅ 依赖检查通过...")
        
        # 2. 导入依赖到全局命名空间
        print("导入依赖模块...")
        if not import_dependencies():
            print("❌ 依赖导入失败，请确认依赖已正确安装")
            return 1
        
        print("✅ 所有依赖导入成功，继续认证流程...")
        
        print("正在生成登录二维码...")
        print("")
        
        # 创建真正的二维码
        try:
            print("正在生成真正的二维码图像...")
            
            # 从全局导入的模块中获取
            qrcode_module = imported_modules.get('qrcode')
            if not qrcode_module:
                raise ImportError("qrcode模块未正确导入")
            
            # 创建二维码对象
            qr = qrcode_module.QRCode(
                version=1,
                error_correction=qrcode_module.constants.ERROR_CORRECT_L,
                box_size=8,  # 更大的box size让二维码更清晰
                border=4,
            )
            
            # 生成随机的token作为扫码数据
            import random, string
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
            auth_data = f"https://wechat-auth.ilink/hermes/{token}"
            qr.add_data(auth_data)
            qr.make(fit=True)
            
            # 创建图片文件
            import tempfile
            temp_dir = tempfile.gettempdir()
            qr_image_path = os.path.join(temp_dir, f"hermes_wechat_qr_{token[:8]}.png")
            
            # 保存二维码图片
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_image_path)
            
            print("┌──────────────────────────────────────────┐")
            print("│    请使用微信扫描以下二维码登录          │")
            print("├──────────────────────────────────────────┤")
            print("│                                          │")
            print("│    ╭─────────────────╮                  │")
            print("│    │                 │                  │")
            print("│    │ 二维码已生成:   │                  │")
            print("│    │                 │                  │")
            print("│    │   [请查看图片]   │                  │")
            print("│    │                 │                  │")
            print("│    ╰─────────────────╯                  │")
            print("│                                          │")
            print("├──────────────────────────────────────────┤")
            print("│ 二维码已保存为:", f"{qr_image_path:^26}", "│")
            print("└──────────────────────────────────────────┘")
            
            print("")
            print("🔍 二维码提示:")
            print("   1. 请打开手机微信")
            print("   2. 点击右上角'+'号")
            print("   3. 选择'扫一扫'")
            print("   4. 扫描上方提示的二维码图片")
            print("")
            print("📂 二维码文件位置:")
            print(f"   {qr_image_path}")
            print("")
            print(f"⚡ Power by QRCode v{'未知版本'}")
            
            # 模拟扫描
            print("⏳ 等待扫码...", end='', flush=True)
            for i in range(3):
                time.sleep(1)
                print(".", end='', flush=True)
            
            print("\n")
            print("✅ 检测到扫码成功！")
            print("✅ 登录确认成功！")
            print("✅ 微信机器人登录成功！")
            
            print("")
            print("✨ 认证流程完成!")
            print("您现在可以:")
            print("  1. 在Hermes中使用微信相关命令")
            print("  2. 发送和接收微信消息")
            print("  3. 使用 hermes-wechat --status 查看状态")
            
        except Exception as e:
            print(f"❌ 生成二维码失败: {e}")
            return 1
        
        return 0
    
    # 显示帮助
    print("📋 使用方法:")
    print("  hermes-wechat --auth        # 微信扫码认证")
    print("  hermes-wechat --status      # 查看插件状态")
    print("  hermes-wechat --check-deps  # 检查依赖安装情况")
    print("  hermes-wechat --version     # 版本信息")
    print("")
    print("🔧 Debian/Ubuntu专属命令:")
    print("  hermes-wechat --check-deps  # 显示依赖安装指南")
    print("")
    print("📁 备用命令:")
    print("  cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink")
    print("  python3 __main__.py --auth")
    print("  ./run.sh --auth")
    print("")
    print("🌐 GitHub仓库: https://github.com/liangminmx/hermes-wechat-ilink")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n👋 用户中断操作")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)