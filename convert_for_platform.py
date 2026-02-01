#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将博客文章转换为适合掘金、知乎等平台发布的版本
- 将相对路径的图片转换为 GitHub CDN 地址
- 生成可直接复制粘贴的版本
"""

import os
import re
import argparse
from pathlib import Path

# 默认配置
DEFAULT_BLOG_DIR = "/Users/wwxu/Documents/ydnote"
GITHUB_USERNAME = "wwxu-zx"  # 修改为你的 GitHub 用户名
GITHUB_REPO = "blog"      # 修改为你的仓库名
GITHUB_BRANCH = "main"    # 或 "master"


class PlatformConverter:
    """平台转换器"""
    
    # 颜色归一化映射表
    COLOR_NORMALIZATION = {
        # 红色系 -> 统一红色
        'red': '#e74c3c',
        'rgb(255, 0, 0)': '#e74c3c',
        'rgb(255,0,0)': '#e74c3c',
        '#ff0000': '#e74c3c',
        '#FF0000': '#e74c3c',
        '#e74c3c': '#e74c3c',
        
        # 蓝色系 -> 统一蓝色
        'blue': '#3498db',
        'rgb(0, 0, 255)': '#3498db',
        'rgb(0,0,255)': '#3498db',
        '#0000ff': '#3498db',
        '#0000FF': '#3498db',
        '#3498db': '#3498db',
        
        # 绿色系 -> 统一绿色
        'green': '#27ae60',
        'rgb(0, 255, 0)': '#27ae60',
        'rgb(0,255,0)': '#27ae60',
        '#00ff00': '#27ae60',
        '#00FF00': '#27ae60',
        '#27ae60': '#27ae60',
    }
    
    def __init__(self, blog_dir, github_username, github_repo, github_branch):
        self.blog_dir = blog_dir
        self.posts_dir = os.path.join(blog_dir, "posts")
        self.assets_dir = os.path.join(blog_dir, "assets")
        self.output_dir = os.path.join(blog_dir, "platform_ready")
        self.github_username = github_username
        self.github_repo = github_repo
        self.github_branch = github_branch
    
    def normalize_colors(self, content):
        """归一化颜色值
        
        将各种颜色格式统一为预定义的颜色方案：
        - 红色系 -> #e74c3c
        - 蓝色系 -> #3498db
        - 绿色系 -> #27ae60
        """
        def replace_color(match):
            style = match.group(1)
            text = match.group(2)
            
            # 提取颜色值（支持带引号和不带引号的情况）
            color_match = re.search(r'color:\s*([^;"\'>]+)', style)
            bg_color_match = re.search(r'background-color:\s*([^;"\'>]+)', style)
            
            new_style_parts = []
            
            # 处理文字颜色
            if color_match:
                original_color = color_match.group(1).strip()
                normalized_color = self._normalize_single_color(original_color)
                if normalized_color:
                    new_style_parts.append(f'color: {normalized_color}')
                else:
                    # 保留原始颜色
                    new_style_parts.append(f'color: {original_color}')
            
            # 处理背景色
            if bg_color_match:
                original_bg = bg_color_match.group(1).strip()
                normalized_bg = self._normalize_single_color(original_bg)
                if normalized_bg:
                    new_style_parts.append(f'background-color: {normalized_bg}')
                else:
                    # 保留原始背景色
                    new_style_parts.append(f'background-color: {original_bg}')
            
            if new_style_parts:
                new_style = '; '.join(new_style_parts)
                return f'<span style="{new_style}">{text}</span>'
            
            return match.group(0)
        
        # 匹配 <span style="...">...</span>
        # 使用非贪婪匹配和更宽松的内容模式来处理嵌套的Markdown语法
        content = re.sub(
            r'<span\s+style="([^"]+)">(.+?)</span>',
            replace_color,
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _normalize_single_color(self, color):
        """归一化单个颜色值
        
        Args:
            color: 颜色值，支持多种格式（rgb(), #hex, 颜色名）
            
        Returns:
            归一化后的颜色值（HEX格式），如果无法识别则返回None
        """
        if not color:
            return None
            
        color = color.strip().lower()
        
        # 1. 直接查找映射表（最快）
        if color in self.COLOR_NORMALIZATION:
            return self.COLOR_NORMALIZATION[color]
        
        # 2. 尝试解析RGB值
        rgb_match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color)
        if rgb_match:
            r, g, b = int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3))
            return self._classify_color_by_rgb(r, g, b)
        
        # 3. 尝试解析HEX值
        hex_match = re.match(r'#?([0-9a-f]{6})', color)
        if hex_match:
            hex_color = hex_match.group(1)
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return self._classify_color_by_rgb(r, g, b)
        
        # 4. 尝试解析简写HEX值 (#abc -> #aabbcc)
        short_hex_match = re.match(r'#?([0-9a-f]{3})$', color)
        if short_hex_match:
            hex_color = short_hex_match.group(1)
            r = int(hex_color[0] * 2, 16)
            g = int(hex_color[1] * 2, 16)
            b = int(hex_color[2] * 2, 16)
            return self._classify_color_by_rgb(r, g, b)
        
        return None
    
    def _classify_color_by_rgb(self, r, g, b):
        """根据RGB值分类颜色
        
        Args:
            r, g, b: RGB颜色值 (0-255)
            
        Returns:
            归一化后的颜色HEX值，如果无法分类则返回None
        """
        # 红色系：红色分量显著高于其他分量
        if r > 200 and g < 100 and b < 100:
            return '#e74c3c'
        if r > 150 and (r - g) > 80 and (r - b) > 80:
            return '#e74c3c'
        
        # 蓝色系：蓝色分量显著高于其他分量
        if r < 100 and g < 150 and b > 200:
            return '#3498db'
        if b > 150 and (b - r) > 80 and (b - g) > 50:
            return '#3498db'
        
        # 绿色系：绿色分量显著高于其他分量
        if r < 100 and g > 200 and b < 100:
            return '#27ae60'
        if g > 150 and (g - r) > 80 and (g - b) > 80:
            return '#27ae60'
        
        return None
    
    def convert_image_path(self, match, note_name):
        """将相对路径的图片链接转换为 GitHub raw URL"""
        img_alt = match.group(1)
        img_path = match.group(2)
        
        # 如果已经是 http/https 链接，不处理
        if img_path.startswith(('http://', 'https://')):
            return match.group(0)
        
        # 处理相对路径: assets/note_name/image.png
        if img_path.startswith('assets/'):
            # 去掉 assets/ 前缀
            relative_path = img_path[7:]  # 移除 "assets/"
            github_url = (
                f"https://raw.githubusercontent.com/"
                f"{self.github_username}/{self.github_repo}/"
                f"{self.github_branch}/assets/{relative_path}"
            )
            return f"![{img_alt}]({github_url})"
        
        # 如果是其他相对路径格式，尝试智能处理
        if not img_path.startswith('/'):
            github_url = (
                f"https://raw.githubusercontent.com/"
                f"{self.github_username}/{self.github_repo}/"
                f"{self.github_branch}/assets/{note_name}/{img_path}"
            )
            return f"![{img_alt}]({github_url})"
        
        return match.group(0)
    
    def convert_image_path_angle_brackets(self, match, note_name):
        """将相对路径的图片链接（<>格式）转换为 GitHub raw URL"""
        img_alt = match.group(1)
        img_path = match.group(2)
        
        # 如果已经是 http/https 链接，不处理
        if img_path.startswith(('http://', 'https://')):
            return match.group(0)
        
        # 处理 ../assets/ 开头的路径
        if img_path.startswith('../assets/'):
            # 去掉 ../ 前缀
            relative_path = img_path[3:]  # 移除 "../"
            # URL编码特殊字符
            from urllib.parse import quote
            encoded_path = quote(relative_path, safe='/.')
            github_url = (
                f"https://raw.githubusercontent.com/"
                f"{self.github_username}/{self.github_repo}/"
                f"{self.github_branch}/{encoded_path}"
            )
            return f"![{img_alt}]({github_url})"
        
        # 处理 assets/ 开头的路径
        if img_path.startswith('assets/'):
            from urllib.parse import quote
            encoded_path = quote(img_path, safe='/.')
            github_url = (
                f"https://raw.githubusercontent.com/"
                f"{self.github_username}/{self.github_repo}/"
                f"{self.github_branch}/{encoded_path}"
            )
            return f"![{img_alt}]({github_url})"
        
        return match.group(0)
    
    def process_markdown_file(self, file_path, output_path):
        """处理单个 markdown 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取笔记名称（不含扩展名）
        note_name = Path(file_path).stem
        
        # 添加文章信息头部（可选）
        header = f"<!-- 原文件: {note_name}.md -->\n<!-- 图片托管于 GitHub -->\n\n"
        
        # 处理图片链接 - 匹配 ![alt](path) 和 ![](<path>) 格式
        # 先处理 <> 包裹的路径
        content = re.sub(
            r'!\[(.*?)\]\(<(.*?)>\)',
            lambda m: self.convert_image_path_angle_brackets(m, note_name),
            content
        )
        # 再处理普通路径
        content = re.sub(
            r'!\[(.*?)\]\((?!<)(.*?)\)',
            lambda m: self.convert_image_path(m, note_name),
            content
        )
        
        # 处理可能的 HTML img 标签（如果有）
        content = re.sub(
            r'<img\s+[^>]*src=["\']([^"\']+)["\'][^>]*>',
            lambda m: self._convert_html_img(m, note_name),
            content
        )
        
        # 归一化颜色
        content = self.normalize_colors(content)
        
        # 写入输出文件
        final_content = header + content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        return True
    
    def _convert_html_img(self, match, note_name):
        """转换 HTML img 标签"""
        img_tag = match.group(0)
        src_match = re.search(r'src=["\']([^"\']+)["\']', img_tag)
        if src_match:
            src = src_match.group(1)
            if not src.startswith(('http://', 'https://')):
                if src.startswith('assets/'):
                    relative_path = src[7:]
                    github_url = (
                        f"https://raw.githubusercontent.com/"
                        f"{self.github_username}/{self.github_repo}/"
                        f"{self.github_branch}/assets/{relative_path}"
                    )
                    return img_tag.replace(src, github_url)
        return img_tag
    
    def run(self):
        """执行转换"""
        # 检查目录
        if not os.path.exists(self.posts_dir):
            print(f"❌ 错误: posts 目录不存在: {self.posts_dir}")
            return False
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 遍历处理所有 md 文件
        md_files = [f for f in os.listdir(self.posts_dir) if f.endswith('.md')]
        
        if not md_files:
            print(f"⚠️  警告: 在 {self.posts_dir} 中没有找到 .md 文件")
            return False
        
        processed_count = 0
        failed_files = []
        
        print(f"📝 开始处理 {len(md_files)} 个文件...\n")
        
        for filename in md_files:
            input_path = os.path.join(self.posts_dir, filename)
            output_path = os.path.join(self.output_dir, filename)
            
            try:
                self.process_markdown_file(input_path, output_path)
                print(f"✅ {filename}")
                processed_count += 1
            except Exception as e:
                print(f"❌ {filename} - 错误: {e}")
                failed_files.append(filename)
        
        # 输出结果
        print(f"\n{'='*60}")
        print(f"✨ 处理完成!")
        print(f"   成功: {processed_count} 个文件")
        if failed_files:
            print(f"   失败: {len(failed_files)} 个文件")
            for f in failed_files:
                print(f"      - {f}")
        print(f"\n📂 输出目录: {self.output_dir}")
        print(f"{'='*60}\n")
        
        # 使用提示
        print("📌 使用提示:")
        print(f"   1. 确保已将代码 push 到 GitHub 仓库")
        print(f"      git add . && git commit -m 'update' && git push")
        print(f"   2. 确保仓库是 public（或配置了访问权限）")
        print(f"   3. 等待几分钟让 GitHub CDN 生效")
        print(f"   4. 在 {self.output_dir} 中复制文章内容")
        print(f"   5. 粘贴到掘金、知乎等平台发布\n")
        
        # 显示图片 URL 示例
        if md_files:
            sample_file = Path(md_files[0]).stem
            sample_url = (
                f"https://raw.githubusercontent.com/"
                f"{self.github_username}/{self.github_repo}/"
                f"{self.github_branch}/assets/{sample_file}/example.png"
            )
            print(f"🖼️  图片 URL 示例:\n   {sample_url}\n")
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将博客文章转换为适合掘金、知乎等平台发布的版本'
    )
    parser.add_argument(
        '--blog-dir',
        default=DEFAULT_BLOG_DIR,
        help=f'博客目录路径 (默认: {DEFAULT_BLOG_DIR})'
    )
    parser.add_argument(
        '--github-user',
        default=GITHUB_USERNAME,
        help=f'GitHub 用户名 (默认: {GITHUB_USERNAME})'
    )
    parser.add_argument(
        '--github-repo',
        default=GITHUB_REPO,
        help=f'GitHub 仓库名 (默认: {GITHUB_REPO})'
    )
    parser.add_argument(
        '--github-branch',
        default=GITHUB_BRANCH,
        help=f'GitHub 分支名 (默认: {GITHUB_BRANCH})'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📱 博客文章平台转换工具")
    print("="*60 + "\n")
    
    converter = PlatformConverter(
        blog_dir=args.blog_dir,
        github_username=args.github_user,
        github_repo=args.github_repo,
        github_branch=args.github_branch
    )
    
    success = converter.run()
    
    if not success:
        exit(1)


if __name__ == "__main__":
    main()
