from unittest.mock import patch,MagicMock
import io
from PyPDF2 import PdfWriter

# 构造 PDF
def make_test_pdf():
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=72, height=72)
    pdf_bytes = io.BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes.read()

# mock 写法

@patch("app.routers.documents.VectorStore")
def test_upload_pdf(mock_vectorstore,client):
    mock_instance = MagicMock()
    mock_vectorstore.return_value = mock_instance
    pdf_bytes = make_test_pdf()
    response = client.post("/knowledge-bases/1/upload",files={"file":("test.pdf",pdf_bytes,"application/pdf")})
    assert response.status_code == 200
    assert "doc_id" in response.json()

def test_upload_non_pdf(client):
    response = client.post("/knowledge-bases/1/upload")
    assert response.status_code == 422


@patch("app.routers.documents.VectorStore")
def test_upload_chunks_count(mock_vectorstore,client):
    mock_instance = MagicMock()
    mock_vectorstore.return_value = mock_instance
    # 测试上传的 PDF 被分成了多少个 chunk
    pdf_bytes = make_test_pdf()
    # 这里假设每个 chunk 的大小是 1KB，PDF 的大小是 1KB，所以应该只有一个 chunk
    response = client.post("/knowledge-bases/1/upload",files={"file":("test.pdf",pdf_bytes,"application/pdf")})
    assert response.status_code == 200
    # 检查 add_chunks 方法是否被调用了一次
    mock_instance.add_chunks.assert_called_once()