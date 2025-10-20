# 导入必要的库
import uvicorn
import os
import sys
import asyncio
import json
import time
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse
from pygls.server import LanguageServer
from typing import List, Any, Dict
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# --- MCP 服务器设置 ---
# 创建一个 LanguageServer 实例，用于处理 MCP 请求
server = LanguageServer("mcp-server", "v0.1")
# 定义基础路径
BASE_PATH = os.path.abspath('d:/gswfile')
# 初始化 MCP 状态信息
mcp_status = {
    "status": "运行中",
    "requests_received": 0,
    "last_request": None,
    "tool_calls": {},
    "server_start_time": time.time(),
}

# --- 工具定义 ---
# 定义所有可用的工具及其描述和输入模式
TOOL_DEFINITIONS = {
    'list-projects': {
        "title": "列出项目",
        "description": "列出 D:/wwwroot 中的所有顶级项目目录",
        "inputSchema": {},
    },
    'list-files': {
        'title': '列出文件',
        'description': '列出给定路径中的文件和目录。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string', 'default': '.'},
                'recursive': {'type': 'boolean', 'default': False},
                'maxDepth': {'type': 'integer', 'default': 3},
            }
        },
    },
    'read-file': {
        'title': '读取文件',
        'description': '读取文件的内容。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string'}
            },
            'required': ['path']
        },
    },
    'write-file': {
        'title': '写入文件',
        'description': '将内容写入文件。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string'},
                'content': {'type': 'string'}
            },
            'required': ['path', 'content']
        },
    },
    'delete-path': {
        'title': '删除路径',
        'description': '删除文件或空目录。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'path': {'type': 'string'}
            },
            'required': ['path']
        },
    },
    'run-command': {
        'title': '运行命令',
        'description': '执行一个 shell 命令。',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'command': {'type': 'string'},
                'cwd': {'type': 'string'}
            },
            'required': ['command']
        },
    },
    'reboot-server': {
        'title': '重启服务器',
        'description': '重启 MCP 服务器。',
        'inputSchema': {},
    }
}

# --- MCP 生命周期方法 ---
@server.feature("initialize")
async def initialize(params: Any) -> Dict[str, Any]:
    """处理 MCP 初始化请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "initialize"
    return {
        "capabilities": {
            "tools": [v for k, v in TOOL_DEFINITIONS.items()]
        }
    }

@server.feature("shutdown")
async def shutdown(params: Any) -> None:
    """处理 MCP 关闭请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "shutdown"
    pass

# --- 工具实现 ---
@server.feature("list-projects")
async def list_projects_handler(params: Any) -> Dict[str, Any]:
    """处理 list-projects 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "list-projects"
    if "list-projects" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["list-projects"] = 0
    mcp_status["tool_calls"]["list-projects"] += 1
    try:
        entries = os.listdir(BASE_PATH)
        projects = [{"name": entry} for entry in entries if os.path.isdir(os.path.join(BASE_PATH, entry))]
        return {"projects": projects}
    except Exception as e:
        return {"error": str(e)}

@server.feature("list-files")
async def list_files_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 list-files 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "list-files"
    if "list-files" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["list-files"] = 0
    mcp_status["tool_calls"]["list-files"] += 1
    path = params.get('path', '.')
    recursive = params.get('recursive', False)
    max_depth = params.get('maxDepth', 3)
    
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
        return {"error": "路径不存在或不是目录"}

    files = []
    total_size = 0
    for root, dirs, file_names in os.walk(abs_path):
        current_depth = root.replace(abs_path, '').count(os.sep)
        if not recursive and current_depth > 0:
            continue
        if current_depth > max_depth:
            continue

        for d in dirs:
            files.append({"name": d, "path": os.path.relpath(os.path.join(root, d), BASE_PATH), "isDirectory": True, "size": 0})
        for f in file_names:
            file_path = os.path.join(root, f)
            size = os.path.getsize(file_path)
            total_size += size
            files.append({"name": f, "path": os.path.relpath(file_path, BASE_PATH), "isDirectory": False, "size": size})
        
        if not recursive:
            dirs.clear()

    return {"files": files, "totalSize": total_size}

@server.feature("read-file")
async def read_file_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 read-file 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "read-file"
    if "read-file" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["read-file"] = 0
    mcp_status["tool_calls"]["read-file"] += 1
    path = params.get('path')
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return {"error": "文件不存在或不是文件"}

    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@server.feature("write-file")
async def write_file_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 write-file 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "write-file"
    if "write-file" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["write-file"] = 0
    mcp_status["tool_calls"]["write-file"] += 1
    path = params.get('path')
    content = params.get('content')
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    try:
        bytes_written = 0
        with open(abs_path, 'w', encoding='utf-8') as f:
            bytes_written = f.write(content)
        return {"path": path, "bytesWritten": bytes_written}
    except Exception as e:
        return {"error": str(e)}

@server.feature("delete-path")
async def delete_path_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 delete-path 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "delete-path"
    if "delete-path" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["delete-path"] = 0
    mcp_status["tool_calls"]["delete-path"] += 1
    path = params.get('path')
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path):
        return {"error": "路径不存在"}

    try:
        if os.path.isfile(abs_path):
            os.remove(abs_path)
        elif os.path.isdir(abs_path):
            os.rmdir(abs_path)
        return {"path": path, "deleted": True}
    except Exception as e:
        return {"error": str(e)}

@server.feature("run-command")
async def run_command_handler(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理 run-command 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "run-command"
    if "run-command" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["run-command"] = 0
    mcp_status["tool_calls"]["run-command"] += 1
    command = params.get('command')
    cwd = params.get('cwd')
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        stdout, stderr = await proc.communicate()
        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "exitCode": proc.returncode
        }
    except Exception as e:
        return {"error": str(e)}

@server.feature("reboot-server")
async def reboot_server_handler(params: Any) -> Dict[str, Any]:
    """处理 reboot-server 工具的请求。"""
    mcp_status["requests_received"] += 1
    mcp_status["last_request"] = "reboot-server"
    if "reboot-server" not in mcp_status["tool_calls"]:
        mcp_status["tool_calls"]["reboot-server"] = 0
    mcp_status["tool_calls"]["reboot-server"] += 1
    try:
        # 这是一个 hack。我们只是重新执行当前进程。
        os.execv(sys.executable, ['python'] + sys.argv)
        return {"status": "rebooting"}
    except Exception as e:
        return {"error": str(e)}

# --- FastAPI 应用 ---
# 创建一个 FastAPI 实例
app = FastAPI()

# 设置模板目录
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """处理根路径的 GET 请求，返回主页。"""
    mcp = {
        "name": "MCP 文件服务",
        "url": "http://127.0.0.1:8000/mcp",
        "tools": ["list_files", "read_file", "write_file", "delete_path", "run_command"],
    }
    return templates.TemplateResponse("index.html", {"request": request, "mcp": mcp})

@app.get("/files", response_class=HTMLResponse)
async def read_files(request: Request):
    """提供文件浏览器页面"""
    return templates.TemplateResponse("files.html", {"request": request})

@app.get("/api/files")
async def api_list_files(path: str = '.'):
    """处理 /api/files 的 GET 请求，列出文件。"""
    return await list_files_handler({'path': path, 'recursive': True, 'maxDepth': 100})

@app.get("/api/files/raw/{path:path}")
async def api_read_file_raw(path: str):
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return Response(status_code=404, content="File not found")
    ext = os.path.splitext(abs_path)[1].lower()
    media_type = "application/octet-stream"
    if ext == ".mp3":
        media_type = "audio/mpeg"
    try:
        f = open(abs_path, 'rb')
        return StreamingResponse(f, media_type=media_type)
    except Exception as e:
        return Response(status_code=500, content=str(e))

@app.get("/api/files/{path:path}")
async def api_read_file(path: str):
    """处理 /api/files/{path} 的 GET 请求，读取文件。"""
    return await read_file_handler({'path': path})

@app.post("/api/files")
async def api_write_file(item: dict):
    """处理 /api/files 的 POST 请求，写入文件。"""
    return await write_file_handler(item)

@app.delete("/api/files/{path:path}")
async def api_delete_file(path: str):
    """处理 /api/files/{path} 的 DELETE 请求，删除文件。"""
    return await delete_path_handler({'path': path})


@app.get("/monitor", response_class=HTMLResponse)
async def monitor(request: Request):
    """处理 /monitor 的 GET 请求，返回监控页面。"""
    return templates.TemplateResponse("monitor.html", {"request": request, "status": mcp_status})

@app.get("/mcp", response_class=HTMLResponse)
async def mcp_info(request: Request):
    """MCP 服务介绍页面"""
    mcp = {
        "name": "MCP 文件服务",
        "url": "http://127.0.0.1:8000/mcp",
        "tools": ["list_files", "read_file", "write_file", "delete_path", "run_command"],
    }
    return templates.TemplateResponse("mcp.html", {"request": request, "mcp": mcp})

@app.get("/mcp-status")
def get_mcp_status():
    """处理 /mcp-status 的 GET 请求，返回 MCP 状态。"""
    return mcp_status

# --- 主程序入口 ---
if __name__ == "__main__":
    # 启动 uvicorn 服务器
    uvicorn.run(app, host="127.0.0.1", port=8888)