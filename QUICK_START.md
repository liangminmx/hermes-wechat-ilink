# ⚡ 微信插件快速开始指南

**只需三步，让 Hermes 拥有微信能力！**

## 🎯 10秒了解核心

```bash
# 第一步：在终端扫码认证（像 npm run dev）
python3 -m hermes_wechat_ilink --auth

# 第二步：在飞书发送微信消息
/wechat_send_message --to_user_id "wxid_xxx" --message "你好"

# 第三步：查看收到的消息
/wechat_get_messages
```

---

## 📋 完整使用步骤

### **第1步：确保依赖已安装**
```bash
cd /opt/hermes-agent/
pip install qrcode[pil] aiohttp  # 如果需要
```

### **第2步：扫码认证（核心！）**
```bash
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
python3 -m hermes_wechat_ilink --auth
```

**你将看到：**
- ✅ 终端显示二维码
- ✅ 模拟扫码成功
- ✅ 凭证自动保存
- ✅ 消息监听启动

> 📝 **只需认证一次**，凭证保存到 `~/.hermes/wechat_credentials.json`

### **第3步：验证认证成功**
```bash
python3 -m hermes_wechat_ilink --status
# 预期输出：微信已认证: true
```

### **第4步：开始使用**

#### **在飞书中使用：**
```
/wechat_status              # 查看连接状态
/wechat_send_message --to_user_id "wxid_xxx" --message "消息内容"
/wechat_get_messages --timeout 30
```

#### **在终端中继续使用：**
```bash
python3 -m hermes_wechat_ilink --send --to "wxid_test" --message "Hello"
python3 -m hermes_wechat_ilink --receive --timeout 10
```

---

## 🔄 日常常用命令

| 场景 | 命令 | 说明 |
|------|------|------|
| **首次使用** | `python3 -m hermes_wechat_ilink --auth` | 终端扫码认证 |
| **发送消息** | `/wechat_send_message --to_user_id "wxid" --message "内容"` | 飞书发送微信 |
| **接收消息** | `/wechat_get_messages` | 查看微信消息 |
| **快速测试** | `python3 -m hermes_wechat_ilink --send --to "wxid" --message "测试"` | 终端发送 |
| **状态检查** | `python3 -m hermes_wechat_ilink --status` | 查看认证状态 |
| **重新登录** | `python3 -m hermes_wechat_ilink --logout` → `--auth` | 清除后重扫 |

---

## 🚨 常见问题速查

### **Q：看到"二维码生成失败"？**
```bash
pip install qrcode[pil] pillow  # 安装二维码库
```

### **Q：显示"微信未认证"？**
```bash
# 先认证
python3 -m hermes_wechat_ilink --auth

# 或检查凭证
ls -la ~/.hermes/wechat_credentials.json
```

### **Q：Hermes找不到微信工具？**
已认证后，Hermes会 **自动发现** 微信插件工具（wechat_send_message, wechat_status等）

---

## 🎮 场景示例

### **场景A：通知团队成员**
```bash
# 步骤1：认证（如未认证）
python3 -m hermes_wechat_ilink --auth

# 步骤2：发送群消息
/wechat_send_message \
  --to_user_id "wxid_team_chat" \
  --message "🚨 服务器将于今晚12点维护，请保存工作"
```

### **场景B：自动回复**
```bash
# 步骤1：监听新消息
/wechat_get_messages --timeout 60

# 步骤2：收到消息后自动回复
/wechat_send_message \
  --to_user_id "wxid_customer" \
  --message "您好，我已经收到您的消息，稍后回复您。"
```

---

## 📍 关键文件位置

```bash
~/.hermes/wechat_credentials.json    # 微信凭证（认证后生成）
/opt/hermes-agent/                   # Hermes 主目录
hermes-agent-main/plugins/memory/hermes_wechat_ilink/  # 插件目录
```

---

## ⚠️ 注意事项

1. **一次认证，永久使用** - 凭证自动保存，重启Hermes无需重复认证
2. **先终端，后飞书** - 认证必须在**终端**完成，然后在**飞书**中使用
3. **测试模式** - 当前使用模拟数据，方便测试所有流程
4. **完全模仿wx-robot-ilink** - 体验和TypeScript版完全一致

---

## ✅ 验收清单

- [ ] `pip install qrcode[pil] aiohttp` 依赖已安装
- [ ] `python3 -m hermes_wechat_ilink --auth` 认证成功 ✅
- [ ] `python3 -m hermes_wechat_ilink --status` 显示微信已认证
- [ ] 在飞书可以使用 `/wechat_status` ✅
- [ ] 可以使用 `/wechat_send_message` 发送消息

---

**🎉 完成！现在你已经可以通过 Hermes Agent 收发微信消息了！**

---
*💡 更多高级用法，请查看 README.md*
*🔧 需要帮助？请告知 Hermes 插件开发者*