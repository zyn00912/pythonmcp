# MCP 服务器

## 概述

该项目是一个基于 Python 的服务器，实现了模型上下文协议 (MCP)，其核心功能是管理和操作 `D:/WWWROOT/GSW/file` 文件夹。该服务器使用 FastAPI 和 `pygls` 构建，通过 HTTP 与任何支持 MCP 的客户端（如 TRAE）通信。

## 项目结构

```
. d:\mcp_server\mcp_python/
├── .gitignore
├── .venv/
├── DOCUMENTATION.md
├── README.md
├── __pycache__/
├── main.py
├── pyproject.toml
├── requirements.txt
└── templates/
    ├── files.html
    ├── index.html
    ├── monitor.html
    └── nav.html
```

- **`main.py`**: 项目的核心，包含 FastAPI 应用和 LSP 服务器的实现。它定义了所有可用的工具，并将文件操作的基础路径设置为 `D:/WWWROOT/GSW/file`。
- **`templates/`**: 包含所有 HTML 模板的目录。
  - **`index.html`**: 项目主页，提供项目介绍和站点地图。
  - **`files.html`**: 文件浏览器页面。
  - **`monitor.html`**: 服务器状态监控页面。
  - **`nav.html`**: 统一的导航栏。
- **`pyproject.toml`**: 使用 UV 进行现代化的包管理配置文件。

## 核心功能

### FastAPI 应用 (`main.py`)

- **项目主页**: 在根路径 (`/`) 提供项目介绍和站点地图。
- **文件浏览器**: 在 `/files` 路径提供一个 Web 界面，用于浏览和管理 `D:/WWWROOT/GSW/file` 文件夹中的文件。
- **状态监控**: 在 `/monitor` 路径提供一个 Web 界面，用于实时监控服务器状态。
- **MCP 端点**: 在 `/mcp` 提供一个端点，用于与兼容 MCP 的客户端进行通信。此端点现在支持流式响应（`text/event-stream`），允许服务器逐步发送数据，而不是等待整个响应完成后一次性发送。支持的工具包括：
    - `list-files`: 列出 `D:/WWWROOT/GSW/file` 目录下的文件和目录。
    - `read-file`: 读取 `D:/WWWROOT/GSW/file` 目录下的文件内容。
    - `write-file`: 将内容写入 `D:/WWWROOT/GSW/file` 目录下的文件。
    - `delete-path`: 删除 `D:/WWWROOT/GSW/file` 目录下的文件或空目录。
    - `run-command`: 执行 shell 命令。
    - `reboot-server`: 重启服务器。

## 如何运行

1. **创建并激活虚拟环境**:
   ```bash
   uv venv
   .venv\Scripts\activate
   ```

2. **安装依赖**:
   ```bash
   uv pip sync pyproject.toml
   ```

3. **启动服务器**:
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8888
   ```

## Web 界面

- **项目主页**: `http://127.0.0.1:8888/`
- **文件浏览器**: `http://127.0.0.1:8888/files`
- **监控页面**: `http://127.0.0.1:8888/monitor`