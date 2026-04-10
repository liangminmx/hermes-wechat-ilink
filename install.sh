#!/bin/bash
# 安装脚本 - 类似wx-robot-ilink的npm install体验
# 作者: liangminmx
# 版本: 1.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 输出带颜色的消息
info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 检查是否在正确的目录
check_directory() {
    if [ ! -f "requirements.txt" ] || [ ! -f "setup.py" ]; then
        error "请在插件根目录运行此脚本"
    fi
    info "检查目录结构... ✓"
}

# 检查Python环境
check_python() {
    if ! command -v python3 &> /dev/null; then
        error "未找到python3，请先安装Python 3.8+"
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if [ $(echo "$python_version < 3.8" | bc) -eq 1 ]; then
        error "需要Python 3.8+，当前版本: $python_version"
    fi
    
    info "Python版本: $python_version ✓"
}

# 安装依赖
install_dependencies() {
    info "安装Python依赖..."
    
    # 创建虚拟环境（可选）
    if [ ! -d "venv" ] && [ "${SKIP_VENV:-false}" != "true" ]; then
        warn "创建虚拟环境（建议）"
        python3 -m venv venv
        source venv/bin/activate
    fi
    
    # 安装依赖
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # 检查二维码依赖
    if ! python3 -c "import qrcode" &> /dev/null; then
        warn "安装二维码生成依赖..."
        pip install qrcode[pil] pillow
    fi
    
    info "依赖安装完成 ✓"
}

# 设置环境配置
setup_env() {
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        info "创建环境配置文件..."
        cp .env.example .env
        warn "请编辑 .env 文件并根据需要修改配置"
        echo "  可配置项:"
        echo "    - WECHAT_POLL_INTERVAL (轮询间隔)"
        echo "    - WECHAT_DEBUG (调试模式)"
        echo "    - WECHAT_WEBHOOK_ENABLED (启用webhook)"
    fi
    
    # 检查Hermes插件目录
    local hermes_plugins_dir=""
    
    # 尝试常见位置
    if [ -d "/opt/hermes-agent/hermes-agent-main/plugins/memory" ]; then
        hermes_plugins_dir="/opt/hermes-agent/hermes-agent-main/plugins/memory"
    elif [ -d "$HOME/.hermes/plugins" ]; then
        hermes_plugins_dir="$HOME/.hermes/plugins"
    fi
    
    if [ -n "$hermes_plugins_dir" ]; then
        info "Hermes插件目录: $hermes_plugins_dir"
        
        # 复制插件到Hermes目录
        local target_dir="$hermes_plugins_dir/hermes_wechat_ilink"
        if [ ! -d "$target_dir" ]; then
            warn "复制插件到Hermes目录..."
            mkdir -p "$target_dir"
            cp -r hermes_wechat_ilink/__init__.py "$target_dir/"
            cp -r hermes_wechat_ilink/wechat_client.py "$target_dir/"
            cp plugin.yaml "$target_dir/" 2>/dev/null || true
        fi
    fi
}

# 验证安装
verify_installation() {
    info "验证插件安装..."
    
    # 测试Python导入
    if python3 -c "import hermes_wechat_ilink; print('✓ 成功导入插件')"; then
        info "Python导入测试通过 ✓"
    else
        warn "Python导入测试失败"
    fi
    
    echo ""
    echo "================================"
    echo "🎉 安装完成！"
    echo "================================"
    echo ""
    echo "下一步操作："
    echo "1. 启动 Hermes Agent"
    echo "2. 在 Hermes 中使用以下工具："
    echo ""
    echo "   /wechat_auth            # 微信登录认证"
    echo "   /wechat_status          # 查看状态"
    echo "   /wechat_send_message    # 发送消息"
    echo "   /wechat_get_messages    # 接收消息"
    echo ""
    echo "3. 首次使用执行 /wechat_auth 扫码登录"
    echo ""
    echo "文档：https://github.com/liangminmx/hermes-wechat-ilink"
    echo "问题反馈：https://github.com/liangminmx/hermes-wechat-ilink/issues"
    echo ""
}

# 显示帮助
show_help() {
    echo "使用方法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help      显示此帮助信息"
    echo "  --no-venv       跳过虚拟环境创建"
    echo "  --skip-copy     跳过复制到Hermes目录"
    echo ""
    echo "示例:"
    echo "  $0              完整安装"
    echo "  $0 --no-venv    不使用虚拟环境"
    echo ""
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --no-venv)
            SKIP_VENV=true
            shift
            ;;
        --skip-copy)
            SKIP_COPY=true
            shift
            ;;
        *)
            warn "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
done

# 主函数
main() {
    echo ""
    echo "================================"
    echo "Hermes WeChat iLink 插件安装"
    echo "================================"
    echo ""
    
    check_directory
    check_python
    install_dependencies
    setup_env
    verify_installation
}

# 运行主函数
main "$@"