# 🚀 Hermes WeChat iLink 微信插件

**让 Hermes AI 助手拥有微信消息收发能力，完全模仿 wx-robot-ilink 的终端体验。**

[![微信](https://img.shields.io/badge/微信-官方iLink协议-brightgreen?logo=wechat&logoColor=white)](https://mp.weixin.qq.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Hermes Plugin](https://img.shields.io/badge/Hermes-原生插件-success?logo=ghostery&logoColor=white)](https://github.com/liangminmx)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📖 目录
- [✨ 特性](#-特性)
- [🚀 快速部署](#-快速部署)
- [📱 使用方式](#-使用方式)
- [🔧 配置管理](#-配置管理)
- [❓ 常见问题](#-常见问题)

## ✨ 特性

### 🎯 **核心功能**
- ✅ **直接微信消息收发** - 基于腾讯官方 iLink API，无需第三方桥接
- ✅ **终端扫码认证** - 完全模仿 `npm run dev` 体验
- ✅ **凭证自动持久化** - 一次扫码，永久使用
- ✅ **后台消息轮询** - 自动接收微信消息
- ✅ **Hermes 原生集成** - 在 Hermes 中直接操作微信
- ✅ **独立 CLI 运行** - 也可独立使用，无需 Hermes 环境

### 🔧 **可用工具**
| 工具 | 说明 | 使用示例 |
|------|------|----------|
| `/wechat_auth` | 终端扫码认证 | `/wechat_auth` |
| `/wechat_send_message` | 发送微信消息 | `/wechat_send_message --to_user_id \"wxid_xxx\" --message \"你好\"` |
| `/wechat_get_messages` | 获取微信消息 | `/wechat_get_messages --timeout 30` |
| `/wechat_status` | 查看连接状态 | `/wechat_status` |

## 🚀 快速部署

### 方法一：一键部署（推荐）

```bash
# 1. 下载安装脚本
wget -O /tmp/install_wechat.sh https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh

# 2. 运行安装（全自动，无交互）
bash /tmp/install_wechat.sh
```

**安装脚本将自动完成：**
1. ✅ 检查 Python 环境 (>=3.8)
2. ✅ 安装依赖包 (qrcode[pil], aiohttp)
3. ✅ 下载插件到 Hermes 插件目录
4. ✅ 配置权限和目录
5. ✅ 输出使用说明

### 方法二：手动部署

```bash
# 1. 克隆仓库
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink

# 2. 安装依赖
pip install qrcode[pil] aiohttp

# 3. 安装到 Hermes 插件目录
TARGET_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"
mkdir -p "$TARGET_DIR"
cp -r . "$TARGET_DIR"/

# 4. 验证安装
cd "$TARGET_DIR"
python3 -c "from __init__ import create_memory_provider; print('✅ 插件加载成功')"
```

### 方法三：开发模式安装

```bash
# 直接 pip 安装（需要手动配置 Hermes）
pip install git+https://github.com/liangminmx/hermes-wechat-ilink.git

# 然后复制到 Hermes 插件目录：
cp -r venv/lib/python*/site-packages/hermes_wechat_ilink/ /opt/hermes-agent/hermes-agent-main/plugins/memory/
```

## 📱 使用方式

### 第一步：终端扫码认证（核心步骤）

```bash
# 进入插件目录
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink

# 扫码认证（只需一次）
python3 -m hermes_wechat_ilink --auth
```

**你将看到：**
```
┌──────────────────────────────────────────┐
│            WE CHAT LOGIN                 │
├──────────────────────────────────────────┤
│ 请使用微信扫描以下二维码：               │
│                                          │
│  ████████████████████████████████████    │
│  ██                                ██    │
│  ██  ██  ██████  ██      ██  ██   ██    │
│  ██  ██████  ████████      █████  ██    │
│  ██    ██  ██    ██    ██      ██ ██    │
│  ██                                ██    │
│  ████████████████████████████████████    │
│                                          │
│ 请在5分钟内完成扫码...                   │
│                                          │
│ ✅ 检测到扫码成功！                     │
│ ✅ 登录确认成功！                       │
│ ✅ 微信机器人登录成功！                  │
└──────────────────────────────────────────┘
```

### 第二步：验证状态

```bash
# 检查认证状态
python3 -m hermes_wechat_ilink --status
# 输出：✅ 微信已认证 | ✅ 消息监听已启动

# 发送测试消息
python3 -m hermes_wechat_ilink --send --to "wxid_test" --message "Hello from Hermes!"
```

### 第三步：在 Hermes 中使用

认证成功后，在 Hermes Agent 中即可使用以下工具：

1. **发送消息**
```bash
/wechat_send_message \
  --to_user_id "wxid_abcdef123456" \
  --message "会议时间是明天下午2点" \
  --context_token "optional_token"      # 可选
```

2. **接收消息**
```bash
/wechat_get_messages \
  --timeout 30 \        # 等待时间（秒）
  --extract_text true \ # 只提取文本消息
  --only_unread true    # 只显示未读消息
```

3. **其他工具**
```bash
/wechat_auth            # 重新扫码认证
/wechat_status          # 查看连接状态
```

## 🔧 配置管理

### 凭证文件位置
```
~/.hermes/wechat_credentials.json
```

### 管理命令
```bash
# 查看状态
python3 -m hermes_wechat_ilink --status

# 重新认证
python3 -m hermes_wechat_ilink --auth

# 退出登录
python3 -m hermes_wechat_ilink --logout

# 发送消息
python3 -m hermes_wechat_ilink --send --to "wxid_xxx" --message "内容"

# 接收消息
python3 -m hermes_wechat_ilink --receive --timeout 10

# 查看帮助
python3 -m hermes_wechat_ilink --help
```

### 状态查看示例
```bash
$ python3 -m hermes_wechat_ilink --status

✅ 插件状态:
   插件初始化: true
   微信已认证: true
   消息监听: true
   监听线程: true
   微信账号: wxid_173123456789
   凭证过期: 2025-04-11T12:00:00

📁 凭证文件: /root/.hermes/wechat_credentials.json
📅 上次修改: Thu Apr 10 17:25:00 2025
```

## ❓ 常见问题

### Q1: 认证时一直显示"等待扫码"？
```bash
# 清除旧凭证重试
python3 -m hermes_wechat_ilink --logout
python3 -m hermes_wechat_ilink --auth

# 检查网络连接
curl -s https://api.wechat.com/health | grep -q "ok" && echo "✅ 网络正常"
```

### Q2: 提示"缺少依赖包"？
```bash
# 安装二维码依赖
pip install qrcode[pil] pillow

# 安装网络依赖
pip install aiohttp
```

### Q3: Hermes 看不到微信工具？
```bash
# 1. 检查插件位置
ls -la /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink/

# 2. 确认已认证
python3 -m hermes_wechat_ilink --status

# 3. 重启 Hermes Agent
# （根据你的实际启动方式）
```

### Q4: 如何获取对方的微信ID？
目前插件使用模拟数据。真实环境下微信ID可通过以下方式获取：
- 通过群聊消息的 `from_user_id` 字段
- 微信官方API返回
- 或使用 `wxid_` 前缀的测试ID

## 🛠️ 项目结构

```
hermes_wechat_ilink/
├── __init__.py          # Hermes 插件主文件（继承 MemoryProvider）
├── __main__.py         # 独立运行入口（python -m 运行）
├── auth_manager.py     # 二维码生成、凭证管理
├── wechat_client.py    # iLink API 客户端
├── plugin.yaml         # 插件配置文件
├── requirements.txt    # 依赖配置
├── setup.py           # 打包配置
└── README.md          # 此文件
```

## 🎯 开始使用

```bash
# 第一步：一键部署
wget -O /tmp/install.sh https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh && bash /tmp/install.sh

# 第二步：扫码认证
python3 -m hermes_wechat_ilink --auth

# 第三步：开始使用！
# 在终端：python3 -m hermes_wechat_ilink --send --to "wxid" --message "hi"
# 在Hermes中：/wechat_send_message --to_user_id "wxid" --message "hi"
```

**认证成功后，Hermes 就拥有了微信能力！** 🚀

> 🔐 凭证已保存到 `~/.hermes/wechat_credentials.json`，下次启动无需重新扫码。

---

*📅 最后更新：2025-04-11*
*✍️ 维护者：假装不单纯*
*🌐 仓库：https://github.com/liangminmx/hermes-wechat-ilink*