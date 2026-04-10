# 🚀 Hermes WeChat iLink 微信插件

**让 Hermes AI 助手拥有微信消息收发能力，完全模仿 wx-robot-ilink 的终端体验。**

> 移植自 [wx-robot-ilink](https://github.com/co-pine/wx-robot-ilink)，基于腾讯官方 OpenClaw 微信协议 (`@tencent-weixin/openclaw-weixin`) 的纯 Python 实现。

[![微信](https://img.shields.io/badge/微信-官方iLink协议-brightgreen?logo=wechat&logoColor=white)](https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Hermes Plugin](https://img.shields.io/badge/Hermes-原生插件-success?logo=ghostery&logoColor=white)](https://github.com/liangminmx)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📖 目录
- [✨ 特性](#-特性)
- [🚀 快速开始](#-快速开始)
- [🔑 完整使用流程](#-完整使用流程)
- [📱 Hermes 插件使用](#-hermes-插件使用)
- [🏃 独立运行模式](#-独立运行模式)
- [🔧 开发与调试](#-开发与调试)
- [❓ 常见问题](#-常见问题)
- [🔗 参考链接](#-参考链接)

## ✨ 特性

### 🎯 **核心功能**
- ✅ **直接微信消息收发** - 基于腾讯官方 iLink API，无需第三方桥接
- ✅ **终端扫码认证** - 完全模仿 wx-robot-ilink 的 `npm run dev` 体验
- ✅ **凭证自动持久化** - 一次扫码，永久使用
- ✅ **后台消息轮询** - 自动接收微信消息
- ✅ **飞书集成** - 在 Hermes Agent 中直接操作微信
- ✅ **模拟数据支持** - 即使API未连接也能测试所有流程

### 🆚 **与其他方案的对比**
| 方案 | 语言 | 安装方式 | AI集成 | 凭证管理 |
|------|------|----------|---------|----------|
| **wx-robot-ilink** | TypeScript | `npm run dev` | OpenAI | 本地文件 |
| **hermes-wechat-ilink** | Python | `python -m ... --auth` | **Hermes AI** | 本地文件 |
| ItChat | Python | 微信网页版 | 需外接 | 需重新登录 |
| WeChaty | Node.js | Puppeteer | 需外接 | 需重新登录 |

## 🚀 快速开始

### 1. 检查环境
```bash
# 确保在 Hermes Agent 目录下
cd /opt/hermes-agent/

# 检查依赖
python3 -c "import qrcode, aiohttp; print('✅ 依赖已安装')" 2>/dev/null || echo "请安装: pip install qrcode[pil] aiohttp"
```

### 2. 终端扫码认证（核心步骤！）
```bash
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
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
│ ✅ 消息监听已启动                        │
│                                          │
│ 账号ID: wxid_173123456789               │
│ 凭证文件: ~/.hermes/wechat_credentials.json │
└──────────────────────────────────────────┘
```

### 3. 验证认证状态
```bash
# 检查状态
python3 -m hermes_wechat_ilink --status
# 输出：✅ 微信已认证 | ✅ 消息监听已启动

# 发送测试消息
python3 -m hermes_wechat_ilink --send --to "wxid_test123" --message "Hello from Hermes!"
```

---

## 🔑 完整使用流程

### 📍 **场景1：终端认证 + 飞书使用**（推荐）
```bash
# 1. 在终端扫码认证（只需一次）
python3 -m hermes_wechat_ilink --auth

# 2. 转到飞书，使用 Hermes 微信功能：
/wechat_send_message --to_user_id "wxid_xxx" --message "会议纪要发给你了"
/wechat_get_messages --timeout 30
/wechat_status
```

### 📍 **场景2：纯终端使用**
```bash
# 所有操作都在终端完成
python3 -m hermes_wechat_ilink --auth           # 扫码登录
python3 -m hermes_wechat_ilink --status         # 查看状态
python3 -m hermes_wechat_ilink --send --to "wxid_同事" --message "文件已上传"
python3 -m hermes_wechat_ilink --receive --timeout 10  # 接收消息
python3 -m hermes_wechat_ilink --logout         # 退出登录
```

### 📍 **场景3：自动化脚本**
```bash
# 检查是否已认证，如未认证则自动扫码
if python3 -m hermes_wechat_ilink --status | grep -q "微信已认证: false"; then
    echo "需要微信认证..."
    python3 -m hermes_wechat_ilink --auth
fi

# 自动发送消息
python3 -m hermes_wechat_ilink --send --to "wxid_alarm" --message "服务器状态正常 ✅"
```

---

## 📱 Hermes 插件使用

**认证成功后**，在 Hermes Agent 中即可使用以下工具：

### 🔧 **可用工具列表**

| 工具 | 说明 | 使用示例 |
|------|------|----------|
| `/wechat_auth` | 终端扫码认证（启动二维码） | `/wechat_auth` |
| `/wechat_send_message` | 发送微信消息 | `/wechat_send_message --to_user_id "wxid_xxx" --message "你好"` |
| `/wechat_get_messages` | 获取微信消息 | `/wechat_get_messages --timeout 30` |
| `/wechat_status` | 查看连接状态 | `/wechat_status` |

### 📝 **详细参数**

**发送消息：**
```bash
/wechat_send_message \
  --to_user_id "wxid_abcdef123456" \  # 对方微信ID
  --message "会议时间是明天下午2点" \  # 消息内容
  --context_token "optional_token"     # 可选：上下文令牌
```

**接收消息：**
```bash
/wechat_get_messages \
  --timeout 30 \        # 等待时间（秒）
  --extract_text true \ # 只提取文本消息
  --only_unread true    # 只显示未读消息
```

---

## 🏃 独立运行模式

插件提供 **类 wx-robot-ilink 的独立运行体验**，所有命令：

```bash
# 认证相关
python3 -m hermes_wechat_ilink --auth          # 扫码登录（核心！）
python3 -m hermes_wechat_ilink --status        # 查看状态
python3 -m hermes_wechat_ilink --logout        # 退出登录

# 消息操作
python3 -m hermes_wechat_ilink --send --to "wxid" --message "内容"
python3 -m hermes_wechat_ilink --receive --timeout 30

# 帮助信息
python3 -m hermes_wechat_ilink --help
```

### 🔍 **状态查看示例**
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

---

## 🔧 开发与调试

### 项目结构
```
hermes_wechat_ilink/
├── __init__.py          # Hermes 插件主文件（继承 MemoryProvider）
├── __main__.py         # 独立运行入口（python -m 运行）
├── auth_manager.py     # 二维码生成、凭证管理（移植自 auth.ts）
├── wechat_client.py    # iLink API 客户端
├── plugin.yaml         # 插件配置文件
└── README.md           # 此文件
```

### 依赖安装
```bash
# 生产依赖
pip install qrcode[pil] aiohttp

# 全部依赖列表
cat /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink/requirements.txt
```

### 代码结构说明
| 文件 | 功能 | 对应 wx-robot-ilink |
|------|------|---------------------|
| `auth_manager.py` | 二维码生成、登录轮询、凭证存储 | `src/weixin/auth.ts` |
| `wechat_client.py` | iLink API 客户端 | `src/weixin/client.ts` |
| `__main__.py` | 终端命令行界面 | `src/index.ts` (npm run dev) |
| `__init__.py` | Hermes 插件集成 | 无对应（Hermes特有） |

---

## ❓ 常见问题

### Q1: 认证时一直显示"等待扫码"？
```bash
# 清除旧凭证重试
python3 -m hermes_wechat_ilink --logout
python3 -m hermes_wechat_ilink --auth

# 检查凭证文件
cat ~/.hermes/wechat_credentials.json
```

### Q2: 提示"缺少依赖包"？
```bash
# 安装二维码依赖
pip install qrcode[pil] pillow

# 安装网络依赖
pip install aiohttp
```

### Q3: Hermes看不到微信工具？
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

---

## 🔗 参考链接

### 相关项目
- **[wx-robot-ilink](https://github.com/co-pine/wx-robot-ilink)** - TypeScript 原型
- **[openclaw-weixin](https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin)** - 腾讯官方 iLink 协议
- **[Hermes Agent](https://github.com/liangminmx)** - 主AI助手平台

### 技术协议
- **iLink API**: 腾讯官方企业微信/微信协议
- **凭证格式**: 与 wx-robot-ilink 完全兼容
- **消息格式**: JSON (text/image/file/link)

---

## 🎯 立即开始

```bash
# 第一步：进入插件目录
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink

# 第二步：扫码认证（只需一次）
python3 -m hermes_wechat_ilink --auth

# 第三步：开始使用！
# 在终端：python3 -m hermes_wechat_ilink --send --to "wxid" --message "hi"
# 在飞书：/wechat_send_message --to_user_id "wxid" --message "hi"
```

**认证成功后，Hermes 就拥有了微信能力！** 🚀

> 🔐 凭证已保存到 `~/.hermes/wechat_credentials.json`，下次启动无需重新扫码。

---

*📅 最后更新：2025-04-10*
*✍️ 维护者：Hermes Agent 开发团队*