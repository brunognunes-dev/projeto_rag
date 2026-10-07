from typing import List
from fastembed import TextEmbedding

# Instância compartilhada do FastEmbed
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = TextEmbedding()
    return _embedding_model

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Gera embeddings reais usando FastEmbed (BAAI/bge-small-en-v1.5).
    Retorna lista de vetores float32 de 384 dimensões.
    """
    model = get_embedding_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]

def generate_single_embedding(text: str) -> List[float]:
    return generate_embeddings([text])[0]

if __name__ == "__main__":
    embs = generate_embeddings(["Nota fiscal de compra de notebooks Dell"])
    print("Embedding gerado com sucesso!")
    print("Dimensão:", len(embs[0]))
    print("Primeiros 5 valores:", embs[0][:5])
