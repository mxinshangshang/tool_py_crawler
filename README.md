# CAD文件爬虫

一个**通用、资源友好**的CAD文件爬虫，支持通过YAML配置文件自定义搜索目标。

## 特性

- 📁 **配置驱动** - 通过YAML文件配置，无需改代码
- 🔍 **多源搜索** - GitHub、Thingiverse、Printables、Google等
- ✅ **文件验证** - 智能验证DXF/STL/STEP/SVG文件有效性
- 🗂️ **智能去重** - 基于SHA-256的文件去重
- ⏸️ **断点续传** - 随时中断，随时继续
- 🎯 **资源友好** - 自适应请求延迟，避免对目标站点造成压力
- 📊 **进度显示** - 实时进度和最终统计

## 快速开始

```bash
cd cad-crawler

# 安装依赖
pip install -r requirements.txt

# 查看可用配置
python main.py --list

# 运行树莓派5配置
python main.py --config raspberry-pi5

# 查看状态
python main.py --config raspberry-pi5 --status
```

## 可用配置

- `raspberry-pi5` - 树莓派5外壳
- `arduino` - Arduino外壳
- `laser-cutting` - 激光切割模板
- `example` - 示例配置模板

## 命令行用法

```bash
# 列出所有配置
python main.py --list

# 使用指定配置运行
python main.py --config raspberry-pi5

# 使用自定义配置文件
python main.py --config ./my-config.yaml

# 查看状态
python main.py --config raspberry-pi5 --status

# 从头开始（不恢复）
python main.py --config raspberry-pi5 --no-resume

# 创建新配置
python main.py --create-config my-project
```

## 创建自己的配置

复制 `configs/example.yaml` 并修改：

```yaml
name: "我的项目"

base_keywords:
  - "my project"
  - "我的项目"

product_types:
  - "case"
  - "外壳"

file_types:
  - "dxf"
  - "stl"

target_extensions:
  - ".dxf"
  - ".stl"
  - ".step"
  - ".svg"

sources:
  - "github"
  - "thingiverse"

# 礼貌爬取设置
request_delay: 4.0  # 请求间隔4秒
verify_files: true  # 验证文件
deduplicate: true   # 去重
```

## 目录结构

```
cad-crawler/
├── main.py                   # 主入口
├── requirements.txt          # 依赖
├── configs/                  # 配置文件
│   ├── raspberry-pi5.yaml
│   ├── arduino.yaml
│   └── ...
├── cadcrawler/               # 核心模块
│   ├── core.py              # 爬虫引擎
│   ├── config.py            # 配置管理
│   ├── downloader.py        # 下载器
│   ├── storage.py           # 存储管理
│   ├── validators.py        # 文件验证
│   ├── progress.py          # 进度显示
│   ├── utils.py             # 工具函数
│   └── parsers/             # 站点解析器
└── data/                    # 数据目录
    └── [config-name]/
        ├── downloads/       # 下载的文件
        ├── state.json       # 状态文件
        └── hashes.txt       # 哈希值（去重用）
```

## 资源友好设计

- **自适应延迟** - 基础4秒，失败时指数退避（最长30秒）
- **单线程** - 避免并发请求造成压力
- **User-Agent标识** - 清晰标识爬虫身份
- **断点续传** - 随时可中断，进度保存

## License

MIT
