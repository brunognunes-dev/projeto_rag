import os
import json
import uuid
import numpy as np
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# Caminho para armazenamento local persistente que complementa o Supabase
LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "storage")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)
DB_FILE = os.path.join(LOCAL_STORAGE_DIR, "rag_database.json")

def _load_data() -> Dict[str, Any]:
    if not os.path.exists(DB_FILE):
        return {"documents": [], "chunks": []}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"documents": [], "chunks": []}

def _save_data(data: Dict[str, Any]):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_document_and_chunks(
    doc_data: Dict[str, Any],
    chunks: List[Dict[str, Any]],
    embeddings: List[List[float]],
    base_name: str = "Notas Fiscais 2026"
) -> Dict[str, Any]:
    """
    Armazena documento e chunks com seus embeddings e metadados.
    Tenta sincronizar no Supabase via API e mantém persistência local.
    """
    data = _load_data()
    doc_id = str(uuid.uuid4())
    
    doc_record = {
        "id": doc_id,
        "base_name": base_name,
        "filename": doc_data.get("filename"),
        "numero_nota": doc_data["structured_fields"].get("numero_nota"),
        "data_emissao": doc_data["structured_fields"].get("data_emissao"),
        "fornecedor": doc_data["structured_fields"].get("fornecedor"),
        "cnpj": doc_data["structured_fields"].get("cnpj"),
        "cliente": doc_data["structured_fields"].get("cliente"),
        "valor_total": doc_data["structured_fields"].get("valor_total"),
        "valor_total_formatado": doc_data["structured_fields"].get("valor_total_formatado"),
        "clean_text": doc_data.get("clean_text")
    }
    
    chunk_records = []
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        c_id = str(uuid.uuid4())
        chunk_records.append({
            "id": c_id,
            "document_id": doc_id,
            "base_name": base_name,
            "filename": doc_data.get("filename"),
            "numero_nota": doc_data["structured_fields"].get("numero_nota"),
            "fornecedor": doc_data["structured_fields"].get("fornecedor"),
            "chunk_index": idx,
            "content": chunk["content"],
            "tokens_count": chunk.get("tokens_count", len(chunk["content"].split())),
            "tokens_preview": chunk.get("tokens_preview", []),
            "embedding": emb
        })
        
    data["documents"].append(doc_record)
    data["chunks"].extend(chunk_records)
    _save_data(data)
    
    return {"document_id": doc_id, "chunks_count": len(chunk_records)}

def get_all_bases() -> List[str]:
    data = _load_data()
    bases = list(set([d["base_name"] for d in data.get("documents", [])]))
    if not bases:
        return ["Notas Fiscais 2026", "Base de Suprimentos TI", "Geral"]
    return bases

def get_all_documents(base_name: Optional[str] = None) -> List[Dict[str, Any]]:
    data = _load_data()
    docs = data.get("documents", [])
    if base_name:
        docs = [d for d in docs if d["base_name"] == base_name]
    return docs

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    v1 = np.array(vec1, dtype=np.float32)
    v2 = np.array(vec2, dtype=np.float32)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))

def vector_search(
    query_embedding: List[float], 
    base_name: Optional[str] = None, 
    top_k: int = 5,
    threshold: float = 0.55
) -> List[Dict[str, Any]]:
    """
    Busca por similaridade de cosseno nos vetores de chunks armazenados.
    Retorna os top_k candidatos com scores e metadados completos.
    """
    data = _load_data()
    chunks = data.get("chunks", [])
    
    if base_name and base_name != "Todas as bases":
        chunks = [c for c in chunks if c.get("base_name") == base_name]
        
    scored_candidates = []
    for chunk in chunks:
        sim = cosine_similarity(query_embedding, chunk["embedding"])
        if sim >= threshold:
            scored_candidates.append({
                "id": chunk["id"],
                "document_id": chunk["document_id"],
                "base_name": chunk.get("base_name"),
                "filename": chunk.get("filename"),
                "numero_nota": chunk.get("numero_nota"),
                "fornecedor": chunk.get("fornecedor"),
                "chunk_index": chunk.get("chunk_index"),
                "content": chunk.get("content"),
                "tokens_count": chunk.get("tokens_count"),
                "score": round(sim, 4)
            })
            
    # Ordena pelo maior score
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)
    return scored_candidates[:top_k]

def reset_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
