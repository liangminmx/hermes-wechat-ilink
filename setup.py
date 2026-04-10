#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hermes-wechat-ilink-plugin",
    version="2.0.1",
    author="假装不单纯",
    author_email="",
    description="WeChat iLink plugin for Hermes Agent - Pure Python implementation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/liangminmx/hermes-wechat-ilink",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "qrcode[pil]>=7.4.2",
        "aiohttp>=3.9.0",
    ],
    entry_points={
        "console_scripts": [
            "hermes-wechat=hermes_wechat_ilink.__main__:main",
        ],
    },
)