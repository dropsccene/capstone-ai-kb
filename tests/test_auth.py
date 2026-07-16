from tests.conftest import create_test_token


def test_register(client):
    response = client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    assert response.status_code == 200
    assert "id" in response.json()

def test_register_duplicate(client):
    client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    response = client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    assert response.status_code == 400

def test_register_weak_password(client):
    response = client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123"})
    assert response.status_code == 200

def test_login_wrong_password(client):
    client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    response = client.post("/api/auth/login",json={"username":"testuser","password":"wrongpassword"})
    assert response.status_code == 401

def test_login(client):
    client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    response = client.post("/api/auth/login",json={"username":"testuser","password":"123456"})
    assert response.status_code == 200
    assert response.json()["access_token"] 
    assert response.json()["token_type"] == "bearer"

def test_me(client):
    client.post("/api/auth/register",json={"username":"testuser","email":"test@test.com","password":"123456"})
    token = create_test_token(user_id=1)
    response = client.get("/api/auth/me",headers={"Authorization":f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401