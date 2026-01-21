import pytest
from app.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home route."""
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Hello, World!", "status": "running"}

def test_add(client):
    """Test the add route."""
    response = client.get('/add/2/3')
    assert response.status_code == 200
    assert response.json == {"result": 5}

def test_add_failure(client):
    """
    DELIBERATE FAILURE: This test expects 2 + 2 = 5.
    The AI Agent should fix this by changing the assertion to 4.
    """
    response = client.get('/add/2/2')
    assert response.status_code == 200
    # BUG: The code returns 4, but we assert 5
    assert response.json == {"result": 5} 
