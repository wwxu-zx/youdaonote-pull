# 更新说明

## 新增功能

### 1. 行内代码支持 ✅
有道云笔记中的行内代码现在可以正确转换为Markdown格式。

### 2. 颜色支持 ✅
- 保留文字颜色和背景色
- 使用HTML标签（兼容主流平台）

### 3. 平台发布工具 ✅
新增 `convert_for_platform.py` 脚本：
- 图片转换为GitHub CDN地址
- 颜色归一化（统一为红/蓝/绿）
- 适合掘金、知乎等平台

### 4. 文件名规范化 ✅
- 自动规范化笔记和资源文件夹名称
- 只保留中英文、数字、下划线
- 空格和特殊字符统一替换为下划线

### 5. 图片MD5命名 ✅
- 图片使用内容MD5作为文件名
- 自动去重相同内容的图片
- 新增 `rename_images_by_md5.py` 工具

### 6. 资源目录优化 ✅
- 原始图片保存到 `assets_ori/`
- 方便与MD5命名的 `assets/` 区分

## 使用方法

### 同步笔记
```bash
python pull.py
```

### 转换为平台版本
```bash
python convert_for_platform.py --blog-dir ./ydnote
# 或使用快捷脚本
./quick_convert.sh
```

### 图片MD5重命名
```bash
python rename_images_by_md5.py ./ydnote/assets_ori ./ydnote/assets
```

## 技术细节

- 向后兼容：不影响现有功能
- 配置安全：敏感文件已忽略
