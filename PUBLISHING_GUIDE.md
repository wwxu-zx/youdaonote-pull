# 📚 有道云笔记发布指南

完整的从有道云笔记同步到 GitHub 并发布到掘金、知乎等平台的详细流程。

---

## 🎯 目标

- ✅ 同步有道云笔记到本地 Markdown
- ✅ 推送到 GitHub 仓库作为备份
- ✅ 转换为适合平台发布的版本
- ✅ 发布到掘金、知乎等技术平台

---

## 📋 前置准备

### 1. 环境要求

- Python 3.6+
- Git
- GitHub 账号
- 有道云笔记账号

### 2. 配置文件

编辑 `config.json`：

```json
{
    "local_dir": "/Users/wwxu/Documents/ydnote",
    "ydnote_dir": "Blogs",
    "smms_secret_token": "",
    "is_relative_path": true
}
```

**参数说明：**
- `local_dir`: 本地博客目录（绝对路径）
- `ydnote_dir`: 有道云笔记中要同步的目录名
- `smms_secret_token`: 留空（使用本地图片）
- `is_relative_path`: 必须为 `true`（使用相对路径）

### 3. 登录有道云笔记

首次使用需要登录：

```bash
python pull.py
```

按提示使用浏览器登录有道云笔记，登录信息会保存到 `cookies.json`。

### 4. 创建 GitHub 仓库

1. 访问 https://github.com/new
2. 仓库名：`blog`
3. 可见性：**Public**（图片才能被外部访问）
4. 不勾选 "Add a README file"
5. 点击 "Create repository"

---

## 🚀 完整发布流程

### 步骤 1：同步有道云笔记

```bash
cd /Users/wwxu/Projects/youdaonote-pull
python pull.py
```

**执行效果：**

```
正在 pull，请稍后 ...
新增「posts/深度学习基础.md」
新增「posts/Python最佳实践.md」
已将图片「...」转换为「/Users/wwxu/Documents/ydnote/assets/深度学习基础/image1.png」
运行完成！耗时 15 秒
```

**生成的目录结构：**

```
/Users/wwxu/Documents/ydnote/
├── posts/                          # 所有 Markdown 笔记
│   ├── 深度学习基础.md
│   ├── Python最佳实践.md
│   └── ...
└── assets/                         # 图片和附件
    ├── 深度学习基础/
    │   ├── image1.png
    │   └── image2.png
    └── Python最佳实践/
        └── diagram.png
```

**关键特性：**
- ✅ 保留行内代码格式（\`code\`）
- ✅ 保留文字颜色和背景色
- ✅ 自动清理云端已删除的文件
- ✅ 图片和附件按笔记分组管理

---

### 步骤 2：推送到 GitHub

#### 首次推送

```bash
cd /Users/wwxu/Projects/blog

# 初始化 Git 仓库
git init

# 创建 .gitignore
cat > .gitignore << 'EOF'
.DS_Store
platform_ready/
*.bak
*~
EOF

# 添加所有文件
git add .

# 创建初始提交
git commit -m "init: import notes from youdao"

# 设置默认分支
git branch -M main

# 添加远程仓库（修改为你的用户名）
git remote add origin https://github.com/your_username/blog.git

# 推送到 GitHub
git push -u origin main
```

#### 后续更新

```bash
cd /Users/wwxu/Projects/blog

git add .
git commit -m "update: $(date +%Y-%m-%d)"
git push
```

**验证推送成功：**

访问 `https://github.com/your_username/blog` 确认文件已上传。

---

### 步骤 3：转换为平台发布版本

```bash
cd /Users/wwxu/Projects/youdaonote-pull

# 方式 A：使用快捷脚本（推荐）
./quick_convert.sh

# 方式 B：完整命令
python convert_for_platform.py \
  --blog-dir /Users/wwxu/Documents/ydnote \
  --github-user your_username \
  --github-repo blog \
  --github-branch main
```

**转换过程：**

```
📝 开始处理 10 个文件...

✅ 深度学习基础.md
✅ Python最佳实践.md
...

✨ 处理完成!
   成功: 10 个文件

📂 输出目录: /Users/wwxu/Documents/ydnote/platform_ready

📌 使用提示:
   1. 确保已将代码 push 到 GitHub 仓库
   2. 确保仓库是 public（或配置了访问权限）
   3. 等待几分钟让 GitHub CDN 生效
   4. 在 /Users/wwxu/Documents/ydnote/platform_ready 中复制文章内容
   5. 粘贴到掘金、知乎等平台发布
```

**转换效果对比：**

| 项目 | 本地版本 | 平台版本 |
|------|---------|---------|
| 图片路径 | `../assets/note/img.png` | `https://raw.githubusercontent.com/user/blog/main/assets/note/img.png` |
| 红色 | `#ff0000`, `rgb(255,0,0)` | 统一 `#e74c3c` |
| 蓝色 | `#0000ff`, `rgb(0,0,255)` | 统一 `#3498db` |
| 绿色 | `#00ff00`, `rgb(0,255,0)` | 统一 `#27ae60` |

---

### 步骤 4：发布到掘金

#### 4.1 访问掘金创作中心

https://juejin.cn/editor/drafts/new

#### 4.2 切换到 Markdown 编辑器

点击编辑器右上角的 **Markdown** 按钮。

#### 4.3 复制文章内容

```bash
# 在 Finder 中打开
open /Users/wwxu/Documents/ydnote/platform_ready

# 或使用命令行查看
cat /Users/wwxu/Documents/ydnote/platform_ready/深度学习基础.md
```

选择要发布的文章，**复制全部内容**。

#### 4.4 粘贴到掘金

在掘金 Markdown 编辑器中粘贴内容。

#### 4.5 预览效果

- 点击 **预览** 按钮查看效果
- 图片会自动从 GitHub CDN 加载
- 检查颜色、代码块、表格等格式

#### 4.6 完善信息

- **标题**：文章标题
- **封面**：选择封面图（可选）
- **摘要**：文章简介
- **标签**：添加相关标签（如：Python、深度学习）
- **分类**：选择技术分类

#### 4.7 发布

点击 **发布文章** 按钮。

---

### 步骤 5：发布到知乎

#### 5.1 访问知乎创作中心

https://www.zhihu.com/creator/featured-question/write

#### 5.2 导入 Markdown

1. 点击编辑器右上角的 **···** (更多)
2. 选择 **导入** → **Markdown**

#### 5.3 粘贴内容

打开 `/Users/wwxu/Documents/ydnote/platform_ready/{文章名}.md`，复制全部内容粘贴。

#### 5.4 调整格式

知乎对 Markdown 的支持有限，可能需要手动调整：

- **颜色**：知乎支持有限，可能显示为普通文本
- **代码块**：检查语法高亮
- **图片**：确认图片正常加载

#### 5.5 添加信息

- **话题**：添加相关话题（如：#Python# #深度学习#）
- **封面**：选择封面图

#### 5.6 发布

点击 **发布文章**。

---

## 🔄 日常更新工作流

### 完整流程

```bash
# 1. 同步有道云笔记
cd /Users/wwxu/Projects/youdaonote-pull
python pull.py

# 2. 将待发布的 blog 拷贝到 blog project 目录下，推送到 GitHub
cd /Users/wwxu/Projects/blog
git add .
git commit -m "update: $(date +%Y-%m-%d)"
git push

# 3. 等待 2-5 分钟（让 GitHub CDN 生效）
sleep 300

# 4. 转换平台版本
cd /Users/wwxu/Projects/youdaonote-pull
./quick_convert.sh

# 5. 发布到平台
open /Users/wwxu/Documents/ydnote/platform_ready
```

---

## 📌 重要提示

### ⚠️ GitHub CDN 生效时间

- **首次推送**：需要 3-5 分钟
- **更新图片**：需要 2-3 分钟
- **建议**：push 后等待几分钟再转换平台版本

### 🔐 隐私和安全

- `config.json` 包含本地路径，不应提交
- `cookies.json` 包含登录信息，不应提交
- 已在 `.gitignore` 中排除这些文件
- GitHub 仓库必须是 **public** 才能作为图床

### 📊 图片加载优化

**图片 URL 格式：**

```
https://raw.githubusercontent.com/your_username/blog/main/assets/{笔记名}/{图片名}
```

**加速方法：**

1. 使用 CDN 加速（可选）：
   ```
   https://cdn.jsdelivr.net/gh/your_username/blog@main/assets/{笔记名}/{图片名}
   ```

2. 修改 `convert_for_platform.py` 中的 `GITHUB_USERNAME` 等配置

### 🎨 颜色归一化说明

**为什么要归一化？**

- 有道云笔记可能使用多种颜色格式
- 平台对颜色的显示效果不同
- 统一方案让文章更专业、一致

**颜色映射：**

```python
红色系 → #e74c3c (适合强调、警告)
蓝色系 → #3498db (适合信息、链接)
绿色系 → #27ae60 (适合成功、正确)
```

### 📂 目录结构说明

```
blog/
├── posts/              # Markdown 文章（推送到 GitHub）
├── assets/             # 图片和附件（推送到 GitHub）
└── platform_ready/     # 平台版本（不推送，由 .gitignore 排除）
```

**为什么分开？**

- `posts/` 和 `assets/`: GitHub 仓库内容，图片使用相对路径
- `platform_ready/`: 平台发布版本，图片使用绝对 GitHub CDN 路径

---

## 🛠️ 故障排查

### 问题 1：图片无法加载

**症状：** 平台上图片显示不出来

**解决方法：**

1. 确认仓库是 **public**
2. 检查图片 URL 是否正确：
   ```bash
   # 手动访问图片链接测试
   curl -I https://raw.githubusercontent.com/your_username/blog/main/assets/test/image.png
   ```
3. 等待 2-5 分钟让 CDN 生效
4. 清除浏览器缓存重试

### 问题 2：颜色没有正确转换

**症状：** 平台版本颜色和本地不一致

**解决方法：**

1. 检查 `convert_for_platform.py` 是否正确执行
2. 查看 `platform_ready/` 目录下的文件
3. 确认 HTML span 标签格式：
   ```html
   <span style="color: #e74c3c">红色文字</span>
   ```

### 问题 3：Cookies 过期

**症状：** 运行 `python pull.py` 提示 "Cookies 可能已过期"

**解决方法：**

1. 删除 `cookies.json`
2. 重新运行 `python pull.py`
3. 按提示重新登录有道云笔记

### 问题 4：推送失败

**症状：** `git push` 失败

**解决方法：**

```bash
# 检查远程仓库
git remote -v

# 重新设置远程仓库
git remote remove origin
git remote add origin https://github.com/your_username/blog.git

# 强制推送（谨慎使用）
git push -u origin main -f
```

---

## 🎓 进阶技巧

### 1. 批量发布多篇文章

```bash
# 列出所有待发布文章
ls /Users/wwxu/Documents/ydnote/platform_ready

# 按修改时间排序
ls -lt /Users/wwxu/Documents/ydnote/platform_ready
```

### 2. 自定义颜色方案

编辑 `convert_for_platform.py` 的 `COLOR_NORMALIZATION` 字典：

```python
COLOR_NORMALIZATION = {
    'red': '#your_red_color',
    'blue': '#your_blue_color',
    'green': '#your_green_color',
}
```

### 3. 只转换特定文章

```bash
python convert_for_platform.py \
  --blog-dir /Users/wwxu/Documents/ydnote \
  --github-user your_username

# 手动筛选
cp /Users/wwxu/Documents/ydnote/platform_ready/特定文章.md ~/Desktop/
```

### 4. 定时自动同步

使用 macOS 的 `launchd` 或 `cron`：

```bash
# 编辑 crontab
crontab -e

# 每天晚上 10 点自动同步
0 22 * * * cd /Users/wwxu/Projects/youdaonote-pull && python pull.py && cd /Users/wwxu/Projects/blog && git add . && git commit -m "auto: $(date +\%Y-\%m-\%d)" && git push
```

---

## 📚 参考资源

- **有道云笔记 API**: 本项目基于 [DeppWang/youdaonote-pull](https://github.com/DeppWang/youdaonote-pull)
- **GitHub Raw CDN**: https://docs.github.com/en/repositories
- **掘金 Markdown 指南**: https://juejin.cn/markdown
- **知乎 Markdown 支持**: https://www.zhihu.com/question/20409634

---

## 🤝 贡献和反馈

遇到问题或有改进建议，欢迎提 Issue。

---

**最后更新：** 2026-02-01
