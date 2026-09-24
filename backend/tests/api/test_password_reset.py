import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models.user import User
from app.models.password_reset import PasswordReset
from app.core.security import verify_password, hash_password
from app.core.database import Base
from app.api.deps import get_db
from main import app as original_app
import uuid

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.fixture
def app(db):
    original_app.dependency_overrides[get_db] = lambda: db
    yield original_app
    original_app.dependency_overrides.clear()

@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def setup_test_user(db: AsyncSession):
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=f"testreset_{user_id}@example.com",
        hashed_password=hash_password("oldpassword"),
        full_name="Reset Tester",
        is_active=True
    )
    db.add(user)
    await db.commit()
    return user

@pytest.mark.asyncio
async def test_forgot_password_generic_response(client: AsyncClient, setup_test_user):
    user = setup_test_user
    # Test valid email
    response = await client.post("/api/v1/auth/forgot-password", json={"email": user.email})
    assert response.status_code == 200
    assert "recovery link has been sent" in response.json()["message"]
    
    # Test invalid email (should return same response)
    response_invalid = await client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@example.com"})
    assert response_invalid.status_code == 200
    assert "recovery link has been sent" in response_invalid.json()["message"]

@pytest.mark.asyncio
async def test_token_not_stored_plaintext_and_no_logs(client: AsyncClient, setup_test_user, db: AsyncSession, caplog):
    user = setup_test_user
    
    with caplog.at_level("INFO"):
        response = await client.post("/api/v1/auth/forgot-password", json={"email": user.email})
    
    assert response.status_code == 200
    
    # Check DB
    result = await db.execute(select(PasswordReset).where(PasswordReset.user_id == user.id))
    reset_entry = result.scalar_one()
    
    # Check it's a hash, not the raw token
    assert reset_entry.token_hash.startswith("$2b$") or reset_entry.token_hash.startswith("$2a$")
    assert len(reset_entry.token_hash) >= 60
    
    # Check logs to ensure no raw token or full URL is leaked
    log_text = caplog.text
    assert "PASSWORD RESET LINK" not in log_text
    assert "token=" not in log_text

@pytest.mark.asyncio
async def test_valid_reset_succeeds(client: AsyncClient, setup_test_user, db: AsyncSession):
    user = setup_test_user
    
    # Mock a token
    raw_token = "securetoken123"
    reset_entry = PasswordReset(
        user_id=user.id,
        token_hash=hash_password(raw_token)
    )
    db.add(reset_entry)
    await db.commit()
    await db.refresh(reset_entry)
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": reset_entry.id,
        "token": raw_token,
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 200
    
    # Verify password was updated
    await db.refresh(user)
    assert verify_password("newpassword123", user.hashed_password)
    
    # Verify token is used
    await db.refresh(reset_entry)
    assert reset_entry.is_used is True

@pytest.mark.asyncio
async def test_invalid_token_fails(client: AsyncClient, setup_test_user, db: AsyncSession):
    user = setup_test_user
    
    reset_entry = PasswordReset(
        user_id=user.id,
        token_hash=hash_password("securetoken123")
    )
    db.add(reset_entry)
    await db.commit()
    await db.refresh(reset_entry)
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": reset_entry.id,
        "token": "wrongtoken123",
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 400
    
    # Verify password was NOT updated
    await db.refresh(user)
    assert not verify_password("newpassword123", user.hashed_password)

@pytest.mark.asyncio
async def test_expired_token_fails(client: AsyncClient, setup_test_user, db: AsyncSession):
    user = setup_test_user
    
    reset_entry = PasswordReset(
        user_id=user.id,
        token_hash=hash_password("securetoken123"),
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db.add(reset_entry)
    await db.commit()
    await db.refresh(reset_entry)
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": reset_entry.id,
        "token": "securetoken123",
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_used_token_fails(client: AsyncClient, setup_test_user, db: AsyncSession):
    user = setup_test_user
    
    reset_entry = PasswordReset(
        user_id=user.id,
        token_hash=hash_password("securetoken123"),
        is_used=True
    )
    db.add(reset_entry)
    await db.commit()
    await db.refresh(reset_entry)
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": reset_entry.id,
        "token": "securetoken123",
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_wrong_identifier_valid_token_fails(client: AsyncClient, setup_test_user, db: AsyncSession):
    user = setup_test_user
    
    reset_entry = PasswordReset(
        user_id=user.id,
        token_hash=hash_password("securetoken123")
    )
    db.add(reset_entry)
    await db.commit()
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": str(uuid.uuid4()), # wrong ID
        "token": "securetoken123",
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_no_on_scan(client: AsyncClient, setup_test_user, db: AsyncSession, monkeypatch):
    user = setup_test_user
    
    # Create 5 resets for different users
    for i in range(5):
        db.add(PasswordReset(
            user_id=user.id,
            token_hash=hash_password("token")
        ))
    await db.commit()
    
    # Monkeypatch verify_password to count how many times it's called
    call_count = 0
    import app.services.auth_service
    original_verify = app.services.auth_service.verify_password
    def mock_verify(raw, hashed):
        nonlocal call_count
        call_count += 1
        return original_verify(raw, hashed)
        
    monkeypatch.setattr(app.services.auth_service, "verify_password", mock_verify)
    
    response = await client.post("/api/v1/auth/reset-password", json={
        "reset_id": str(uuid.uuid4()), # Invalid ID
        "token": "some-token",
        "new_password": "newpassword123"
    })
    
    assert response.status_code == 400
    
    # Verify it didn't scan all 5 records (should be 0 because reset_id is invalid)
    assert call_count == 0

