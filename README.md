# 🚀 Hermes WeChat iLink 微信插件

**纯净版插件，解决 "No module named hermes_wechat_ilink" 问题**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Hermes Plugin](https://img.shields.io/badge/Hermes-原生插件-success?logo=ghostery&logoColor=white)](https://github.com/liangminmx)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 🎯 核心特点

✅ **纯净包结构** - 完全解决 `python3 -m hermes_wechat_ilink` 导入问题  
✅ **多运行方式** - 支持4种运行方法  
✅ **一键安装** - 提供完整安装脚本  
✅ **全局命令** - 创建 `hermes-wechat` 全局命令  
✅ **依赖自动检查** - 运行时自动提示  

## 🚀 快速开始

### 方法一：一键安装（推荐）

```bash
# 直接运行（会自动检测和安装）
curl -sL https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh | bash

# 或下载后运行
wget -O install.sh https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh
bash install.sh
```

### 方法二：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink

# 2. 复制插件文件到Hermes插件目录
cp -r hermes_wechat_ilink/* /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink/

# 3. 安装依赖
pip install qrcode[pil] aiohttp

# 4. 创建全局命令（可选）
sudo cp bin/hermes-wechat /usr/local/bin/
chmod +x /usr/local/bin/hermes-wechat
```

## 📱 使用方式

### 方式1 - 全局命令（最简单）
```bash
hermes-wechat --auth          # 扫码认证
hermes-wechat --status        # 查看状态
hermes-wechat --send --to "wxid_test" --message "你好"
```

### 方式2 - 直接运行（最可靠）
```bash
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
python3 __main__.py --auth
```

### 方式3 - Python模块方式
```bash
python3 -m hermes_wechat_ilink.__main__ --auth
```

### 方式4 - 直接调用
```bash
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
python3 -c "import sys; sys.path.insert(0, '.'); from __main__ import main; main()" --auth
```

## 🛠️ 修复的问题

### ✅ 已解决的问题
1. **"No module named hermes_wechat_ilink"** - 纯净包结构
2. **无法 `python3 -m hermes_wechat_ilink`** - 创建正确模块结构
3. **依赖问题** - 运行时自动检查
4. **多运行方式** - 提供4种运行方法
5. **全局访问** - 创建 `hermes-wechat` 命令

### 📁 纯净包结构
```
hermes_wechat_ilink/          # ✅ 纯插件目录
├── __init__.py              # Hermes插件主文件
├── __main__.py              # CLI入口点
├── auth_manager.py          # 认证管理
├── wechat_client.py         # iLink客户端
└── plugin.yaml              # 插件配置
```

### 🔧 安装脚本功能
- ✅ 自动检测Python环境
- ✅ 自动安装依赖
- ✅ 创建全局命令
- ✅ 验证安装结果

## ❓ 常见问题

### Q: 仍然出现 "No module named hermes_wechat_ilink"？
```bash
# 使用最可靠的方式2
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
python3 __main__.py --auth

# 或安装全局命令
sudo cp bin/hermes-wechat /usr/local/bin/
hermes-wechat --auth
```

### Q: 需要安装依赖？
```bash
pip install qrcode[pil] aiohttp
```

### Q: 如何卸载？
```bash
# 删除插件文件
rm -rf /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink

# 删除全局命令
sudo rm -f /usr/local/bin/hermes-wechat
```

## 📞 支持与反馈

**维护者**: 假装不单纯  
**仓库**: https://github.com/liangminmx/hermes-wechat-ilink  
**问题**: https://github.com/liangminmx/hermes-wechat-ilink/issues  

---

*📅 最后更新: 2025-04-11*  
*✨ 完全解决导入问题，享受无障碍微信插件体验！*
