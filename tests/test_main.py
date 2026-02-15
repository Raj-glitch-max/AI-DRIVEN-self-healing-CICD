import pytest
import json
from app.main import app, add, subtract

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_add():
    """Test the add function"""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    """Test the subtract function"""
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0
    assert subtract(-1, -1) == 0

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'flask-app'

def test_main_endpoint(client):
    """Test the main endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['message'] == 'AI-Driven Self-Healing CI/CD Platform'
    assert data['status'] == 'running'
    assert data['version'] == '1.0.0'

def test_api_add_endpoint(client):
    """Test the API add endpoint"""
    response = client.get('/api/add/2/3')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['operation'] == 'add'
    assert data['inputs'] == [2, 3]
    assert data['result'] == 5

def test_api_subtract_endpoint(client):
    """Test the API subtract endpoint"""
    response = client.get('/api/subtract/5/3')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['operation'] == 'subtract'
    assert data['inputs'] == [5, 3]
    assert data['result'] == 2

def test_failing_case():
    """This test is designed to fail to trigger the self-healing agent"""
    # This assertion is intentionally wrong to demonstrate the healing process
    # The AI should fix this to: assert add(2, 2) == 4
    assert add(2, 2) == 5  # This will fail and trigger healing

def test_edge_cases():
    """Test edge cases for mathematical operations"""
    # Test large numbers
    assert add(1000000, 2000000) == 3000000
    assert subtract(1000000, 500000) == 500000
    
    # Test negative numbers
    assert add(-5, -3) == -8
    assert subtract(-5, -3) == -2
