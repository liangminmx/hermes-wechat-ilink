#!/bin/bash
# 🚀 Hermes WeChat iLink 一键安装脚本 v2.0.1
# 修复版 - 解决依赖安装和文件下载问题

set -e

echo "======================================================"
echo "🚀 Hermes WeChat iLink 安装脚本 v2.0.1"
echo "🔧 修复依赖安装和文件下载问题"
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

# 2. 确定Hermes插件目录
print_info "查找 Hermes 安装目录..."

HERMES_PATHS=(
    "/opt/hermes-agent/hermes-agent-main"
    "/opt/hermes-agent"
    "$HOME/.hermes"
    "/usr/local/bin"
)

HERMES_DIR=""
for path in "${HERMES_PATHS[@]}"; do
    if [ -d "$path" ]; then
        HERMES_DIR="$path"
        print_success "找到 Hermes 目录: $HERMES_DIR"
        break
    fi
done

if [ -z "$HERMES_DIR" ]; then
    print_warning "未自动找到 Hermes 目录，使用默认路径"
    HERMES_DIR="/opt/hermes-agent/hermes-agent-main"
    print_info "将使用默认路径: $HERMES_DIR"
fi

TARGET_PLUGIN_DIR="$HERMES_DIR/plugins/memory/hermes_wechat_ilink"
print_info "插件将安装到: $TARGET_PLUGIN_DIR"

# 3. 创建目录
mkdir -p "$TARGET_PLUGIN_DIR"

# 4. 备份现有插件
if [ "$(ls -A "$TARGET_PLUGIN_DIR" 2>/dev/null)" ]; then
    BACKUP_DIR="$TARGET_PLUGIN_DIR.backup.$(date +%s)"
    print_info "备份现有插件到: $BACKUP_DIR"
    cp -r "$TARGET_PLUGIN_DIR" "$BACKUP_DIR"
    print_success "备份完成"
fi

# 5. 安装依赖（改进版）
print_info "安装依赖 (qrcode[pil] aiohttp)..."
DEPENDENCIES_INSTALLED=false

# 尝试多种安装方式
if command -v pip3 &> /dev/null; then
    print_info "使用 pip3 安装..."
    if pip3 install qrcode[pil] aiohttp --quiet 2>/dev/null; then
        DEPENDENCIES_INSTALLED=true
        print_success "依赖安装成功 (使用 pip3)"
    fi
fi

if [ "$DEPENDENCIES_INSTALLED" = "false" ] && command -v pip &> /dev/null; then
    print_info "使用 pip 安装..."
    if pip install qrcode[pil] aiohttp --quiet 2>/dev/null; then
        DEPENDENCIES_INSTALLED=true
        print_success "依赖安装成功 (使用 pip)"
    fi
fi

if [ "$DEPENDENCIES_INSTALLED" = "false" ]; then
    print_warning "自动依赖安装失败"
    print_info "将尝试不安装依赖继续，稍后可手动安装:"
    print_info "   pip install qrcode[pil] aiohttp"
    print_info "   pip3 install qrcode[pil] aiohttp"
    print_info "   python3 -m pip install qrcode[pil] aiohttp"
fi

# 6. 获取插件文件（修复版）
print_info "获取插件文件..."
cd "$TARGET_PLUGIN_DIR"

# 方法1: 尝试从Git克隆
if command -v git &> /dev/null; then
    print_info "使用Git下载插件..."
    TEMP_DIR=$(mktemp -d)
    if git clone --depth=1 https://github.com/liangminmx/hermes-wechat-ilink.git "$TEMP_DIR" 2>/dev/null; then
        print_success "Git克隆成功"
        # 复制文件
        if [ -f "$TEMP_DIR/hermes_wechat_ilink/__init__.py" ]; then
            cp -r "$TEMP_DIR/hermes_wechat_ilink"/* .
        else
            print_warning "插件文件结构异常"
        fi
        rm -rf "$TEMP_DIR"
    else
        print_warning "Git下载失败，使用curl下载"
    fi
fi

# 方法2: 直接curl下载（修复URL路径）
print_info "下载核心插件文件..."

# GitHub raw URL基础路径
GITHUB_BASE="https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main"

# 核心文件列表
CORE_FILES=(
    "hermes_wechat_ilink/__init__.py"
    "hermes_wechat_ilink/__main__.py"
    "hermes_wechat_ilink/auth_manager.py"
    "hermes_wechat_ilink/wechat_client.py"
    "hermes_wechat_ilink/plugin.yaml"
    "requirements.txt"
)

for file in "${CORE_FILES[@]}"; do
    FILENAME=$(basename "$file")
    
    # 使用更可靠的下载方式
    print_info "  下载: $FILENAME"
    
    # 尝试多个URL路径
    URLS=(
        "$GITHUB_BASE/$file"
        "https://cdn.jsdelivr.net/gh/liangminmx/hermes-wechat-ilink@main/$file"
        "https://raw.github.com/liangminmx/hermes-wechat-ilink/main/$file"
    )
    
    for url in "${URLS[@]}"; do
        if curl -sL "$url" -o "$FILENAME" 2>/dev/null; then
            if [ -s "$FILENAME" ]; then
                print_success "      ✅ 下载成功 (从 $(echo "$url" | cut -d'/' -f3))"
                break
            fi
        fi
    done
    
    if [ ! -s "$FILENAME" ]; then
        print_warning "      ⚠️  下载失败: $FILENAME"
    fi
done

# 7. 检查核心文件
print_info "验证文件..."
REQUIRED_FILES=("__init__.py" "__main__.py" "auth_manager.py" "wechat_client.py")
MISSING_COUNT=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "  ✅ $file (存在, $(wc -l < "$file") 行)"
    else
        print_error "  ❌ $file (缺失)"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done

if [ $MISSING_COUNT -gt 0 ]; then
    print_warning "⚠️  缺少 $MISSING_COUNT 个核心文件"
    print_info "可以从备份恢复或重新下载"
fi

# 8. 创建全局命令（简化但可靠）
print_info "创建全局命令..."

GLOBAL_CMD="/usr/local/bin/hermes-wechat"

cat > "$GLOBAL_CMD" << 'EOF'
#!/bin/bash
# Hermes WeChat iLink 命令行工具

# 优先使用已知的插件目录
PLUGIN_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"

# 检查目录是否存在
if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ 错误: 插件目录不存在: $PLUGIN_DIR"
    echo "📋 运行路径示例:"
    echo "   cd /opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"
    echo "   python3 __main__.py --auth"
    exit 1
fi

# 切换到插件目录
cd "$PLUGIN_DIR" || {
    echo "❌ 无法进入插件目录: $PLUGIN_DIR"
    exit 1
}

# 检查依赖（只检查，不安装）
if ! python3 -c "import qrcode, aiohttp" 2>/dev/null; then
    echo "⚠️  缺少依赖，请先安装:"
    echo "   pip install qrcode[pil] aiohttp"
    echo ""
fi

# 运行插件
exec python3 __main__.py "$@"
EOF

chmod +x "$GLOBAL_CMD"
print_success "全局命令创建: $GLOBAL_CMD"

# 9. 创建备用的本地脚本
print_info "创建备用脚本..."
cat > "$TARGET_PLUGIN_DIR/run.sh" << 'EOF'
#!/bin/bash
# Hermes WeChat iLink 本地运行脚本

cd "$(dirname "$0")"

echo "🚀 Hermes 微信插件运行脚本"

# 检查文件
if [ ! -f "__main__.py" ]; then
    echo "❌ 错误: __main__.py 不存在"
    exit 1
fi

# 运行
python3 __main__.py "$@"
EOF

chmod +x "$TARGET_PLUGIN_DIR/run.sh"

# 10. 显示安装结果
echo ""
echo "======================================================"
echo "✨ 安装完成！"
echo "======================================================"
echo ""
echo "📋 安装总结:"
echo "   插件目录: $TARGET_PLUGIN_DIR"
echo "   全局命令: $GLOBAL_CMD"
if [ "$DEPENDENCIES_INSTALLED" = "true" ]; then
    echo "   依赖状态: ✅ 已安装 (qrcode[pil], aiohttp)"
else
    echo "   依赖状态: ⚠️  需要手动安装"
    echo "       命令: pip install qrcode[pil] aiohttp"
fi
echo "   核心文件: $((${#REQUIRED_FILES[@]} - MISSING_COUNT))/4 个已安装"
echo ""

echo "🚀 使用方式:"
echo ""
echo "   1. 全局命令 (推荐):"
echo "      hermes-wechat --auth"
echo "      hermes-wechat --status"
echo ""
echo "   2. 直接运行 (最可靠):"
echo "      cd $TARGET_PLUGIN_DIR && python3 __main__.py --auth"
echo ""
echo "   3. 本地脚本:"
echo "      cd $TARGET_PLUGIN_DIR && ./run.sh --auth"
echo ""

if [ $MISSING_COUNT -gt 0 ]; then
    echo "⚠️  注意: 缺少 $MISSING_COUNT 个核心文件"
    echo "   运行前请确保以下文件存在:"
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$TARGET_PLUGIN_DIR/$file" ]; then
            echo "      ❌ $file"
        fi
    done
    echo ""
fi

echo "📱 立即开始认证:"
echo "   hermes-wechat --auth"
echo ""
echo "   或: cd $TARGET_PLUGIN_DIR && python3 __main__.py --auth"
echo ""
echo "❓ 问题反馈: https://github.com/liangminmx/hermes-wechat-ilink/issues"
echo ""
echo "======================================================"

# 列出安装的文件
echo "📁 安装的文件:"
cd "$TARGET_PLUGIN_DIR" && ls -la *.py *.yaml *.sh 2>/dev/null || echo "无文件列表"