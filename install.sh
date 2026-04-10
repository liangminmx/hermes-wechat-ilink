#!/bin/bash
# 🚀 Hermes WeChat iLink 安装脚本 v2.0.4
# 完全修复版 - 解决所有已知问题

echo "=================================================="
echo "🚀 Hermes WeChat iLink Plugin v2.0.4"
echo "✨ 完全修复版 - 解决所有已知问题"
echo "=================================================="

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

# 检测系统
print_info "检测系统环境..."
if [ -f /etc/debian_version ]; then
    print_info "检测到 Debian/Ubuntu 系统"
    DEBIAN_LIKE=true
else
    DEBIAN_LIKE=false
fi

# 插件目录
PLUGIN_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"
print_info "插件目录: $PLUGIN_DIR"
mkdir -p "$PLUGIN_DIR"
cd "$PLUGIN_DIR"

# 备份现有文件
if [ "$(ls -A . 2>/dev/null)" ]; then
    BACKUP_DIR="$PLUGIN_DIR.backup.$(date +%s)"
    cp -r . "$BACKUP_DIR"
    print_success "备份到: $BACKUP_DIR"
fi

# 1. 安装核心文件
print_info "安装插件文件..."
echo ""

GITHUB_BASE="https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/hermes_wechat_ilink"
FILES=(
    "__init__.py"
    "__main__.py"
    "auth_manager.py"
    "wechat_client.py"
    "plugin.yaml"
    "requirements.txt"
)

for file in "${FILES[@]}"; do
    print_info "  下载: $file"
    
    # 尝试多个源
    if curl -sL "$GITHUB_BASE/$file" -o "$file" 2>/dev/null; then
        lines=$(wc -l < "$file" 2>/dev/null || echo "?")
        print_success "      ✅ 成功 ($lines 行)"
    else
        print_warning "      ❌ 下载失败，使用备用源..."
        # 备用源
        curl -sL "https://cdn.jsdelivr.net/gh/liangminmx/hermes-wechat-ilink@main/hermes_wechat_ilink/$file" -o "$file" 2>/dev/null || \
        print_error "      ❌ 所有源都失败"
    fi
done

echo ""
print_info "创建备用运行脚本..."

# 创建run.sh
cat > run.sh << 'EOF'
#!/bin/bash
# Hermes微信插件运行脚本

cd "$(dirname "$0")"

echo "🚀 Hermes WeChat Plugin"
echo "📅 $(date '+%Y-%m-%d %H:%M:%S')"

if [ ! -f "__main__.py" ]; then
    echo "❌ 错误: __main__.py 不存在"
    exit 1
fi

python3 __main__.py "$@"
EOF

chmod +x run.sh
print_success "创建 run.sh"

# 2. 处理依赖安装
echo ""
print_info "处理依赖安装 (Debian兼容模式)..."

if [ "$DEBIAN_LIKE" = true ]; then
    echo ""
    echo "📋 Debian/Ubuntu 23.10+ 依赖安装选项:"
    echo "   1) 使用系统包管理器 (推荐)"
    echo "   2) 创建虚拟环境"
    echo "   3) 使用 pipx"
    echo "   4) 跳过依赖安装"
    echo ""
    
    if [ -f /tmp/hermes_auto_install ]; then
        CHOICE="1"
    else
        read -p "请选择 (1-4) [1]: " CHOICE
        CHOICE=${CHOICE:-1}
    fi
    
    print_info "您选择了: 选项 $CHOICE"
    
    case $CHOICE in
        1)
            print_info "使用系统包管理器安装..."
            apt update
            apt install -y python3-qrcode python3-aiohttp python3-pipx || {
                print_warning "系统包安装失败，尝试其他方法..."
                apt install -y python3-pip
                pip install qrcode[pil] aiohttp --break-system-packages
            }
            ;;
        2)
            print_info "创建虚拟环境..."
            VENV_DIR="/opt/hermes-wechat-venv"
            python3 -m venv "$VENV_DIR"
            source "$VENV_DIR/bin/activate"
            pip install qrcode[pil] aiohttp
            deactivate
            print_success "虚拟环境创建在: $VENV_DIR"
            ;;
        3)
            print_info "使用 pipx..."
            # 先安装pipx
            apt install -y pipx
            pipx ensurepath
            pipx install qrcode[pil]
            pipx inject qrcode[pil] Pillow
            pipx install aiohttp
            ;;
        4)
            print_warning "跳过依赖安装"
            ;;
        *)
            print_error "无效选择，使用默认选项1"
            apt install -y python3-qrcode python3-aiohttp 2>/dev/null || true
            ;;
    esac
else
    # 非Debian系统
    print_info "使用标准pip安装..."
    pip install qrcode[pil] aiohttp 2>/dev/null || \
    pip3 install qrcode[pil] aiohttp 2>/dev/null || \
    print_warning "pip安装失败，请手动安装"
fi

# 3. 创建全局命令
echo ""
print_info "创建全局命令..."

# 检测系统Python环境并创建合适的命令
cat > /tmp/hermes-wechat-global << 'EOF'
#!/bin/bash
# Hermes WeChat iLink 全局命令 v2.0.3
# 自动适应Debian/Ubuntu系统

PLUGIN_DIR="/opt/hermes-agent/hermes-agent-main/plugins/memory/hermes_wechat_ilink"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ 错误: 插件目录不存在"
    echo "📋 请先运行安装脚本:"
    echo "   curl -sL https://raw.githubusercontent.com/liangminmx/hermes-wechat-ilink/main/install.sh | bash"
    exit 1
fi

cd "$PLUGIN_DIR" || {
    echo "❌ 无法进入插件目录"
    exit 1
}

# 检查依赖是否安装
check_deps() {
    if ! python3 -c "import qrcode, aiohttp" 2>/dev/null; then
        echo ""
        echo "⚠️  缺少依赖检测:"
        python3 -c "
try:
    import qrcode
    print('  ✅ qrcode模块: 已安装')
except ImportError:
    print('  ❌ qrcode模块: 未安装')
try:
    import aiohttp
    print('  ✅ aiohttp模块: 已安装')
except ImportError:
    print('  ❌ aiohttp模块: 未安装')
" 2>/dev/null || echo "无法检测依赖"
        
        echo ""
        echo "📋 Debian/Ubuntu用户请运行:"
        echo "   sudo apt install python3-qrcode python3-aiohttp"
        echo "   或"
        echo "   pip install qrcode[pil] aiohttp --break-system-packages"
        echo ""
    fi
}

check_deps

# 运行插件
if [ -f "__main__.py" ]; then
    python3 __main__.py "$@"
else
    echo "❌ 错误: __main__.py 不存在"
    ls -la
    exit 1
fi
EOF

# 安装全局命令
if command -v sudo > /dev/null; then
    sudo cp /tmp/hermes-wechat-global /usr/local/bin/hermes-wechat
    sudo chmod +x /usr/local/bin/hermes-wechat
else
    cp /tmp/hermes-wechat-global /usr/local/bin/hermes-wechat
    chmod +x /usr/local/bin/hermes-wechat
fi

print_success "全局命令创建: hermes-wechat"

# 4. 验证安装
echo ""
print_info "验证安装..."

VALID_FILES=0
TOTAL_FILES=${#FILES[@]}

for file in "${FILES[@]}"; do
    if [ -f "$file" ] && [ -s "$file" ]; then
        VALID_FILES=$((VALID_FILES + 1))
    fi
done

if [ $VALID_FILES -eq $TOTAL_FILES ]; then
    print_success "✅ 所有 $TOTAL_FILES 个文件都安装成功"
else
    print_warning "⚠️  只有 $VALID_FILES/$TOTAL_FILES 个文件安装成功"
fi

# 5. 显示安装总结
echo ""
echo "=================================================="
echo "✨ 安装完成！ (v2.0.4 - 完全修复版)"
echo "=================================================="
echo ""
echo "📋 安装总结:"
echo "   插件目录: $PLUGIN_DIR"
echo "   文件状态: $VALID_FILES/$TOTAL_FILES 个文件"
echo "   全局命令: hermes-wechat"
echo ""
echo "🚀 可用的命令:"
echo "   hermes-wechat --help      # 查看帮助"
echo "   hermes-wechat --status    # 查看状态"
echo "   hermes-wechat --auth      # 开始认证"
echo ""
echo "🔧 依赖检查 (如果显示未安装):"
echo "   sudo apt install python3-qrcode python3-aiohttp"
echo "   或"
echo "   pip install qrcode[pil] aiohttp --break-system-packages"
echo ""
echo "📁 备用运行方式:"
echo "   cd $PLUGIN_DIR && ./run.sh --auth"
echo ""
echo "❓ 问题反馈: https://github.com/liangminmx/hermes-wechat-ilink/issues"
echo ""
echo "=================================================="