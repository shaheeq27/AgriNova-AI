import pytest
import os
from fastapi import UploadFile
from unittest.mock import AsyncMock, patch
from app.services.disease_service import DiseaseService
from app.core.exceptions import AgriNovaException
from io import BytesIO

pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def disease_service(mock_db):
    return DiseaseService(mock_db)

async def create_upload_file(filename: str, content_type: str, content: bytes) -> UploadFile:
    file = UploadFile(filename=filename, file=BytesIO(content))
    file.headers = {"content-type": content_type}
    return file

async def test_jpeg_mime_malicious_php_filename(disease_service):
    file = await create_upload_file("malicious.php", "image/jpeg", b"fake data")
    image = await disease_service.upload_image("crop_1", file)
    assert image.file_path.endswith(".jpg")
    assert ".php" not in image.file_path

async def test_png_mime_malicious_php_filename(disease_service):
    file = await create_upload_file("shell.php", "image/png", b"fake data")
    image = await disease_service.upload_image("crop_1", file)
    assert image.file_path.endswith(".png")
    assert ".php" not in image.file_path

async def test_webp_mime_malicious_exe_filename(disease_service):
    file = await create_upload_file("virus.exe", "image/webp", b"fake data")
    image = await disease_service.upload_image("crop_1", file)
    assert image.file_path.endswith(".webp")
    assert ".exe" not in image.file_path

async def test_unsupported_mime_rejected(disease_service):
    file = await create_upload_file("test.pdf", "application/pdf", b"fake data")
    with pytest.raises(AgriNovaException) as exc:
        await disease_service.upload_image("crop_1", file)
    assert exc.value.status_code == 400
    assert "Invalid file type" in exc.value.message

async def test_valid_upload_works(disease_service):
    file = await create_upload_file("test.jpg", "image/jpeg", b"fake data")
    image = await disease_service.upload_image("crop_1", file)
    assert image.file_path.endswith(".jpg")
    assert image.file_name == "test.jpg"

async def test_generated_filename_does_not_preserve_attacker_extension(disease_service):
    file = await create_upload_file("test.php", "image/jpeg", b"fake data")
    image = await disease_service.upload_image("crop_1", file)
    # The actual saved file path does NOT contain .php
    saved_filename = os.path.basename(image.file_path)
    assert ".php" not in saved_filename
    assert saved_filename.endswith(".jpg")
