import asyncio
import aiohttp
from dotenv import load_dotenv
import os

from models.endpoint_consts import TODO_ENDPOINT, FETCH_TOKEN

load_dotenv()
app_name = os.getenv('APPLICATION_NAME')
HABITICA_PW = os.getenv('HABITICA_PW')
HABITICA_USER = os.getenv('HABITICA_USER')
BASE_URL = os.getenv('HABITICA_BASE_URL')


## Habitica Rules
# Add a condition that stops automatic calls if the action can no longer be completed, such as running out of Mana when using Skills.
# For automated scripts that run in the background, include a delay of 30 seconds between API calls. This includes POST, PUT, and GET calls.
# All API calls must include an "x-client" header

class HabiticaManager:
    def __init__(self):
        self.session = None
        self.token = None
        self.username = HABITICA_USER
        self.user_id = None
        self.x_client = None
        self.headers = None

    def get_username(self):
        """Get current user's Habitica username"""
        return self.username
    def set_username(self, username):
        """Set current user Habitica username"""
        self.username = username
    def get_x_client(self):
        """Get current user's Habitica x_client id"""
        return self.x_client
    def set_x_client(self, x_client):
        """Set current user Habitica x_client id"""
        self.x_client = x_client

    def ensure_session(self):
        """Ensure we have an active aiohttp session"""
        if self.session is None or self.session.closed:
            # If not, create and store a new client session
            if not self.headers:
                return 404, "No header info available"
            elif not self.x_client:
                return 404, "No x_client info available"
            else:
                self.session = aiohttp.ClientSession(headers=self.headers)
                return 200, "Session created"
        else:
            return 100, "Session already active"

    async def close_session(self):
        """Close and clean up the session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def habitica_request(self, endpoint, method="GET", data=None):
        """Make async request to Habitica API"""
        active_session = self.ensure_session()
        if active_session[0] != 200 and active_session[0] != 100:
            return active_session

        if self.token is None or self.user_id is None:
            await self.fetch_token()

        url = f"{BASE_URL}{endpoint}"

        try:
            if method == "GET":
                async with self.session.get(url, headers=self.headers, data=data) as response:
                    print(f"Got response from Habitica: {response}")
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 400:
                        return None, f"Bad Request: {response.status}"
                    elif response.status == 401:
                        return None, f"Unauthorized: {response.status}"
                    else:
                        return None, f"API Error: {response.status}"
            if method == "POST":
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
            return None, f"Request timed out"

    async def fetch_token(self):
        """Fetch a new token from Habitica"""
        # Ensure we have a session for the login request
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

        body = {"username": self.username, "password": HABITICA_PW}
        async with self.session.post(f"{BASE_URL}{FETCH_TOKEN}", json=body) as response:
            print(f"Got response from Habitica: {response}")
            if response.status == 200:
                login_body = await response.json()
                self.token = login_body["apiToken"]
                self.user_id = login_body["_id"]
                self.set_x_client(f"{login_body['_id']}-PAPA")
                self.headers = {"x-client": self.x_client, "x-api-user": self.user_id, "x-api-key": self.token}

    async def create_todo(self, text, task_type, tags, alias, attribute, checklist, collapse_checklist, notes, date,
                          priority,
                          reminders, frequency, repeat, every_x, streak, days_of_month, weeks_of_month, start_date, up,
                          down, value):
        """Create a to-do task item in Habitica"""
        body = {
            "text": text, "type": task_type, "tags": tags, "alias": alias, "attribute": attribute, "checklist": checklist,
            "collapse_checklist": collapse_checklist, "notes": notes, "date": date, "priority": priority,
            "reminders": reminders, "frequency": frequency, "repeat": repeat, "every_x": every_x, "streak": streak,
            "days_of_month": days_of_month, "weeks_of_month": weeks_of_month, "start_date": start_date, "up": up,
            "down": down, "value": value
        }
        return await self.habitica_request()

    async def get_todos(self, task_type):
        params = {"type": task_type}
        return await self.habitica_request(TODO_ENDPOINT, method="GET", data=params)



