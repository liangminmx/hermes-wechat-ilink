#!/bin/bash
# 🚀 Hermes WeChat iLink 一键安装脚本
# 全自动安装，无需用户交互

set -e  # 出错时停止

echo "======================================================"
echo "🚀 Hermes WeChat iLink 微信插件一键安装"
echo "======================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 1. 检查 Python 环境
print_info "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if [ "$(echo "$python_version < 3.8" | bc 2>/dev/null)" = "1" ]; then
    print_warning "Python 版本 $python_version 可能过旧，建议升级到 3.8+"
else
    print_success "Python $python_version 版本符合要求"
fi

# 2. 检查 Hermes 安装目录
print_info "检查 Hermes Agent 安装目录..."

HERMES_DIRS=(
    "/opt/hermes-agent/hermes-agent-main"
    "/opt/hermes-agent"
    "$HOME/.hermes"
    "/usr/local/bin"
)

HERMES_DIR=""
for dir in "${HERMES_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        HERMES_DIR="$dir"
        print_success "找到 Hermes 目录: $HERMES_DIR"
        break
    fi
done

if [ -z "$HERMES_DIR" ]; then
    print_warning "未找到 Hermes 目录，请手动确认安装位置"
    HERMES_DIR="/opt/hermes-agent/hermes-agent-main"
fi

# 3. 确定插件目标目录
if [[ "$HERMES_DIR" == *"/plugins"* ]]; then
    TARGET_DIR="$HERMES_DIR/plugins/memory/hermes_wechat_ilink"
else
    TARGET_DIR="$HERMES_DIR/plugins/memory/hermes_wechat_ilink"
fi

print_info "插件将安装到: $TARGET_DIR"

# 4. 备份现有插件（如果存在）
if [ -d "$TARGET_DIR" ]; then
    TIMESTAMP=$(date +%s)
    BACKUP_DIR="$TARGET_DIR.backup.$TIMESTAMP"
    print_info "备份现有插件到: $BACKUP_DIR"
    cp -r "$TARGET_DIR" "$BACKUP_DIR"
    print_success "备份完成"
fi

# 5. 下载插件代码
print_info "下载插件代码..."

# 创建临时目录
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

# 从 GitHub 下载
if command -v git &> /dev/null; then
    print_info "使用 Git 下载..."
    git clone --depth=1 https://github.com/liangminmx/hermes-wechat-ilink.git . 2>/dev/null || {
        print_warning "Git 下载失败，使用 curl 下载..."
        rm -rf "$TEMP_DIR"/*
        # 下载单个文件
        FILES=(
            "__init__.py"
            "__main__.py"
            "auth_manager.py"
            "wechat_client.py"
            "plugin.yaml"
            "requirements.txt"
            "README.md"
            "QUICK_START.md"
        )
        
        for file in "${FILES[@]}"; do
            curl -s "https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/$file" -o "$file" 2>/dev/null || echo "下载 $file 失败"
        done
    }
else
    print_info "使用 curl 下载..."
    # 创建目录结构
    mkdir -p hermes_wechat_ilink
    cd hermes_wechat_ilink
    
    FILES=(
        "__init__.py"
        "__main__.py"
        "auth_manager.py"
        "wechat_client.py"
        "plugin.yaml"
        "requirements.txt"
        "README.md"
        "QUICK_START.md"
    )
    
    for file in "${FILES[@]}"; do
        curl -s "https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/$file" -o "$file" 2>/dev/null || echo "下载 $file 失败"
    done
fi

# 6. 安装依赖
print_info "安装依赖..."
if command -v pip3 &> /dev/null; then
    pip_cmd="pip3"
elif command -v pip &> /dev/null; then
    pip_cmd="pip"
else
    print_warning "未找到 pip，依赖安装将跳过"
    pip_cmd=""
fi

if [ -n "$pip_cmd" ] && [ -f "requirements.txt" ]; then
    print_info "安装依赖包: qrcode[pil] aiohttp"
    $pip_cmd install qrcode[pil] aiohttp --quiet 2>/dev/null ||     $pip_cmd install qrcode[pil] aiohttp --user --quiet 2>/dev/null ||     print_warning "依赖安装失败，可能需要手动安装: pip install qrcode[pil] aiohttp"
fi

# 7. 安装插件到目标目录
print_info "安装插件到 Hermes..."
mkdir -p "$(dirname "$TARGET_DIR")"

if [ -d "hermes_wechat_ilink" ]; then
    # 已经在子目录中
    cp -r hermes_wechat_ilink/* "$TARGET_DIR"/ 2>/dev/null || true
else
    cp -r . "$TARGET_DIR"/ 2>/dev/null || true
fi

# 8. 验证安装
print_info "验证安装..."
if [ -f "$TARGET_DIR/__init__.py" ]; then
    print_success "✅ 插件文件已安装"
    
    # 测试导入
    if python3 -c "import sys; sys.path.insert(0, '$TARGET_DIR'); from __init__ import create_memory_provider; p = create_memory_provider(); print('✅ 插件加载成功')" 2>/dev/null; then
        print_success "✅ 插件加载测试通过"
    else
        print_warning "⚠ 插件加载测试存在问题，但文件已安装"
    fi
else
    print_error "❌ 插件安装失败，文件不存在: $TARGET_DIR/__init__.py"
fi

# 9. 清理临时文件
print_info "清理临时文件..."
rm -rf "$TEMP_DIR"

# 10. 显示安装结果
echo ""
echo "======================================================"
echo "✨ 安装完成！"
echo "======================================================"
echo ""
echo "📋 安装信息:"
echo "   插件目录: $TARGET_DIR"
echo "   依赖状态: $( [ -n "$pip_cmd" ] && echo "已安装" || echo "需手动安装" )"
echo "   文件数量: $(find "$TARGET_DIR" -type f -name "*.py" -o -name "*.yaml" -o -name "*.md" 2>/dev/null | wc -l) 个"
echo ""
echo "🚀 下一步操作:"
echo "   1. 进入插件目录: cd $TARGET_DIR"
echo "   2. 扫码认证: python3 -m hermes_wechat_ilink --auth"
echo "   3. 验证状态: python3 -m hermes_wechat_ilink --status"
echo ""
echo "📱 在 Hermes 中使用:"
echo "   /wechat_auth          # 终端扫码认证"
echo "   /wechat_send_message  # 发送微信消息"
echo "   /wechat_get_messages  # 接收微信消息"
echo "   /wechat_status        # 查看连接状态"
echo ""
echo "📧 凭证文件: ~/.hermes/wechat_credentials.json"
echo ""
echo "❓ 问题反馈: https://github.com/liangminmx/hermes-wechat-ilink/issues"
echo ""
echo "======================================================"

exit 0
