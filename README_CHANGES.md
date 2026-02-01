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

## 使用方法

### 同步笔记
```bash
python pull.py
```

### 转换为平台版本
```bash
python convert_for_platform.py --blog-dir /path/to/blog
# 或使用快捷脚本
./quick_convert.sh
```

## 技术细节

- 向后兼容：不影响现有功能
- 配置安全：敏感文件已忽略
