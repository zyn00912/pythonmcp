import os
import asyncio
from typing import Any, Dict, List

from fastmcp import FastMCP

# 基础路径，与 FastAPI 保持一致
BASE_PATH = os.path.abspath('d:/gswfile')

mcp = FastMCP(name="MCP 文件服务")

@mcp.tool
def list_files(path: str = '.', recursive: bool = False, max_depth: int = 3) -> Dict[str, Any]:
    """列出给定路径中的文件和目录（相对 BASE_PATH）。"""
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
        return {"error": "路径不存在或不是目录"}

    files: List[Dict[str, Any]] = []
    total_size = 0
    for root, dirs, file_names in os.walk(abs_path):
        current_depth = root.replace(abs_path, '').count(os.sep)
        if not recursive and current_depth > 0:
            continue
        if current_depth > max_depth:
            continue
        for d in dirs:
            files.append({
                "name": d,
                "path": os.path.join(root, d).replace(BASE_PATH, ''),
                "isDirectory": True,
                "size": 0
            })
        for f in file_names:
            file_path = os.path.join(root, f)
            size = os.path.getsize(file_path)
            total_size += size
            files.append({
                "name": f,
                "path": file_path.replace(BASE_PATH, ''),
                "isDirectory": False,
                "size": size
            })
        if not recursive:
            dirs.clear()

    return {"files": files, "totalSize": total_size}

@mcp.tool
def read_file(path: str) -> Dict[str, Any]:
    """读取文件内容（相对 BASE_PATH）。"""
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    if not os.path.exists(abs_path) or not os.path.isfile(abs_path):
        return {"error": "文件不存在或不是文件"}
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def write_file(path: str, content: str) -> Dict[str, Any]:
    """写入文件内容（相对 BASE_PATH）。"""
    abs_path = os.path.abspath(os.path.join(BASE_PATH, path))
    try:
        with open(abs_path, 'w', encoding='utf-8') as f:
            bytes_written = f.write(content)
        return {"path": path, "bytesWritten": bytes_written}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool
def delete_path(path: str) -> Dict[str, Any]:
    """删除文件或空目录（相对 BASE_PATH）。"""
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

@mcp.tool
async def run_command(command: str, cwd: str | None = None) -> Dict[str, Any]:
    """执行一个 shell 命令并返回结果。"""
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
            "exitCode": proc.returncode,
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # 直接运行 FastMCP 服务器；也可使用 CLI：`fastmcp run mcp_server.py`
    mcp.run()