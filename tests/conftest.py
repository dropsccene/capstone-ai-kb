import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import os
os.environ['DATABASE_URL'] = 'sqlite:///./test.db'
import pytest
from fastapi.testclient import TestClient
from app.database import Base, get_db, engine, SessionLocal
from app.main import app
from datetime import datetime, timedelta
from app.config import settings

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

def create_test_token(user_id: int):
    from jose import jwt
    payload = {'sub': str(user_id), 'exp': datetime.utcnow() + timedelta(hours=1)}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token
