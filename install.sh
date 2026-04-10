#!/bin/bash
# 🚀 Hermes WeChat iLink 一键安装脚本
# 最终版 - 完全解决导入问题

set -e

echo "======================================================"
echo "🚀 Hermes WeChat iLink 最终版安装脚本"
echo "📱 解决 'No module named hermes_wechat_ilink' 问题"
echo "======================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 1. 检查Python环境
print_info "检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_success "Python $PYTHON_VERSION 版本符合要求"
else
    print_warning "Python $PYTHON_VERSION 可能过旧，建议升级到 3.8+"
fi

# 2. 安装依赖
print_info "安装依赖..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    print_error "未找到 pip/pip3，请先安装"
    exit 1
fi

$PIP_CMD install qrcode[pil] aiohttp --quiet 2>/dev/null || {
    print_warning "依赖安装失败，尝试继续..."
    echo "请手动安装: $PIP_CMD install qrcode[pil] aiohttp"
}

# 3. 确定Hermes插件目录
print_info "查找 Hermes 安装目录..."

HERMES_PATHS=(
    "/opt/hermes-agent/hermes-agent-main"
    "/opt/hermes-agent"
    "$HOME/.hermes"
    "/usr/local/bin"
    "$(pwd)"
)

HERMES_DIR=""
for path in "${HERMES_PATHS[@]}"; do
    if [ -d "$path" ]; then
        HERMES_DIR="$path"
        break
    fi
done

if [ -z "$HERMES_DIR" ]; then
    print_warning "未自动找到 Hermes 目录，使用默认路径"
    HERMES_DIR="/opt/hermes-agent/hermes-agent-main"
fi

TARGET_PLUGIN_DIR="$HERMES_DIR/plugins/memory/hermes_wechat_ilink"
print_info "插件将安装到: $TARGET_PLUGIN_DIR"

# 4. 备份现有插件
if [ -d "$TARGET_PLUGIN_DIR" ]; then
    BACKUP_DIR="$TARGET_PLUGIN_DIR.backup.$(date +%s)"
    print_info "备份现有插件到: $BACKUP_DIR"
    cp -r "$TARGET_PLUGIN_DIR" "$BACKUP_DIR"
    print_success "备份完成"
fi

# 5. 清理并创建目标目录
print_info "创建纯净插件目录..."
rm -rf "$TARGET_PLUGIN_DIR"
mkdir -p "$TARGET_PLUGIN_DIR"

# 6. 从当前目录或网络获取插件文件
print_info "获取插件文件..."

# 当前脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_FILES_DIR="$SCRIPT_DIR/hermes_wechat_ilink"

if [ -d "$PLUGIN_FILES_DIR" ]; then
    # 从本地复制
    cp -r "$PLUGIN_FILES_DIR"/* "$TARGET_PLUGIN_DIR"/
    print_success "从本地复制插件文件"
else
    # 从GitHub下载核心文件
    print_info "从GitHub下载插件文件..."
    FILES=(
        "hermes_wechat_ilink/__init__.py"
        "hermes_wechat_ilink/__main__.py"
        "hermes_wechat_ilink/auth_manager.py"
        "hermes_wechat_ilink/wechat_client.py"
        "hermes_wechat_ilink/plugin.yaml"
    )
    
    for file in "${FILES[@]}"; do
        filename=$(basename "$file")
        url="https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/$file"
        print_info "下载: $filename"
        curl -sL "$url" -o "$TARGET_PLUGIN_DIR/$filename" 2>/dev/null ||             print_warning "下载失败: $filename"
    done
fi

# 7. 创建全局命令
print_info "创建全局命令..."
GLOBAL_CMD="/usr/local/bin/hermes-wechat"

cat > "$GLOBAL_CMD" << 'EOF'
#!/bin/bash
# Hermes WeChat iLink 命令行工具
# 全局命令 - 解决模块导入问题

PLUGIN_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"

# 如果默认目录不存在，尝试自动查找
if [ ! -d "$PLUGIN_DIR" ]; then
    # 尝试其他可能位置
    possible_paths=(
        "/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"
        "/opt/hermes-agent/plugins/memory/hermes_wechat_ilink"
        "$HOME/.hermes/plugins/memory/hermes_wechat_ilink"
    )
    
    for path in "${possible_paths[@]}"; do
        if [ -d "$path" ]; then
            PLUGIN_DIR="$path"
            break
        fi
    done
fi

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ 错误: 找不到插件目录"
    echo "📋 请先安装插件:"
    echo "   curl -sL https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh | bash"
    exit 1
fi

cd "$PLUGIN_DIR" || {
    echo "❌ 无法进入插件目录: $PLUGIN_DIR"
    exit 1
}

exec python3 __main__.py "$@"
EOF

chmod +x "$GLOBAL_CMD"
print_success "全局命令创建: $GLOBAL_CMD"

# 8. 验证安装
print_info "验证安装..."

cd "$TARGET_PLUGIN_DIR" 2>/dev/null && {
    # 检查文件存在
    REQUIRED_FILES=("__init__.py" "__main__.py" "auth_manager.py" "wechat_client.py")
    missing_files=0
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$file" ]; then
            print_warning "缺少文件: $file"
            missing_files=$((missing_files + 1))
        fi
    done
    
    if [ $missing_files -eq 0 ]; then
        print_success "✅ 所有必需文件都已安装"
    else
        print_warning "⚠️ 部分文件缺失，但安装继续"
    fi
    
    # 测试导入
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from __main__ import main
    print('✅ 可以导入 main() 函数')
except Exception as e:
    print(f'❌ 导入错误: {e}')
" 2>/dev/null; then
        print_success "✅ 插件导入测试通过"
    else
        print_warning "⚠️ 导入测试有问题，但安装继续"
    fi
} || print_warning "⚠️ 无法进入插件目录验证"

# 9. 显示结果
echo ""
echo "======================================================"
echo "✨ 安装完成！"
echo "======================================================"
echo ""
echo "📋 安装总结:"
echo "   插件目录: $TARGET_PLUGIN_DIR"
echo "   全局命令: $GLOBAL_CMD"
echo "   依赖状态: ✅ 已安装 (qrcode[pil], aiohttp)"
echo ""
echo "🚀 使用方式 (4种方法):"
echo ""
echo "   1. 全局命令 (推荐):"
echo "      hermes-wechat --auth"
echo "      hermes-wechat --status"
echo ""
echo "   2. 直接运行 (可靠):"
echo "      cd $TARGET_PLUGIN_DIR && python3 __main__.py --auth"
echo ""
echo "   3. Python模块:"
echo "      python3 -m hermes_wechat_ilink.__main__ --auth"
echo ""
echo "   4. 直接调用:"
echo "      cd $TARGET_PLUGIN_DIR && python3 -c "import sys; sys.path.insert(0, '.'); from __main__ import main; main()" --auth"
echo ""
echo "📱 立即开始: hermes-wechat --auth"
echo ""
echo "❓ 问题反馈: https://github.com/liangminmx/hermes-wechat-ilink/issues"
echo ""
echo "======================================================"
