# Danbooru2024 角色数据采集器使用说明

## 简介

本模块提供了两种方式来采集Danbooru2024数据集中的角色图片：

1. **DanbooruClient** - 用于本地已下载的Danbooru2024数据集
2. **DanbooruApiSpider** - 用于通过Danbooru官方API在线采集

## 模块结构

```
src/danbooru/
├── __init__.py          # 模块导出
├── danbooru_client.py   # 本地数据集采集器
├── danbooru_api_spider.py # API采集器
└── USAGE.md             # 本说明文档
```

## 一、DanbooruApiSpider（推荐）

通过Danbooru官方API在线采集角色图片。

### 准备工作

1. **注册Danbooru账号**
2. **获取API密钥**: 登录Danbooru → 设置 → API Access → API Key

### 命令行使用

```bash
# 采集所有角色（需要API认证）
python -m src.danbooru.danbooru_api_spider \
    --username your_username \
    --api-key your_api_key \
    --character-file /path/to/loli-role.txt \
    --output-dir /path/to/output \
    --max-count 50

# 采集指定角色
python -m src.danbooru.danbooru_api_spider \
    --username your_username \
    --api-key your_api_key \
    --characters Arona Nahida \
    --output-dir /path/to/output

# 断点续传（从第10个角色开始）
python -m src.danbooru.danbooru_api_spider \
    --username your_username \
    --api-key your_api_key \
    --start-from 10 \
    --output-dir /path/to/output
```

### Python API 使用

```python
from src.danbooru import DanbooruApiSpider, load_character_list

# 创建采集器
spider = DanbooruApiSpider(username='your_username', api_key='your_api_key')

# 加载角色列表
characters = load_character_list('/path/to/loli-role.txt')
print(f"加载了 {len(characters)} 个角色")

# 下载单个角色
success, fail = spider.download_character_images(
    'arona_(blue_archive)',  # Danbooru标签名
    '/path/to/output',
    max_count=50
)

# 批量下载多个角色
results = spider.download_multiple_characters(
    characters,
    '/path/to/output',
    max_count_per_character=50
)
```

## 二、DanbooruClient（本地数据集）

用于访问本地已下载的Danbooru2024数据集。

### 数据集结构要求

```
danbooru2024/
├── metadata.json    # 图片元数据
└── images/          # 图片目录（可选）
    └── <md5>.jpg
```

### 使用示例

```python
from src.danbooru import DanbooruClient

# 创建客户端
client = DanbooruClient('/path/to/danbooru2024')

# 加载metadata
client.load_metadata()

# 搜索角色
records = client.search_by_character('arona')
print(f"找到 {len(records)} 张图片")

# 下载角色图片
success, fail = client.download_character_images(
    'arona',
    '/path/to/output',
    max_count=50
)
```

## 角色列表文件格式

角色列表文件格式如下（每行一个角色）：

```
阿洛娜 蔚蓝档案 Arona アロナ
普拉娜 蔚蓝档案 Plana プラナ
砂狼白子 蔚蓝档案 Shiroko シロコ
纳西妲 原神 Nahida ナヒダ
```

字段说明：
1. 中文名
2. 作品名
3. 英文名（Danbooru标签名）
4. 日文名

采集时使用**英文名**作为Danbooru搜索标签。

## API限制说明

Danbooru API有以下限制：

| 限制类型 | 未认证 | 已认证 |
|---------|-------|-------|
| 每分钟请求数 | 2 | 20 |
| 每小时请求数 | 40 | 300 |
| 每日请求数 | 1000 | 10000 |

建议：
- 使用认证方式以获得更高的请求限制
- 代码已内置随机延迟，避免触发限流
- 大批量采集时建议分多次进行

## 输出目录结构

```
output_dir/
├── 阿洛娜/
│   ├── <md5_1>.jpg
│   ├── <md5_2>.jpg
│   └── ...
├── 普拉娜/
│   ├── <md5_1>.jpg
│   └── ...
└── ...
```

## 注意事项

1. **API认证**: Danbooru官方API需要认证才能访问，未认证请求会返回403错误
2. **标签格式**: Danbooru标签使用下划线分隔，如 `arona_(blue_archive)`
3. **内容过滤**: 默认排除`explicit`和`questionable`评级的内容
4. **网络延迟**: 由于访问国外服务器，建议使用代理或VPN
5. **数据安全**: 请遵守Danbooru的使用条款和版权规定

## 完整命令行参数

```bash
python -m src.danbooru.danbooru_api_spider --help

usage: danbooru_api_spider.py [-h] [--character-file CHARACTER_FILE] 
                              [--output-dir OUTPUT_DIR] [--max-count MAX_COUNT]
                              [--start-from START_FROM] [--username USERNAME]
                              [--api-key API_KEY]

Danbooru API角色图片采集器

optional arguments:
  -h, --help            显示帮助信息
  --character-file      角色列表文件路径
  --output-dir          图片保存目录
  --max-count           每个角色最大下载数量（默认50）
  --start-from          从第几个角色开始（断点续传）
  --username            Danbooru用户名
  --api-key             Danbooru API密钥
```
