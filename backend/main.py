import os
import shutil
import tempfile
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.ocr_extractor import extract_text_from_pdf
from backend.chunker import create_chunks
from backend.tokenizer_service import tokenize_text
from backend.embedder import generate_embeddings, generate_single_embedding
from backend.storage_manager import (
    save_document_and_chunks,
    get_all_bases,
    get_all_documents,
    vector_search,
    reset_database
)
from backend.llm_service import build_augmented_prompt, query_llm

app = FastAPI(title="RAG - Bruno Gabriel Nunes API Didática", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    base_name: Optional[str] = "Notas Fiscais 2026"
    top_k: int = 5
    threshold: float = 0.50

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "RAG - Bruno Gabriel Nunes", "model": "FastEmbed + OpenRouter"}

@app.get("/api/bases")
def list_bases():
    return {"bases": get_all_bases()}

@app.get("/api/documents")
def list_documents(base: Optional[str] = None):
    docs = get_all_documents(base)
    return {"documents": docs, "total": len(docs)}

@app.post("/api/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    base_name: str = Form("Notas Fiscais 2026")
):
    """
    Pipeline de Ingestão Didático passo a passo:
    1. Leitura do PDF
    2. OCR & Extração de texto
    3. Estruturação tabular
    4. Chunking
    5. Tokenização dos chunks
    6. Geração de Embeddings com FastEmbed
    7. Persistência e indexação vetorial
    """
    temp_dir = tempfile.mkdtemp()
    temp_path = os.path.join(temp_dir, file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 1 & 2. Leitura e OCR
        extraction_res = extract_text_from_pdf(temp_path)
        
        # 3. Estruturação
        doc_data = {
            "filename": file.filename,
            "clean_text": extraction_res["clean_text"],
            "structured_fields": extraction_res["structured_fields"],
            "pages_count": extraction_res["pages_count"]
        }
        
        # 4. Chunking
        chunks = create_chunks(
            extraction_res["raw_text"],
            metadata={"filename": file.filename, **extraction_res["structured_fields"]},
            chunk_size=250,
            chunk_overlap=40
        )
        
        # 5. Tokenização didática
        tokenized_chunks = []
        chunk_texts = []
        for c in chunks:
            tok = tokenize_text(c["content"])
            c["tokens_count"] = tok["tokens_count"]
            c["tokens_preview"] = tok["tokens_preview"]
            tokenized_chunks.append({
                "chunk_index": c["chunk_index"],
                "content": c["content"],
                "tokens_count": tok["tokens_count"],
                "tokens_preview": tok["tokens_preview"],
                "token_ids_preview": tok["token_ids_preview"]
            })
            chunk_texts.append(c["content"])
            
        # 6. Geração de Embeddings reais
        embeddings = generate_embeddings(chunk_texts)
        
        # 7. Armazenamento
        save_res = save_document_and_chunks(
            doc_data=doc_data,
            chunks=chunks,
            embeddings=embeddings,
            base_name=base_name
        )
        
        return {
            "success": True,
            "step_1_ocr": {
                "filename": file.filename,
                "pages": extraction_res["pages_count"],
                "raw_text_preview": extraction_res["clean_text"][:300] + "...",
                "structured_fields": extraction_res["structured_fields"]
            },
            "step_2_chunking": {
                "total_chunks": len(chunks),
                "chunks": tokenized_chunks
            },
            "step_3_tokenization": {
                "sample_chunk_index": 0,
                "sample_tokens": tokenized_chunks[0]["tokens_preview"] if tokenized_chunks else [],
                "sample_ids": tokenized_chunks[0]["token_ids_preview"] if tokenized_chunks else []
            },
            "step_4_embeddings": {
                "model": "BAAI/bge-small-en-v1.5 (FastEmbed)",
                "dimension": len(embeddings[0]) if embeddings else 384,
                "first_chunk_vector_preview": embeddings[0][:6] if embeddings else []
            },
            "step_5_storage": {
                "document_id": save_res["document_id"],
                "base_name": base_name,
                "status": "Armazenado com sucesso"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)

@app.post("/api/query")
async def query_rag(req: QueryRequest):
    """
    Pipeline Didático de Consulta RAG:
    1. Pergunta recebida
    2. Tokenização da pergunta
    3. Geração do embedding da pergunta
    4. Retrieval vetorial (top_k=5 com scores)
    5. Regra anti-alucinação ("Sem dados disponiveis na base")
    6. Construção do Prompt Aumentado
    7. Invocação do LLM via OpenRouter
    """
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")
        
    # Etapa A: Tokenização
    question_tokens = tokenize_text(question)
    
    # Etapa B: Embedding da pergunta
    query_vector = generate_single_embedding(question)
    
    # Etapa C: Retrieval vetorial
    candidates = vector_search(
        query_embedding=query_vector,
        base_name=req.base_name,
        top_k=req.top_k,
        threshold=req.threshold
    )
    
    # Etapa D: Regra Obrigatória de Ausência de Dados
    if not candidates:
        return {
            "question": question,
            "pipeline": {
                "tokenization": question_tokens,
                "embedding_preview": query_vector[:6],
                "dimension": len(query_vector),
                "retrieved_candidates": [],
                "candidates_count": 0,
                "augmented_prompt": None,
                "llm_called": False
            },
            "answer": "Sem dados disponiveis na base",
            "has_context": False
        }
        
    # Etapa E: Construção do Prompt Aumentado
    augmented_prompt = build_augmented_prompt(question, candidates)
    
    # Etapa F: LLM OpenRouter
    try:
        llm_result = query_llm(augmented_prompt)
        final_answer = llm_result["response_text"]
        model_name = llm_result["model_used"]
    except Exception as e:
        final_answer = f"Erro ao consultar LLM: {str(e)}"
        model_name = "Erro"
        
    return {
        "question": question,
        "pipeline": {
            "tokenization": question_tokens,
            "embedding_preview": query_vector[:6],
            "dimension": len(query_vector),
            "retrieved_candidates": candidates,
            "candidates_count": len(candidates),
            "augmented_prompt": augmented_prompt,
            "llm_called": True,
            "llm_model": model_name
        },
        "answer": final_answer,
        "has_context": True
    }

@app.post("/api/load-sample-invoices")
async def load_sample_invoices(base_name: str = "Notas Fiscais 2026"):
    """
    Ingesta automaticamente as 4 notas fiscais de teste para agilizar a didática
    """
    samples_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_invoices")
    if not os.path.exists(samples_dir):
        raise HTTPException(status_code=404, detail="Diretório de notas fiscais não encontrado.")
        
    files = [f for f in os.listdir(samples_dir) if f.endswith(".pdf")]
    results = []
    
    for f in sorted(files):
        pdf_path = os.path.join(samples_dir, f)
        ext = extract_text_from_pdf(pdf_path)
        doc_data = {
            "filename": f,
            "clean_text": ext["clean_text"],
            "structured_fields": ext["structured_fields"],
            "pages_count": ext["pages_count"]
        }
        chunks = create_chunks(
            ext["raw_text"],
            metadata={"filename": f, **ext["structured_fields"]},
            chunk_size=250,
            chunk_overlap=40
        )
        chunk_texts = [c["content"] for c in chunks]
        embeddings = generate_embeddings(chunk_texts)
        res = save_document_and_chunks(doc_data, chunks, embeddings, base_name=base_name)
        results.append({
            "filename": f,
            "numero_nota": ext["structured_fields"]["numero_nota"],
            "fornecedor": ext["structured_fields"]["fornecedor"],
            "chunks_count": res["chunks_count"]
        })
        
    return {"success": True, "base_name": base_name, "ingested_files": results}

# Servir Frontend Estático
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
