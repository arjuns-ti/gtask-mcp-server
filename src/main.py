"""MCP Server for Google Tasks"""

import logging
from typing import Annotated, Any
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from pydantic import Field

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

@mcp.tool()
def get_current_datetime():
    """Get the current date and time"""
    logger.debug("Getting current date and time")
    t = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
    return {
        #in iso format with day of the week
        "local_time": t.isoformat() + " " + t.strftime("%A"),
    }

@mcp.tool()
def list_tasklists():
    """Get all task lists"""
    logger.debug("Listing task lists")
    lists = get_task_client().tl_list()
    logger.debug(f"Lists: {lists}")
    return lists

@mcp.tool()
def add_tasklist(title: Annotated[str, Field(description="The title/name for the new task list")]):
    """Add a new task list"""
    logger.debug(f"Adding task list: {title}")
    ret = get_task_client().tl_add(title)
    logger.debug(f"Task list added: {ret}")
    return ret

@mcp.tool()
def delete_tasklist(tasklist_id: Annotated[str, Field(description="The unique identifier of the task list to delete")]):
    """Delete a task list"""
    logger.debug(f"Deleting task list: {tasklist_id}")
    ret = get_task_client().tl_delete(tasklist_id)
    logger.debug(f"Task list deleted: {ret}")
    return ret

@mcp.tool()
def update_tasklist(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the task list to update")],
    title: Annotated[str, Field(description="The new title/name for the task list")]
):
    """Update a task list"""
    logger.debug(f"Updating task list: {tasklist_id}")
    ret = get_task_client().tl_update(tasklist_id, title)
    logger.debug(f"Task list updated: {ret}")
    return ret

@mcp.tool()
def list_tasks(tasklist_id: Annotated[str, Field(description="The unique identifier of the task list to retrieve tasks from")]):
    """List all tasks in a task list"""
    logger.debug(f"Listing tasks: {tasklist_id}")
    tasks = get_task_client().task_list(tasklist_id)
    logger.debug(f"Tasks: {tasks}")
    return tasks

@mcp.tool()
def add_task(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the task list to add the task to")],
    title: Annotated[str, Field(description="The title of the task")],
    description: Annotated[str | None, Field(description="The description/notes for the task (optional)")] = None,
    due_date: Annotated[str | None, Field(description="The due date in DD/MM/YYYY format (optional)")] = None
):
    """
    Add a new task to a task list
    """
    logger.debug(f"Adding task: {title}")
    due = None
    if due_date:
        # convert due_date from DD/MM/YYYY to RFC 3339 date string
        due = datetime.strptime(due_date, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ret = get_task_client().task_add(tasklist_id, title, description, due)
    logger.debug(f"Task added: {ret}")
    return ret

@mcp.tool()
def delete_task(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the task list containing the task")],
    task_id: Annotated[str, Field(description="The unique identifier of the task to delete")]
):
    """Delete a task from a task list"""
    logger.debug(f"Deleting task: {task_id}")
    ret = get_task_client().task_delete(tasklist_id, task_id)
    logger.debug(f"Task deleted: {ret}")
    return ret

@mcp.tool()
def update_task(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the task list containing the task")],
    task_id: Annotated[str, Field(description="The unique identifier of the task to update")],
    title: Annotated[str | None, Field(description="The new title for the task (optional, no change if not provided)")] = None,
    description: Annotated[str | None, Field(description="The new description/notes for the task (optional, no change if not provided)")] = None,
    due_date: Annotated[str | None, Field(description="The new due date in DD/MM/YYYY format (optional, no change if not provided)")] = None
):
    """Update a task in a task list"""
    logger.debug(f"Updating task: {task_id}")
    due = None
    if due_date:
        # convert due_date from DD/MM/YYYY to RFC 3339 date string
        due = datetime.strptime(due_date, "%d/%m/%Y").strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    ret = get_task_client().task_update(tasklist_id, task_id, title, description, due)
    logger.debug(f"Task updated: {ret}")
    return ret

@mcp.tool()
def complete_task(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the task list containing the task")],
    task_id: Annotated[str, Field(description="The unique identifier of the task to mark as completed")]
):
    """Complete a task in a task list"""
    logger.debug(f"Completing task: {task_id}")
    ret = get_task_client().task_complete(tasklist_id, task_id)
    logger.debug(f"Task completed: {ret}")
    return ret

@mcp.tool()
def move_task(
    tasklist_id: Annotated[str, Field(description="The unique identifier of the current task list containing the task")],
    task_id: Annotated[str, Field(description="The unique identifier of the task to move")],
    new_tasklist_id: Annotated[str, Field(description="The unique identifier of the destination task list")]
):
    """Move a task to a different task list"""
    logger.debug(f"Moving task: {task_id} to {new_tasklist_id}")
    ret = get_task_client().task_move(tasklist_id, task_id, new_tasklist_id)
    logger.debug(f"Task moved: {ret}")
    return ret

if __name__ == "__main__":
    mcp.run(transport="stdio")