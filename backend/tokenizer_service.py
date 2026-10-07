import re
from typing import List, Dict, Any

def tokenize_text(text: str) -> Dict[str, Any]:
    """
    Realiza a tokenização explícita e didática do texto.
    Mostra lista de tokens, contagem e mapeamento de IDs simulados/reais.
    """
    # Tokenização por palavras e pontuações
    tokens = re.findall(r'\w+|[^\w\s]', text, re.UNICODE)
    
    # Amostra de tokens para visualização didática
    preview_tokens = tokens[:25]
    
    return {
        "tokens_count": len(tokens),
        "tokens_list": tokens,
        "tokens_preview": preview_tokens,
        "token_ids_preview": [hash(t) % 10000 for t in preview_tokens],
        "vocab_unique_count": len(set(t.lower() for t in tokens))
    }

if __name__ == "__main__":
    t = tokenize_text("DANFE - Documento Auxiliar da Nota Fiscal 0001045 R$ 28.900,00")
    print("Tokens count:", t["tokens_count"])
    print("Tokens preview:", t["tokens_preview"])
