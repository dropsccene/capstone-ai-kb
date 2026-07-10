from fastapi import APIRouter, UploadFile, File,Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document,Chunk
from app.vector_store import VectorStore
from PyPDF2 import PdfReader
import io


router = APIRouter(prefix = "/knowledge-bases/{kb_id}", tags = ["documents"])

async def extract_pdf_text(file:UploadFile):
    raw = await file.read()
    pdf = PdfReader(io.BytesIO(raw))
    text = "\n".join(p.extract_text()for p in pdf.pages if p.extract_text())
    return text

def chunk_by_char(text:str,chunk_size:int=300,overlap:int=30):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


@router.post("/upload")
async def upload_document(kb_id:int,file:UploadFile= File(...),db:Session = Depends(get_db)):
    text = await extract_pdf_text(file)
    doc = Document(filename = file.filename,content = text,kb_id = kb_id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    chunks = chunk_by_char(text)
    store = VectorStore(f"kb_{kb_id}")
    store.add_chunks(chunks, doc.id)
    return {"doc_id":doc.id,"chunks":len(chunks)}