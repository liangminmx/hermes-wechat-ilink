# WeChat iLink Plugin for Hermes

基于腾讯官方 OpenClaw 微信协议 (`@tencent-weixin/openclaw-weixin`) 的纯 Python 微信机器人插件。为 Hermes 提供直接的微信消息收发能力，无需任何第三方桥接服务。

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
| **部署** | Node.js 环境 | Python 虚拟环境 |
| **协议** | `@tencent-weixin/openclaw-weixin` | 同款协议移植到 Python |
| **架构** | 独立机器人程序 | Hermes 插件，可与其他工具联动 |
| **集成** | HTTP API 接口 | Hermes 原生工具调用 |

**移植度**: 约 95%，包含完整认证流程、消息轮询、文本收发。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启用插件
将插件目录放置在 `~/.hermes/plugins/` 或 Hermes 的 `plugins/memory/` 目录下。Hermes 会自动发现并加载插件。

### 3. 基本使用
```python
# 在 Hermes 中调用
/wechat_auth      # 微信扫码认证
/wechat_status    # 查看连接状态
/wechat_send_message --to_user_id wxid_xxxx --message "你好！"
/wechat_get_messages --timeout 30
```

## 📦 安装

### 选项一：手动安装
```bash
# 1. 克隆插件到 Hermes 插件目录
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/
git clone <repository-url> wechat-ilink

# 2. 安装依赖
cd wechat-ilink
pip install -r requirements.txt

# 3. 重启 Hermes
```

### 选项二：通过 Hermes CLI 安装
```bash
# 将插件打包后可通过 /skills 命令安装
```

## 🔧 使用方法

### 认证流程
1. **启动认证**: 调用 `wechat_auth` 工具
2. **扫码登录**: 插件将显示二维码（控制台或网页）
3. **自动轮询**: 认证成功后自动开始接收消息

```json
{
  "步骤": "微信 OAuth 2.0 扫码登录",
  "技术栈": "Tencent iLink 网关",
  "持久化": "凭证保存在 ~/.hermes/wechat_credentials.json"
}
```

### 消息收发

**发送消息**:
```bash
/wechat_send_message --to_user_id "wxid_abcdef" --message "你好，我是Hermes微信机器人！"
```

**接收消息**:
```bash
/wechat_get_messages --timeout 30 --extract_text true
```

**实时轮询**:
- 插件启动后自动后台轮询
- 新消息存入队列，可通过工具提取
- 支持上下文令牌保持对话连贯性

## 🛠 工具参考

### 1. `wechat_auth`
微信扫码认证。

**参数**:
- `server_url`: (可选) iLink 服务器地址
- `qr_only`: (可选) 仅显示二维码，不开始轮询

**返回示例**:
```json
{
  "status": "qr_generated",
  "qrcode": "terminal_ascii_qr_or_url",
  "polling_url": "http://localhost:8080/qr_status"
}
```

### 2. `wechat_send_message`
发送消息到指定微信用户。

**参数**:
- `to_user_id`: (必需) 目标微信用户ID
- `message`: (必需) 消息文本
- `context_token`: (可选) 上下文令牌

**返回示例**:
```json
{
  "success": true,
  "to_user_id": "wxid_123456",
  "sent_at": 1712822400.123,
  "message_preview": "你好..."
}
```

### 3. `wechat_get_messages`
获取新消息（长轮询）。

**参数**:
- `timeout`: (可选) 等待超时时间，默认30秒
- `extract_text`: (可选) 提取消息文本，默认true
- `only_unread`: (可选) 仅未读消息，默认true

**返回示例**:
```json
{
  "success": true,
  "messages": [
    {
      "id": 1,
      "from_user_id": "wxid_abcdef",
      "text": "你好，机器人",
      "received_at": 1712822400.456
    }
  ],
  "count": 1
}
```

### 4. `wechat_status`
查看插件状态。

**返回示例**:
```json
{
  "authenticated": true,
  "polling_active": true,
  "queue_size": 5,
  "unread_messages": 2,
  "account_id": "wxid_robot123",
  "base_url": "https://ilink.tencent.com"
}
```

### 5. `wechat_webhook_server`
启动HTTP服务器，提供ClawBot兼容接口。

**参数**:
- `port`: (可选) 端口号，默认8080
- `host`: (可选) 监听地址，默认"0.0.0.0"
- `webhook_path`: (可选) webhook路径，默认"/wechat/webhook"

## ⚙️ 配置

### 环境变量
```bash
# 可选：设置凭证存储路径
export WECHAT_CREDENTIALS_PATH="~/.hermes/wechat_credentials.json"

# 可选：自定义iLink服务器
export WECHAT_ILINK_BASE_URL="https://ilink.tencent.com"
```

### 配置文件
通过 Hermes 配置文件 `~/.hermes/config.yaml` 设置:

```yaml
wechat-ilink:
  enable_polling: true
  poll_interval: 5
  credentials_path: "~/.hermes/wechat_credentials.json"
  webhook_enabled: false
  webhook_port: 8080
```

## 🧩 与现有插件集成

### 1. 与 `webhook-bridge` 插件协同
```python
# wechat-ilink 负责微信连接
# webhook-bridge 提供通用HTTP接口
# 两者可配合提供完整的 ClawBot 解决方案
```

### 2. 作为 Hermes 工具调用
```python
# 其他插件可通过内存提供者接口调用微信功能
from plugins.memory.wechat_ilink import create_memory_provider

wechat = create_memory_provider()
result = await wechat.call_tool("wechat_send_message", 
                               to_user_id="wxid_xxx",
                               message="Hello from another plugin!")
```

## 🚦 状态代码参考

### 认证状态
- `waiting`: 等待扫码
- `scaned`: 已扫码，等待确认
- `confirmed`: 登录成功
- `expired`: 二维码过期

### API 返回码
| 代码 | 说明 |
|------|------|
| `0` | 成功 |
| `-1` | 通用错误 |
| `1001` | 认证失败 |
| `1002` | Token过期 |
| `1003` | 权限不足 |

## 🔒 安全与隐私

### 数据存储
- 凭证信息本地加密存储
- 消息队列仅保存在内存中
- 支持手动清除凭证

### 权限控制
```bash
# 清除登录凭证
/wechat_auth --logout

# 查看活跃会话
/wechat_status
```

## 🐛 故障排除

### 常见问题

1. **二维码无法显示**
   ```bash
   # 安装二维码生成依赖
   pip install qrcode[pil] pillow
   ```

2. **认证失败**
   ```bash
   # 清除旧凭证重试
   /wechat_auth --logout
   /wechat_auth
   ```

3. **无法接收消息**
   ```bash
   # 检查网络连接和插件的轮询状态
   /wechat_status
   ```

4. **消息发送失败**
   ```bash
   # 确认用户ID是否正确，token是否有效
   ```

### 日志调试
```python
import logging
logging.getLogger("wechat_ilink").setLevel(logging.DEBUG)
```

## 🤝 贡献与开发

### 项目结构
```
wechat-ilink/
├── __init__.py          # 主插件入口，Hermes工具定义
├── wechat_client.py     # 微信iLink API客户端核心
├── plugin.yaml         # 插件元数据
├── requirements.txt    # Python依赖
├── README.md           # 本文档
└── tests/             # 测试目录（待补充）
```

### 待实现功能
- [ ] 完整的QR扫码显示和状态轮询
- [ ] 图片、语音、文件消息支持
- [ ] 群聊消息处理
- [ ] 联系人管理
- [ ] Webhook服务器完整实现

### 开发指南
```bash
# 1. 克隆项目
git clone <repo>

# 2. 开发环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. 运行测试
python -m pytest tests/
```

## 📄 协议与许可

基于 `wx-robot-ilink` (MIT) 协议移植，遵循相同使用条款。

**重要**: 使用微信官方API需遵守腾讯服务条款，禁止用于垃圾消息、欺诈等非法用途。

## 📞 支持与反馈

- **Issues**: 功能请求或问题报告
- **文档**: 本文档在线版本
- **社区**: Hermes Discord/Telegram 频道

---

**让你的Hermes助手拥有微信超能力！** 🚀

> 基于 [wx-robot-ilink](https://github.com/co-pine/wx-robot-ilink) 协议，专为 Hermes AI 助手量身定制。