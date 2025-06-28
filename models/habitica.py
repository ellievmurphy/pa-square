import asyncio
import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()
app_name = os.getenv('APPLICATION_NAME')
pw = os.getenv('HABITICA_PASSWORD')
BASE_URL = f"https://api.habitica.com/v3"


## Habitica Rules
# Add a condition that stops automatic calls if the action can no longer be completed, such as running out of Mana when using Skills.
# For automated scripts that run in the background, include a delay of 30 seconds between API calls. This includes POST, PUT, and GET calls.
# All API calls must include an "x-client" header

class HabiticaManager:
    def __init__(self):
        self.session = None
        self.token = None
        self.username = None
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
        """Get current user's Habitica username"""
        return self.x_client
    def set_x_client(self, x_client):
        """Set current user Habitica username"""
        self.x_client = x_client

    async def ensure_session(self):
        """Ensure we have an active aiohttp session"""
        if self.session is None or self.session.closed:
            # If not, create a store a new client session
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

    async def habitica_request(self, endpoint, headers, method="GET", data=None):
        """Make async request to Habitica API"""
        await self.ensure_session()

        url = f"{BASE_URL}{endpoint}"

        try:
            if method == "GET":
                async with self.session.get(url, headers=headers, data=data) as response:
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
                async with self.session.post(url, headers=headers, json=data) as response:
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
        body = {"username": self.username, "password": pw}
        async with self.session.post(f"{BASE_URL}/user/auth/local/login", json=body,
                                     headers={"x-client": x_client}) as response:
            print(f"Got response from Habitica: {response}")
            if response.status == 200:
                login_body = await response.json()
                self.token = login_body["apiToken"]
                self.user_id = login_body["_id"]

    async def create_todo(self, text, type, tags, alias, attribute, checklist, collapse_checklist, notes, date,
                          priority,
                          reminders, frequency, repeat, every_x, streak, days_of_month, weeks_of_month, start_date, up,
                          down, value):
        """Create a to-do task item in Habitica"""
        body = {
            "text": text, "type": type, "tags": tags, "alias": alias, "attribute": attribute, "checklist": checklist,
            "collapse_checklist": collapse_checklist, "notes": notes, "date": date, "priority": priority,
            "reminders": reminders, "frequency": frequency, "repeat": repeat, "every_x": every_x, "streak": streak,
            "days_of_month": days_of_month, "weeks_of_month": weeks_of_month, "start_date": start_date, "up": up,
            "down": down, "value": value
        }
        self.habitica_request()

    async def get_todos(self, type, due_date):
        headers = {"x-client": x_client}
        params = {"type": type, "due_date": due_date}
