from unittest.mock import Mock, AsyncMock
from src.entity.models import User
from src.services.auth import auth_service
from conftest import disable_ratelimit
from sqlalchemy.ext.asyncio import AsyncSession
from conftest import test_user
import pytest
from tests.conftest import TestingSessionLocal
from sqlalchemy import select

user_data = {"username": "agent007", "email": "agent007@gmail.com", "password": "12345678"}
refresh_user_data = {"username": "refresh_user", "email": "refresh@example.com", "password": "refreshpassword"}
confirm_user_data = {"username": "confirm_user", "email": "confirm@example.com", "password": "confirmpassword"}
request_user_data = {"username": "request_user", "email": "request@example.com", "password": "requestpassword"}

disable_ratelimit()


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


@pytest.mark.asyncio
async def test_repeat_signup(client, db_session: AsyncSession, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    response = client.post("api/auth/signup", json=test_user)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "Account already exists"
    assert not mock_send_email.called


@pytest.mark.asyncio
async def test_not_confirmed_login(client):
    response = client.post("api/auth/login?r=1",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert response.json()["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login?r=1",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


@pytest.mark.asyncio
async def test_wrong_password_login(client):
    response = client.post("api/auth/login?r=1",
                           data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


@pytest.mark.asyncio
async def test_wrong_email_login(client):
    response = client.post("api/auth/login?r=1",
                           data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_refresh_token_essential(client, db_session: AsyncSession, monkeypatch):
    password_hash = auth_service.get_password_hash(refresh_user_data["password"])
    user = User(
        username=refresh_user_data["username"],
        email=refresh_user_data["email"],
        password=password_hash,
        confirmed=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    test_refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    user.refresh_token = test_refresh_token
    await db_session.commit()
    await db_session.refresh(user)

    monkeypatch.setattr("src.routes.auth.auth_service.decode_refresh_token", AsyncMock(return_value=user.email))

    response = client.get(
        "/api/auth/refresh_token?r=1",
        headers={"Authorization": f"Bearer {test_refresh_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    await db_session.refresh(user)
    assert user.refresh_token is not None


@pytest.mark.asyncio
async def test_confirmed_email_essential(client, db_session: AsyncSession, monkeypatch):
    password_hash = auth_service.get_password_hash(confirm_user_data["password"])
    user = User(
        username=confirm_user_data["username"],
        email=confirm_user_data["email"],
        password=password_hash,
        confirmed=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    monkeypatch.setattr("src.routes.auth.auth_service.get_email_from_token", AsyncMock(return_value=user.email))

    response = client.get(f"/api/auth/confirmed_email/some_valid_token")
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Email confirmed"
    await db_session.refresh(user)
    assert user.confirmed is True

@pytest.mark.asyncio
async def test_request_email_essential(client, db_session: AsyncSession, monkeypatch):
    mock_send_email = Mock()

    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    password_hash = auth_service.get_password_hash(request_user_data["password"])

    user = User(
        username=request_user_data["username"],
        email=request_user_data["email"],
        password=password_hash,
        confirmed=False
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    response = client.post("/api/auth/request_email", json={"email": user.email})
    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Check your email for confirmation."

    assert mock_send_email.called
