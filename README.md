# MCP 服务器

## 概述

该项目是一个基于 Python 的服务器，实现了模型上下文协议 (MCP)，其核心功能是管理和操作 `d:/gswfile` 文件夹。该服务器使用 FastAPI 和 `pygls` 构建，通过 HTTP 与任何支持 MCP 的客户端（如 TRAE）通信。

## 项目结构

```
. d:\mcp_server\fastapi_mcp/
├── .gitignore                      # Git 忽略规则
├── README.md                       # 项目说明文档
├── main.py                         # FastAPI 应用与路由
├── mcp_server.py                   # FastMCP MCP 服务器（工具暴露）
├── pyproject.toml                  # 现代化依赖与构建配置
├── requirements.txt                # pip 依赖清单
└── templates/                      # 前端模板
    ├── index.html                  # 主页/站点地图
    ├── files.html                  # 文件浏览器页面
    ├── monitor.html                # 服务器状态监控页面
    └── nav.html                    # 通用导航栏
```

- `main.py`: 项目的核心，包含 FastAPI 应用和 LSP 服务器的实现。它定义了所有可用的工具，并将文件操作的基础路径设置为 `d:/gswfile`。
- `templates/`: 包含所有 HTML 模板的目录。
  - `index.html`: 项目主页，提供项目介绍和站点地图。
  - `files.html`: 文件浏览器页面。
  - `monitor.html`: 服务器状态监控页面。
  - `nav.html`: 统一的导航栏。
- `pyproject.toml`: 使用 UV 进行现代化的包管理配置文件。

## 核心功能

### FastAPI 路由 (`main.py`)

- 项目主页: 在根路径 (`/`) 提供项目介绍和站点地图。
- 文件浏览器: 在 `/files` 路径提供一个 Web 界面，用于浏览和管理 `d:/gswfile` 文件夹中的文件。
- 状态监控: 在 `/monitor` 路径提供一个 Web 界面，用于实时监控服务器状态。
- 文件接口: 提供 `/api/files` 系列接口以进行文件读取、写入与删除。

### MCP 服务 (`mcp_server.py`)

- 使用 `fastmcp` 构建独立的 MCP 服务器，暴露与文件管理相关的工具：
  - `list_files`
  - `read_file`
  - `write_file`
  - `delete_path`
  - `run_command`
- 该 MCP 服务独立运行，适合与支持 MCP 的客户端（如 Claude、Cursor、TRAE）集成。

## 如何运行

1. 创建并激活虚拟环境:
   ```bash
   uv venv
   .venv\Scripts\activate
   ```

2. 安装依赖:
   ```bash
   uv pip sync pyproject.toml
   ```

3. 启动 FastAPI 服务器:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8888
   ```

4. 启动 MCP 服务（fastmcp）:
   - 方式一（推荐，需安装 fastmcp CLI）:
     ```bash
     fastmcp run mcp_server.py
     ```
   - 方式二（直接运行 Python 脚本）:
     ```bash
     python mcp_server.py
     ```

## Web 界面

- 项目主页: `http://127.0.0.1:8888/`
- 文件浏览器: `http://127.0.0.1:8888/files`
- 监控页面: `http://127.0.0.1:8888/monitor`

## 文件浏览器功能概览

- 路径位置与已打开文件分区：右侧内容区分为“位置”和“打开的文件”。
- 面包屑导航：支持点击各级目录快速跳转。
- 统一记录分页：子文件夹与文件合并为统一列表，按名称排序，分页每页 15 条。
- 网格平铺：列表以 5 列网格平铺显示，目录与文件统一卡片样式（图标 + 名称）。
- 多文件同时打开：右侧“打开的文件”区域支持多个文件卡片并存；卡片头部显示完整相对路径；支持关闭。
- 媒体与文本：音频（如 `.mp3`）通过原始流播放，文本文件在卡片内直接显示内容。

## 文件图标使用规范

- 目录：`📁`（专用，不与任何文件类型图标重复）
- 音频：`🎵`（mp3、wav、m4a、flac、ogg）
- 图片：`🖼️`（png、jpg、jpeg、gif、bmp、webp、svg）
- PDF：`📕`
- 文本：`📝`（txt、log、ini、cfg、conf）
- Markdown：`📒`（md、markdown）
- CSV：`📊`
- Word：`📘`（doc、docx）
- Excel：`📈`（xls、xlsx）
- 压缩包：`🗜️`（zip、rar、7z、tar、gz、tgz）
- 结构化数据：`🗂️`（json、yaml、yml、xml）
- 可执行/二进制：`⚙️`（exe、dll、bin、msi）
- 其他：`📃`

> 图标仅用于前端展示，映射逻辑位于 `templates/files.html` 的 `getIcon(record)` 中，目录使用 `kind === 'dir'` 专属图标，文件类型根据扩展名匹配。

## 接口与路径规范

- 列表接口：`GET /api/files` 返回目录与文件的相对路径（相对于 `BASE_PATH`）。
- 文本读取：`GET /api/files/{path}` 返回 `{ content }`，用于在前端卡片中显示文本内容。
- 原始流：`GET /api/files/raw/{path}` 用于音频等二进制内容的流式播放。
- 路径统一：前端将 `\` 规范化为 `/` 并统一使用相对路径进行路由与展示。

## MCP 客户端配置（示例）

- 本地通过 FastMCP CLI 运行后，可在支持 MCP 的客户端中添加如下配置（以 mcp-proxy 为例）：
  ```json
  {
    "mcpServers": {
      "file_mcp_server": {
        "command": "mcp-proxy",
        "args": ["http://127.0.0.1:8000/mcp"],
        "description": "通过代理连接到 FastMCP 服务（如需）"
      }
    }
  }
  ```
- 或直接使用 `fastmcp run mcp_server.py` 的本地进程连接方式，具体以客户端支持为准。

## 自动启动 MCP 服务

- 当启动 FastAPI（`uvicorn main:app --host 127.0.0.1 --port 8888`）时，主进程会在启动钩子中检测 `127.0.0.1:8000` 端口是否空闲：
  - 若空闲：自动启动 `mcp_server.py`（FastMCP 服务），作为子进程常驻。
  - 若已占用：认为 MCP 已运行，跳过自动启动，避免重复。
- 关闭 FastAPI 时会尝试终止该子进程（若是本进程启动的）。
- 注意：如果你希望固定使用其他端口或独立运行，可手动启动 FastMCP 并更新下方 TRAE 配置中的地址。

## 在 TRAE 中配置 MCP（JSON）

- 方式一：通过 `mcp-proxy` 连接到本地 HTTP MCP 端点（推荐，前端界面与 HTTP 服务解耦）
  ```json
  {
    "mcpServers": {
      "file_mcp_server": {
        "command": "mcp-proxy",
        "args": ["http://127.0.0.1:8000/mcp"],
        "description": "连接到本地 FastMCP 服务"
      }
    }
  }
  ```
- 方式二：直接以本地进程方式运行（TRAE 拉起 Python 脚本；适用于不暴露 HTTP 的场景）
  ```json
  {
    "mcpServers": {
      "file_mcp_server": {
        "command": "python",
        "args": ["D:/mcp_server/fastapi_mcp/mcp_server.py"],
        "env": {},
        "description": "直接运行本地 FastMCP 服务器脚本"
      }
    }
  }
  ```
- 将以上 JSON 放入 TRAE 的 MCP 配置区域或全局设置文件（具体路径以 TRAE 版本为准）。若你的 MCP 服务地址或端口不同，请同步调整 `args` 中的 URL 或脚本路径。