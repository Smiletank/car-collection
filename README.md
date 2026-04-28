# 🚗 小车收藏管理

一个基于Streamlit + 智谱AI的小车收藏管理工具。

## 功能

- 📸 **智能入库**：拍照上传，AI自动识别品牌、车型、颜色
- 🔍 **查重检测**：购买前检查是否已有相同或相似车型
- 📚 **收藏浏览**：查看所有收藏，支持搜索和筛选
- ✏️ **可编辑识别结果**：AI识别后可手动修改再入库

## 快速开始

### 1. 安装依赖

```bash
cd car_collection
pip install -r requirements.txt
```

### 2. 运行应用

```bash
streamlit run app.py
```

### 3. 配置API Key

运行后在侧边栏输入你的智谱API Key（在 [open.bigmodel.cn](https://open.bigmodel.cn) 注册获取）

### 4. 开始使用

- **入库**：上传照片 → 点击识别 → 编辑结果 → 确认入库
- **查重**：上传照片 → 点击查重 → 查看是否有相似车型

## 目录结构

```
car_collection/
├── app.py              # 主程序
├── database.py         # 数据库操作
├── ai_recognition.py   # AI识别
├── requirements.txt    # 依赖
├── data/
│   ├── cars.db         # 数据库（自动创建）
│   └── images/         # 图片存储
```

## 注意事项

- 智谱AI有免费额度，足够日常使用
- 数据存储在本地SQLite数据库中
- 图片保存在 data/images/ 目录
