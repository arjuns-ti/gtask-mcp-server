"""MCP Server for Google Tasks"""

import logging
from typing import Any
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]

from task_client import TaskClient
from config import get_settings, Settings

logger = logging.getLogger(__name__)
mcp = FastMCP("gtask-mcp-server")

_task_client: TaskClient | None = None
_settings: Settings | None = None

def get_task_client() -> TaskClient:
    """Get or initialize the task client"""
    global _task_client, _settings
    if _task_client is None:
        if _settings is None:
            _settings = get_settings()
        _task_client = TaskClient.from_oauth_config(
            client_config_path=str(_settings.get_client_config_path()),
            token_file_path=str(_settings.get_token_file_path()),
            oauth_port=_settings.google_oauth_port,
            scopes=_settings.google_task_api_scopes,
        )
    return _task_client

@mcp.toll()
def get_current_datetime():
    """Get the current date and time in GMT+5:30"""
    logger.debug("Getting current date and time")
    return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30))).isoformat()

@mcp.tool()
def list_tasklists():
    """Get all task lists"""
    logger.debug("Listing task lists")
    lists = get_task_client().tl_list()
    logger.debug(f"Lists: {lists}")
    return lists

@mcp.tool()
def add_tasklist(title: str):
    """Add a new task list"""
    logger.debug(f"Adding task list: {title}")
    ret = get_task_client().tl_add(title)
    logger.debug(f"Task list added: {ret}")
    return ret

@mcp.tool()
def delete_tasklist(tasklist_id: str):
    """Delete a task list"""
    logger.debug(f"Deleting task list: {tasklist_id}")
    ret = get_task_client().tl_delete(tasklist_id)
    logger.debug(f"Task list deleted: {ret}")
    return ret

@mcp.tool()
def update_tasklist(tasklist_id: str, title: str):
    """Update a task list"""
    logger.debug(f"Updating task list: {tasklist_id}")
    ret = get_task_client().tl_update(tasklist_id, title)
    logger.debug(f"Task list updated: {ret}")
    return ret

@mcp.tool()
def list_tasks(tasklist_id: str):
    """List all tasks in a task list"""
    logger.debug(f"Listing tasks: {tasklist_id}")
    tasks = get_task_client().task_list(tasklist_id)
    logger.debug(f"Tasks: {tasks}")
    return tasks

@mcp.tool()
def add_task(tasklist_id: str, title: str, description: str | None = None, due_ddmmyyyy: str | None = None):
    """Add a new task to a task list"""
    logger.debug(f"Adding task: {title}")
    # convert due_ddmmyyyy to a RFC 3339 date string
    due_date = datetime.strptime(due_ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ret = get_task_client().task_add(tasklist_id, title, description, due_date)
    logger.debug(f"Task added: {ret}")
    return ret

@mcp.tool()
def delete_task(tasklist_id: str, task_id: str):
    """Delete a task from a task list"""
    logger.debug(f"Deleting task: {task_id}")
    ret = get_task_client().task_delete(tasklist_id, task_id)
    logger.debug(f"Task deleted: {ret}")
    return ret

@mcp.tool()
def update_task(tasklist_id: str, task_id: str, title: str | None = None, description: str | None = None, due_ddmmyyyy: str | None = None):
    """Update a task in a task list"""
    logger.debug(f"Updating task: {task_id}")
    # convert due_ddmmyyyy to a RFC 3339 date string
    due_date = datetime.strptime(due_ddmmyyyy, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ret = get_task_client().task_update(tasklist_id, task_id, title, description, due_date)
    logger.debug(f"Task updated: {ret}")
    return ret

@mcp.tool()
def complete_task(tasklist_id: str, task_id: str):
    """Complete a task in a task list"""
    logger.debug(f"Completing task: {task_id}")
    ret = get_task_client().task_complete(tasklist_id, task_id)
    logger.debug(f"Task completed: {ret}")
    return ret

if __name__ == "__main__":
    mcp.run(transport="stdio")