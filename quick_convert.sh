#!/bin/bash
# 快速转换博客文章为平台发布版本

cd "$(dirname "$0")"
python3 convert_for_platform.py --blog-dir /Users/wwxu/Documents/ydnote "$@"
