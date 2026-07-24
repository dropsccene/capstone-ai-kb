from unittest.mock import patch, MagicMock, AsyncMock
import io
from PyPDF2 import PdfWriter


def make_test_pdf():
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.read()


@patch("app.routers.documents.VectorStore")
def test_upload_pdf(mock_vectorstore, client):
    mock_instance = MagicMock()
    mock_instance.add_chunks = AsyncMock()
    mock_vectorstore.return_value = mock_instance
    pdf_bytes = make_test_pdf()
    response = client.post("/knowledge-bases/1/upload", files={"file": ("test.pdf", pdf_bytes, "application/pdf")})
    assert response.status_code == 200
    assert "doc_id" in response.json()


def test_upload_non_pdf(client):
    response = client.post("/knowledge-bases/1/upload")
    assert response.status_code == 422


@patch("app.routers.documents.VectorStore")
def test_upload_chunks_count(mock_vectorstore, client):
    mock_instance = MagicMock()
    mock_instance.add_chunks = AsyncMock()
    mock_vectorstore.return_value = mock_instance
    pdf_bytes = make_test_pdf()
    response = client.post("/knowledge-bases/1/upload", files={"file": ("test.pdf", pdf_bytes, "application/pdf")})
    assert response.status_code == 200
    mock_instance.add_chunks.assert_called_once()
