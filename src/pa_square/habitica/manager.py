"""Habitica API manager for async operations."""

import asyncio
from typing import Any, Dict, Optional, Tuple

import aiohttp

from src.pa_square.config import config
from src.pa_square.habitica.constants import FETCH_TOKEN, TODO_ENDPOINT


class HabiticaManager:
    """
    Manages async interactions with the Habitica API.
    
    Habitica API Rules:
    - Add a condition that stops automatic calls if the action can no longer be completed,
      such as running out of Mana when using Skills.
    - For automated scripts that run in the background, include a delay of 30 seconds
      between API calls. This includes POST, PUT, and GET calls.
    - All API calls must include an "x-client" header.
    """
    
    def __init__(self) -> None:
        self.session: Optional[aiohttp.ClientSession] = None
        self.token: Optional[str] = None
        self.username: str = config.HABITICA_USER
        self.user_id: Optional[str] = None
        self.x_client: Optional[str] = None
        self.headers: Optional[Dict[str, str]] = None
        self.base_url: str = config.HABITICA_BASE_URL
    
    def get_username(self) -> str:
        """Get current user's Habitica username."""
        return self.username
    
    def set_username(self, username: str) -> None:
        """Set current user Habitica username."""
        self.username = username
    
    def get_x_client(self) -> Optional[str]:
        """Get current user's Habitica x_client id."""
        return self.x_client
    
    def set_x_client(self, x_client: str) -> None:
        """Set current user Habitica x_client id."""
        self.x_client = x_client
    
    def ensure_session(self) -> Tuple[int, str]:
        """
        Ensure we have an active aiohttp session.
        
        Returns:
            Tuple of (status_code, message)
        """
        if self.session is None or self.session.closed:
            if not self.headers:
                return 404, "No header info available"
            elif not self.x_client:
                return 404, "No x_client info available"
            else:
                self.session = aiohttp.ClientSession(headers=self.headers)
                return 200, "Session created"
        else:
            return 100, "Session already active"
    
    async def close_session(self) -> None:
        """Close and clean up the session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def habitica_request(
        self,
        endpoint: str,
        method: str = "GET",
        data: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Make async request to Habitica API.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method (GET, POST, etc.)
            data: Optional data payload
            
        Returns:
            API response or tuple of (None, error_message)
        """
        active_session = self.ensure_session()
        if active_session[0] not in (200, 100):
            return active_session
        
        if self.token is None or self.user_id is None:
            await self.fetch_token()
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                async with self.session.get(url, headers=self.headers, params=data) as response:
                    print(f"Got response from Habitica: {response}")
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 400:
                        return None, f"Bad Request: {response.status}"
                    elif response.status == 401:
                        return None, f"Unauthorized: {response.status}"
                    else:
                        return None, f"API Error: {response.status}"
            
            elif method == "POST":
                async with self.session.post(url, headers=self.headers, json=data) as response:
                    print(f"Got response from Habitica: {response}")
                    if response.status == 201:
                        return await response.json()
                    elif response.status == 400:
                        return None, f"Bad Request: {response.status}"
                    elif response.status == 401:
                        return None, f"Unauthorized: {response.status}"
                    else:
                        return None, f"API Error: {response.status}"
        
        except aiohttp.ClientError as e:
            return None, f"Request failed: {str(e)}"
        except asyncio.TimeoutError:
            return None, "Request timed out"
    
    async def fetch_token(self) -> None:
        """Fetch a new token from Habitica."""
        # Ensure we have a session for the login request
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        
        body = {"username": self.username, "password": config.HABITICA_PW}
        async with self.session.post(f"{self.base_url}{FETCH_TOKEN}", json=body) as response:
            if response.status == 200:
                response_json = await response.json()
                login_body = response_json["data"]
                self.token = login_body["apiToken"]
                self.user_id = login_body["id"]
                self.set_x_client(f"{login_body['id']}-PAPA")
                self.headers = {
                    "x-client": self.x_client,
                    "x-api-user": self.user_id,
                    "x-api-key": self.token,
                }
    
    async def create_todo(
        self,
        text: str,
        task_type: str,
        tags: Optional[list] = None,
        alias: Optional[str] = None,
        attribute: Optional[str] = None,
        checklist: Optional[list] = None,
        collapse_checklist: bool = False,
        notes: Optional[str] = None,
        date: Optional[str] = None,
        priority: float = 1.0,
        reminders: Optional[list] = None,
        frequency: str = "daily",
        repeat: Optional[Dict] = None,
        every_x: int = 1,
        streak: int = 0,
        days_of_month: Optional[list] = None,
        weeks_of_month: Optional[list] = None,
        start_date: Optional[str] = None,
        up: bool = True,
        down: bool = False,
        value: float = 0.0,
    ) -> Any:
        """
        Create a to-do task item in Habitica.
        
        Args:
            text: Task text/title
            task_type: Type of task (todo, habit, daily, reward)
            Additional args: See Habitica API documentation
            
        Returns:
            API response
            :param notes: Additional details in Habitica task
            :param date: Due date of task
            :param priority: Priority of task
            :param reminders: List of date-times for reminders
            :param frequency: How often the task occurs
            :param repeat: How often the task repeats
            :param every_x: Does the task occur on specific days of the week
            :param streak: Task completion streak
            :param days_of_month: Array of integers. Only valid for type "daily"
            :param weeks_of_month: Array of integers. Only valid for type "daily"
            :param start_date: Date when the task will first become available. Only valid for type "daily"
            :param up: Only valid for type "habit" If true, enables the "+" under "Directions/Action" for "Good habits"
            :param down: Only valid for type "habit" If true, enables the "-" under "Directions/Action" for "Bad habits"
            :param value: Only valid for type "reward." The cost in gold of the reward. Should be greater then or equal to 0.
            :param collapse_checklist: Default value false. Determines if checklist is displayed
            :param checklist: An array of checklist items. For example, [{"text":"buy tools", "completed":true}, {"text":"build shed", "completed":false}]
            :param attribute: User's attribute to use, options are: "str", "int", "per", "con"
            :param task_type: Task type, options are: "habit", "daily", "todo", "reward".
            :param text: The text to be displayed for the task
            :param alias: Alias to assign to task
            :param tags: Array of UUIDs of tags
        """
        body = {
            "text": text,
            "type": task_type,
            "tags": tags or [],
            "alias": alias,
            "attribute": attribute,
            "checklist": checklist or [],
            "collapseChecklist": collapse_checklist,
            "notes": notes,
            "date": date,
            "priority": priority,
            "reminders": reminders or [],
            "frequency": frequency,
            "repeat": repeat,
            "everyX": every_x,
            "streak": streak,
            "daysOfMonth": days_of_month or [],
            "weeksOfMonth": weeks_of_month or [],
            "startDate": start_date,
            "up": up,
            "down": down,
            "value": value,
        }
        return await self.habitica_request(TODO_ENDPOINT, method="POST", data=body)
    
    async def get_todos(self, task_type: str = "todos") -> Any:
        """
        Get todos from Habitica.
        
        Args:
            task_type: Type of tasks to retrieve
            
        Returns:
            API response with todos
        """
        params = {"type": task_type}
        return await self.habitica_request(TODO_ENDPOINT, method="GET", data=params)
