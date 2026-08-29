from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, Chunk
from app.vector_store import VectorStore
import io
import re
import pymupdf


router = APIRouter(prefix="/knowledge-bases/{kb_id}", tags=["documents"])


def clean_extracted_text(text: str) -> str:
    """PDF 提取文本清洗：NUL / 目录行

    - NUL(\\x00)：LaTeX PDF 文本层常见，PG/SQLite 均拒绝入库
    - 目录行：标题 + 点线 + 页码（"2.1.1 Argument Passing . . . ... 5"），
      TOC 页被切进正文会污染检索；宽松判据 = 行内含点线串且行尾是页码
    """
    text = text.replace("\x00", "")

    def is_toc_line(line: str) -> bool:
        # 点线两种形态：点+空格重复（". . . ."）或 6+ 连续点（"......"）；
        # 正文 REPL 的 "..." 只有 3 点且无空格，不会误杀
        return bool(re.search(r"\.\s*\.\s*\.", line)) or bool(re.search(r"\.{6,}", line))

    lines = [l for l in text.split("\n") if not is_toc_line(l)]
    return "\n".join(lines)


async def extract_pdf_text(file: UploadFile):
    raw = await file.read()
    # PyMuPDF 对 LaTeX 生成 PDF 的文本层提取保留词间距，
    # 替代 PyPDF2（其英文词间空格丢失导致"字串粘连"）
    pdf = pymupdf.open(stream=raw, filetype="pdf")
    text = "\n".join(page.get_text() for page in pdf)
    return clean_extracted_text(text)


def chunk_by_char(text: str, chunk_size: int = 300, overlap: int = 30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


@router.post("/upload")
async def upload_document(kb_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    text = await extract_pdf_text(file)
    doc = Document(filename=file.filename, content=text, kb_id=kb_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    chunks = chunk_by_char(text)
    store = VectorStore(f"kb_{kb_id}")
    await store.add_chunks(chunks, doc.id)
    return {"doc_id": doc.id, "chunks": len(chunks)}
