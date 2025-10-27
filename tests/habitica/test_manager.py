import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import aiohttp


@pytest.fixture
def habitica_manager():
    """Fixture to create a HabiticaManager instance"""
    from src.pa_square.habitica.manager import HabiticaManager
    return HabiticaManager()


@pytest.fixture
def mock_env_vars():
    """Fixture to mock environment variables"""
    with patch.dict('os.environ', {
        'APPLICATION_NAME': 'test_app',
        'HABITICA_PW': 'test_password',
        'HABITICA_USER': 'test_user',
        'HABITICA_BASE_URL': 'https://habitica.com/api/v3'
    }):
        yield


class TestHabiticaManager:
    APPLICATION_NAME = "test_app"
    HABITICA_PW = "test_password"
    HABITICA_USER = "test_user"
    HABITICA_BASE_URL = "https://habitica.com/api/v3"
    
    def test_initialization(self, habitica_manager):
        """Test HabiticaManager initialization"""
        assert habitica_manager.session is None
        assert habitica_manager.token is None
        assert habitica_manager.username is not None
        assert habitica_manager.user_id is None
        assert habitica_manager.x_client is None
        assert habitica_manager.headers is None

    def test_get_username(self, habitica_manager):
        """Test getting username"""
        habitica_manager.username = "test_user"
        assert habitica_manager.get_username() == "test_user"

    def test_set_username(self, habitica_manager):
        """Test setting username"""
        habitica_manager.set_username("new_user")
        assert habitica_manager.username == "new_user"

    def test_get_x_client(self, habitica_manager):
        """Test getting x_client"""
        habitica_manager.x_client = "test_client_id"
        assert habitica_manager.get_x_client() == "test_client_id"

    def test_set_x_client(self, habitica_manager):
        """Test setting x_client"""
        habitica_manager.set_x_client("new_client_id")
        assert habitica_manager.x_client == "new_client_id"

    def test_ensure_session_no_headers(self, habitica_manager):
        """Test ensure_session when headers are not set"""
        status, message = habitica_manager.ensure_session()
        assert status == 404
        assert message == "No header info available"

    def test_ensure_session_no_x_client(self, habitica_manager):
        """Test ensure_session when x_client is not set"""
        habitica_manager.headers = {"test": "header"}
        status, message = habitica_manager.ensure_session()
        assert status == 404
        assert message == "No x_client info available"

    def test_ensure_session_creates_new_session(self, habitica_manager):
        """Test ensure_session creates a new session when needed"""
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        with patch('aiohttp.ClientSession') as mock_session:
            status, message = habitica_manager.ensure_session()
            assert status == 200
            assert message == "Session created"
            mock_session.assert_called_once_with(headers=habitica_manager.headers)

    def test_ensure_session_already_active(self, habitica_manager):
        """Test ensure_session when session is already active"""
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        # Create a mock session
        mock_session = Mock()
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        status, message = habitica_manager.ensure_session()
        assert status == 100
        assert message == "Session already active"

    @pytest.mark.asyncio
    async def test_close_session(self, habitica_manager):
        """Test closing an active session"""
        mock_session = AsyncMock()
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        await habitica_manager.close_session()
        mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_session_already_closed(self, habitica_manager):
        """Test closing a session that's already closed"""
        mock_session = AsyncMock()
        mock_session.closed = True
        habitica_manager.session = mock_session
        
        await habitica_manager.close_session()
        mock_session.close.assert_not_called()

    @pytest.mark.asyncio
    async def test_fetch_token_success(self, habitica_manager):
        """Test fetching token successfully"""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": {
                "apiToken": "test_token",
                "id": "test_user_id"
            }
        })
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.post = Mock(return_value=mock_response)
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            await habitica_manager.fetch_token()
            
            assert habitica_manager.token == "test_token"
            assert habitica_manager.user_id == "test_user_id"
            assert habitica_manager.x_client == "test_user_id-PAPA"
            assert habitica_manager.headers == {
                "x-client": "test_user_id-PAPA",
                "x-api-user": "test_user_id",
                "x-api-key": "test_token"
            }

    @pytest.mark.asyncio
    async def test_habitica_request_get_success(self, habitica_manager):
        """Test successful GET request"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": "test_data"})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.habitica_request("/test", method="GET")
        assert result == {"data": "test_data"}

    @pytest.mark.asyncio
    async def test_habitica_request_post_success(self, habitica_manager):
        """Test successful POST request"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"data": "created"})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.post = Mock(return_value=mock_response)
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.habitica_request("/test", method="POST", data={"test": "data"})
        assert result == {"data": "created"}

    @pytest.mark.asyncio
    async def test_habitica_request_unauthorized(self, habitica_manager):
        """Test handling 401 unauthorized response"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.habitica_request("/test", method="GET")
        assert result == (None, "Unauthorized: 401")

    @pytest.mark.asyncio
    async def test_habitica_request_bad_request(self, habitica_manager):
        """Test handling 400 bad request response"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.habitica_request("/test", method="GET")
        assert result == (None, "Bad Request: 400")

    @pytest.mark.asyncio
    async def test_get_todos(self, habitica_manager):
        """Test getting todos"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": [{"id": 1, "text": "Test todo"}]})
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock()
        
        mock_session = AsyncMock()
        mock_session.get = Mock(return_value=mock_response)
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.get_todos("todos")
        assert result == {"data": [{"id": 1, "text": "Test todo"}]}

    @pytest.mark.asyncio
    async def test_habitica_request_client_error(self, habitica_manager):
        """Test handling aiohttp ClientError"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"
        
        mock_session = AsyncMock()
        mock_session.get = Mock(side_effect=aiohttp.ClientError("Connection error"))
        mock_session.closed = False
        habitica_manager.session = mock_session
        
        result = await habitica_manager.habitica_request("/test", method="GET")
        assert result == (None, "Request failed: Connection error")

    @pytest.mark.asyncio
    async def test_habitica_request_timeout(self, habitica_manager):
        """Test handling timeout error"""
        habitica_manager.token = "test_token"
        habitica_manager.user_id = "test_user_id"
        habitica_manager.headers = {"test": "header"}
        habitica_manager.x_client = "test_client"

        mock_session = AsyncMock()
        mock_session.get = Mock(side_effect=asyncio.TimeoutError())
        mock_session.closed = False
        habitica_manager.session = mock_session

        result = await habitica_manager.habitica_request("/test", method="GET")
        assert result == (None, "Request timed out")
