#!/bin/bash
# Hermes WeChat 紧急修复安装脚本 v2.0.2

echo "🚀 Hermes WeChat iLink Plugin v2.0.2 (紧急修复)"
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 插件目录
PLUGIN_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"
echo "插件目录: $PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"

# 核心文件
GITHUB_BASE="https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/hermes_wechat_ilink"
FILES="__init__.py __main__.py auth_manager.py wechat_client.py plugin.yaml requirements.txt"

echo "安装核心文件..."
for file in $FILES; do
    echo "  下载: $file"
    curl -sL "$GITHUB_BASE/$file" -o "$PLUGIN_DIR/$file" 2>/dev/null && echo "    ✅ 成功" || echo "    ❌ 失败"
done

# 创建全局命令
echo "创建全局命令..."
cat > /usr/local/bin/hermes-wechat << 'CMEOF'
#!/bin/bash
cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink
python3 __main__.py "$@"
CMEOF

chmod +x /usr/local/bin/hermes-wechat

echo ""
echo "✅ 安装完成!"
echo "可用命令: hermes-wechat --help"
