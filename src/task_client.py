from pathlib import Path
from typing import Any
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class TaskClient:
    """Client to interact with Google Tasks API."""

    def __init__(self, credentials: Credentials):
        self.credentials = credentials
        self.service = build("tasks", "v1", credentials=credentials)

    @classmethod
    def from_oauth_config(
        cls,
        client_config_path: str,
        token_file_path: str,
        oauth_port: int,
        scopes: list[str],
    ) -> "TaskClient":
        """Create a TaskClient from OAuth configuration."""
        credentials: Credentials | None = None
        token_file = Path(token_file_path)

        if token_file.exists():
            credentials = Credentials.from_authorized_user_file(token_file_path, scopes)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(client_config_path, scopes)
                credentials = flow.run_local_server(port=oauth_port)
            
            if credentials is None:
                raise RuntimeError("Failed to obtain OAuth credentials")
            
            with open(token_file_path, "w") as token:
                token.write(credentials.to_json())
        
        if credentials is None:
            raise RuntimeError("Failed to obtain OAuth credentials after all attempts")
        return cls(credentials)

    def tl_list(self) -> list[dict[str, Any]]:
        """List all task lists."""
        ret = self.service.tasklists().list().execute().get("items", [])
        return ret

    def tl_add(self, title: str) -> dict[str, Any]:
        """Add a new task list."""
        ret = self.service.tasklists().insert(body={"title": title}).execute()
        return ret

    def tl_delete(self, tasklist_id: str) -> dict[str, Any]:
        """Delete a task list."""
        ret = self.service.tasklists().delete(tasklist=tasklist_id).execute()
        return ret

    def tl_update(self, tasklist_id: str, title: str) -> dict[str, Any]:
        """Update a task list."""
        # First get the current tasklist
        current_tasklist = self.service.tasklists().get(tasklist=tasklist_id).execute()
        # Update the title
        current_tasklist['title'] = title
        # Update the tasklist with the full object
        ret = self.service.tasklists().update(tasklist=tasklist_id, body=current_tasklist).execute()
        return ret

    
    def task_list(self, tasklist_id: str) -> list[dict[str, Any]]:
        """List all tasks in a task list."""
        ret = self.service.tasks().list(tasklist=tasklist_id).execute().get("items", [])
        return ret

    def task_add(self, tasklist_id: str, title: str, description: str | None = None, due: str | None = None) -> dict[str, Any]:
        """Add a new task to a task list."""
        ret = self.service.tasks().insert(tasklist=tasklist_id, body={"title": title, "notes": description, "due": due}).execute()
        return ret

    def task_delete(self, tasklist_id: str, task_id: str) -> dict[str, Any]:
        """Delete a task from a task list."""
        ret = self.service.tasks().delete(tasklist=tasklist_id, task=task_id).execute()
        return ret

    def task_update(self, tasklist_id: str, task_id: str, title: str | None = None, description: str | None = None, due: str | None = None) -> dict[str, Any]:
        """Update a task in a task list."""
        # First get the current task
        current_task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        # Update the fields that were provided
        if title is not None:
            current_task['title'] = title
        if description is not None:
            current_task['notes'] = description
        if due is not None:
            current_task['due'] = due
        # Update the task with the full object
        ret = self.service.tasks().update(tasklist=tasklist_id, task=task_id, body=current_task).execute()
        return ret

    def task_complete(self, tasklist_id: str, task_id: str) -> dict[str, Any]:
        """Complete a task in a task list."""
        current_task = self.service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        current_task['status'] = 'completed'
        # also set the completed field to a RFC 3339 date string
        current_task['completed'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        ret = self.service.tasks().update(tasklist=tasklist_id, task=task_id, body=current_task).execute()
        return ret