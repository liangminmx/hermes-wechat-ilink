# Hermes WeChat iLink Plugin

基于腾讯官方 OpenClaw 微信协议 (`@tencent-weixin/openclaw-weixin`) 的纯 Python 微信机器人插件。为 Hermes 提供直接的微信消息收发能力，无需任何第三方桥接服务。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/liangminmx/hermes-wechat-ilink?style=flat-square)](https://github.com/liangminmx/hermes-wechat-ilink/releases)
[![Hermes Plugin](https://img.shields.io/badge/Hermes-Plugin-brightgreen?style=flat-square)](https://github.com/liangminmx)

## 🎯 核心优势

- **官方协议**: 使用腾讯官方的 iLink 网关，非第三方破解方案
- **纯Python**: 基于 `wx-robot-ilink` 协议实现，零 Node.js 依赖
- **直接连接**: 扫码登录后直接对接微信服务器
- **完整集成**: Hermes 原生工具，支持所有 Hermes 平台（CLI、Telegram、Discord等）
- **简单部署**: 仅需 Python 环境，无需配置微信企业号或支付账号

## 🔄 与 wx-robot-ilink 的关系

| 特性 | wx-robot-ilink (TypeScript) | wechat-ilink (Python) |
|------|-----------------------------|------------------------|
| **语言** | TypeScript/Node.js | Python 3.8+ |
| **安装** | `npm install` | `pip install` 或 `./install.sh` |
| **配置** | `.env` 文件 | `.env` 文件（同格式） |
| **运行** | `npm run dev` | `python -m hermes_wechat_ilink` |
| **集成** | 独立AI机器人 | Hermes插件，使用Hermes AI |

**移植度**: 约 95%，包含完整认证流程、消息轮询、文本收发。AI对话功能由Hermes主Agent提供。

## 🚀 快速开始（类似wx-robot-ilink安装体验）

### 前提条件
- Python 3.8+
- pip 包管理工具
- Hermes Agent（可选，插件模式需要）

### 方式一：一键安装（推荐）
```bash
# 克隆项目
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink

# 一键安装（类似wx-robot-ilink：npm install）
chmod +x install.sh
./install.sh
```
**脚本会执行**:
1. 检查Python环境
2. 安装依赖（自动创建虚拟环境）
3. 配置环境变量
4. 复制到Hermes插件目录（如果Hermes存在）
5. 验证安装

### 方式二：手动安装
```bash
# 1. 克隆和依赖（类似npm install）
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink
pip install -r requirements.txt

# 2. 环境配置（类似wx-robot-ilink的.env）
cp .env.example .env
# 编辑 .env 文件（可选）

# 3. 复制到Hermes插件目录
./install.sh --skip-copy  # 不自动复制
# 或手动复制到 plugins/memory/
```

### 方式三：开发模式安装
```bash
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink

# 可编辑模式安装
pip install -e .

# 安装开发工具
pip install black ruff pytest
```

## 🔧 使用方式

### 作为Hermes插件使用（推荐）
```bash
# 1. 启动Hermes Agent
# 2. 使用插件提供的5个工具：

/wechat_auth            # 微信登录认证（显示二维码）
/wechat_status          # 查看连接状态  
/wechat_get_messages    # 接收微信消息
/wechat_send_message    # 发送微信消息
/wechat_webhook_server  # 启动HTTP服务器
```

### 独立运行（测试模式）
与wx-robot-ilink类似，可以直接运行：
```bash
# 独立认证（类似wx-robot-ilink npm run dev）
python -m hermes_wechat_ilink --auth

# 发送消息
python -m hermes_wechat_ilink --send --to "wxid_xxx" --message "你好"

# 接收消息
python -m hermes_wechat_ilink --receive --timeout 30

# 查看状态
python -m hermes_wechat_ilink --status

# 清除凭证
python -m hermes_wechat_ilink --logout
```

### 开发调用
```python
# 在你的Python代码中直接使用
from hermes_wechat_ilink import create_memory_provider

provider = create_memory_provider()
result = await provider.call_tool("wechat_status")
print(result)
```

## 📁 项目结构（与wx-robot-ilink对比）

```
# wx-robot-ilink (Node.js/TypeScript)
wx-robot-ilink/
├── src/                    # 源代码
├── .env.example           # 环境变量模板
├── package.json          # Node.js配置
└── npm run dev           # 启动命令

# hermes-wechat-ilink (Python)
hermes-wechat-ilink/
├── hermes_wechat_ilink/  # Python包源代码（类似src/）
├── .env.example          # 环境变量模板（同格式）
├── requirements.txt      # 依赖（类似package.json）
├── setup.cfg            # 包配置
├── install.sh           # 安装脚本（类似npm install）
├── examples/            # 使用示例
├── tests/               # 测试
├── Makefile             # 开发命令
└── README.md
```

## ⚙️ 配置说明

### 环境变量配置（`.env`文件）
```bash
# 复制模板并编辑
cp .env.example .env
nano .env  # 或 vim .env
```

`.env` 文件示例：
```env
# 基础配置
WECHAT_POLL_INTERVAL=5
WECHAT_API_TIMEOUT=15

# 调试模式
WECHAT_DEBUG=false
WECHAT_LOG_LEVEL=INFO

# Webhook服务器
WECHAT_WEBHOOK_ENABLED=false
WECHAT_WEBHOOK_PORT=8080
```

**关键区别**: 相比wx-robot-ilink，我们**不需要**配置：
- `OPENAI_API_KEY` - AI由Hermes提供
- `OPENAI_BASE_URL` - 使用Hermes配置
- `OPENAI_MODEL` - 使用Hermes模型
- `SYSTEM_PROMPT` - 在Hermes中配置

### Hermes配置文件
插件自动适配Hermes配置：
```yaml
# ~/.hermes/config.yaml
wechat-ilink:
  enable_polling: true
  poll_interval: 5
  credentials_path: "~/.hermes/wechat_credentials.json"
```

## 🔌 主要工具API

### `wechat_auth` - 认证登录
```bash
# 扫码登录（类似wx-robot-ilink登录流程）
/wechat_auth

# 仅生成二维码
/wechat_auth --qr_only true

# 清除凭证（登出）
/wechat_auth --logout
```

### `wechat_send_message` - 发送消息
```bash
# 发送文本
/wechat_send_message --to_user_id "wxid_xxx" --message "你好"

# 发送带上下文的回复
/wechat_send_message --to_user_id "wxid_xxx" --message "已处理" --context_token "ctx_123"
```

### `wechat_get_messages` - 接收消息
```bash
# 长轮询接收（30秒超时）
/wechat_get_messages --timeout 30

# 获取未读消息
/wechat_get_messages --only_unread true
```

### `wechat_status` - 状态检查
```bash
/wechat_status
# 返回：认证状态、轮询状态、队列大小、连接时间等
```

## 🎯 使用示例

### 场景1：基本认证和聊天
```bash
# 1. 认证
/wechat_auth
# ↑ 终端显示二维码，微信扫码登录

# 2. 发送测试消息
/wechat_send_message --to_user_id "wxid_测试" --message "hello"

# 3. 接收消息
/wechat_get_messages --timeout 10
```

### 场景2：集成到Hermes自动化流程
```bash
# 创建定时任务：每天早上9点发送问候
/cronjob create \
  --name "早安问候" \
  --schedule "0 9 * * *" \
  --skills "wechat_ilink" \
  --prompt "给微信好友wxid_xxx发送早安消息" \
  --deliver "origin"
```

### 场景3：独立运行测试
```bash
# 像使用wx-robot-ilink一样测试
python -m hermes_wechat_ilink --auth
python -m hermes_wechat_ilink --status
python -m hermes_wechat_ilink --send --to wxid_xxx --message "测试"
```

## 🔧 开发者指南

### 从wx-robot-ilink移植
```bash
# 如果你熟悉wx-robot-ilink，移植非常直接：

# 1. TypeScript auth.ts → Python auth_manager.py
# 2. TypeScript api.ts → Python wechat_client.py  
# 3. TypeScript types.ts → Python 中的类和枚举
# 4. TypeScript bot.ts → Hermes插件消息循环
```

### 开发环境设置
```bash
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink

# 安装开发依赖
make install-dev

# 运行测试
make test

# 代码检查
make lint

# 格式化代码
make format
```

### 代码结构对应表
| wx-robot-ilink文件 | Python实现 | 状态 |
|-------------------|------------|------|
| `src/weixin/auth.ts` | `auth_manager.py` | ✅ |
| `src/weixin/api.ts` | `wechat_client.py` | ✅ |
| `src/weixin/types.ts` | `wechat_client.py`中的类 | ✅ |
| `src/bot.ts` | `__init__.py`中的消息循环 | ✅ |
| `src/ai/chat.ts` | 使用Hermes AI | ⏸️ |

## 🚨 故障排除

### 常见问题

**1. 安装脚本失败**
```bash
# 手动执行安装步骤
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**2. 二维码无法显示**
```bash
# 确保安装二维码依赖
pip install qrcode[pil] pillow

# 检查终端是否支持
echo $TERM
```

**3. 认证失败**
```bash
# 清除旧凭证重新登录
/wechat_auth --logout
/wechat_auth

# 或独立运行
python -m hermes_wechat_ilink --logout
python -m hermes_wechat_ilink --auth
```

**4. Hermes找不到插件**
```bash
# 1. 确认插件已复制到正确位置
#    Hermes插件目录：plugins/memory/hermes_wechat_ilink/

# 2. 重启Hermes

# 3. 检查日志
tail -f ~/.hermes/logs/hermes.log
```

## 📄 协议与许可

- **软件许可证**: [MIT License](LICENSE)（与wx-robot-ilink相同）
- **协议来源**: 腾讯官方 `@tencent-weixin/openclaw-weixin`
- **参考项目**: [wx-robot-ilink](https://github.com/co-pine/wx-robot-ilink) (MIT License)

**重要提示**:
1. 使用微信官方API需遵守[腾讯服务条款](https://weixin.qq.com/cgi-bin/readtemplate?t=weixin_agreement&lang=zh_CN)
2. 插件仅供个人学习和开发测试使用
3. 禁止用于垃圾消息、欺诈、骚扰等非法用途

## 🤝 贡献与支持

### 从wx-robot-ilink移植贡献
- 熟悉wx-robot-ilink的开发者特别欢迎
- 可以直接基于其最新代码改进Python实现
- Issue中标注 `来自wx-robot-ilink` 标签

### 开发流程
```bash
# 1. Fork项目
# 2. 创建功能分支
git checkout -b feature/新功能

# 3. 修改代码并测试
make test
make lint

# 4. 提交PR
```

### 支持渠道
- GitHub Issues: https://github.com/liangminmx/hermes-wechat-ilink/issues
- 标签: `bug`, `enhancement`, `wx-robot-ilink-porting`

---

**立即开始使用**：
```bash
# 像使用wx-robot-ilink一样简单，但是Python版！
git clone https://github.com/liangminmx/hermes-wechat-ilink.git
cd hermes-wechat-ilink
./install.sh

# 作为Hermes插件或独立运行，你选择！
```

体验与wx-robot-ilink相同的功能，但深度集成Hermes AI助手生态！🚀

> 基于 [wx-robot-ilink](https://github.com/co-pine/wx-robot-ilink) 协议移植，为 Hermes Agent 量身定制。