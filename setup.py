from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="hermes-wechat-ilink",
    version="0.1.0",
    author="liangminmx",
    author_email="liangminmx@users.noreply.github.com",
    description="WeChat iLink plugin for Hermes Agent - Direct WeChat integration via Tencent's official iLink API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liangminmx/hermes-wechat-ilink",
    packages=["hermes_wechat_ilink"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "hermes.plugins": [
            "wechat-ilink = hermes_wechat_ilink:create_memory_provider",
        ],
    },
)