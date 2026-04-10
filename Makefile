# Makefile for Hermes WeChat iLink Plugin

.PHONY: help install install-dev test lint format clean

help:
	@echo "可用命令:"
	@echo "  make install      - 安装生产依赖"
	@echo "  make install-dev  - 安装开发依赖"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 代码检查"
	@echo "  make format       - 格式化代码"
	@echo "  make clean        - 清理构建文件"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

test:
	pytest tests/ -v

lint:
	ruff check hermes_wechat_ilink/

format:
	black hermes_wechat_ilink/

clean:
	rm -rf build/ dist/ *.egg-info/
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
