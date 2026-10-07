import re
from typing import List, Dict, Any

def create_chunks(
    text: str, 
    metadata: Dict[str, Any], 
    chunk_size: int = 250, 
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Divide o texto do documento em chunks preservando metadados de rastreabilidade:
    - documento de origem
    - número da nota
    - fornecedor
    - posição/índice do chunk
    - tamanho em caracteres e contagem de palavras
    """
    # Normalização suave mantendo quebras de linhas estruturadas
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    chunk_idx = 0
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 1 <= chunk_size:
            current_chunk = f"{current_chunk}\n{para}".strip()
        else:
            if current_chunk:
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": current_chunk,
                    "char_count": len(current_chunk),
                    "word_count": len(current_chunk.split()),
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_idx
                    }
                })
                chunk_idx += 1
                # Sobreposição com cauda do chunk anterior
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                current_chunk = f"{overlap_text}\n{para}".strip()
            else:
                # Parágrafo maior que chunk_size
                chunks.append({
                    "chunk_index": chunk_idx,
                    "content": para[:chunk_size],
                    "char_count": len(para[:chunk_size]),
                    "word_count": len(para[:chunk_size].split()),
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_idx
                    }
                })
                chunk_idx += 1
                current_chunk = para[chunk_size:]
                
    if current_chunk:
        chunks.append({
            "chunk_index": chunk_idx,
            "content": current_chunk,
            "char_count": len(current_chunk),
            "word_count": len(current_chunk.split()),
            "metadata": {
                **metadata,
                "chunk_index": chunk_idx
            }
        })
        
    return chunks

if __name__ == "__main__":
    sample_text = "Linha 1 da nota.\nLinha 2 com itens.\nLinha 3 com valores e total."
    res = create_chunks(sample_text, {"filename": "teste.pdf", "numero_nota": "123"})
    print(f"Chunks criados: {len(res)}")
    print(res[0])
