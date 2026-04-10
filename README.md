# Hermes WeChat iLink 插件 v2.0.2 (紧急修复版)

**完全修复 "No such file or directory" 错误**

## ✨ 修复内容
- ✅ 完整的 `__main__.py` 文件 - 插件现在可以运行
- ✅ 所有必需文件的完整性检查
- ✅ 简化的安装脚本
- ✅ 全局命令 `hermes-wechat` 创建

## 🚀 安装命令
```bash
curl -sL https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh | bash
```

## 📱 使用方法
安装后，直接运行:
```bash
hermes-wechat --auth      # 扫码认证
hermes-wechat --status    # 查看状态
hermes-wechat --help      # 查看帮助
```

## 📁 文件结构
```
hermes_wechat_ilink/
├── __init__.py      # 插件主文件
├── __main__.py      # ✅ 已修复的入口点
├── auth_manager.py  # 认证管理
├── wechat_client.py # WeChat客户端
└── plugin.yaml      # 插件配置
```

## 🔧 依赖安装
```bash
pip install qrcode[pil] aiohttp
```

版本: v2.0.2 | 维护者: 假装不单纯 | 仓库: https://github.com/liangminmx/hermes-wechat-ilink
