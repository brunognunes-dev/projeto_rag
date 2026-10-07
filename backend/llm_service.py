import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "openrouter/auto"

def build_augmented_prompt(question: str, retrieved_chunks: list) -> str:
    """
    Constrói o prompt aumentado combinando a pergunta, as regras de negócio
    e o contexto real recuperado na busca vetorial.
    """
    context_sections = []
    for i, c in enumerate(retrieved_chunks, 1):
        context_sections.append(
            f"--- [Documento #{i}: {c.get('filename')} | NF: {c.get('numero_nota')} | Fornecedor: {c.get('fornecedor')} | Similaridade: {c.get('score')}] ---\n"
            f"{c.get('content')}\n"
        )
    
    context_str = "\n".join(context_sections)
    
    augmented_prompt = f"""Você é o assistente oficial do sistema RAG - Bruno Gabriel Nunes.
Sua tarefa é responder à pergunta do usuário utilizando ESTRITAMENTE o contexto recuperado dos documentos fiscais abaixo.

REGRAS CRÍTICAS DE SEGURANÇA E FIDELIDADE:
1. Responda apenas com base nas informações contidas nos trechos de contexto fornecidos.
2. Se a informação solicitada não estiver no contexto, responda exatamente: "Sem dados disponiveis na base".
3. Não invente números de notas, nomes de fornecedores, valores ou produtos.
4. Cite o número da nota fiscal e o fornecedor ao responder com dados concretos.
5. Seja didático, objetivo e claro.

CONTEXTO RECUPERADO:
{context_str}

PERGUNTA DO USUÁRIO:
{question}

RESPOSTA DIDÁTICA:"""
    return augmented_prompt

def query_llm(augmented_prompt: str, model: str = DEFAULT_MODEL) -> Dict[str, Any]:
    """
    Realiza a chamada à LLM via OpenRouter.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("Chave OPENROUTER_API_KEY não configurada no ambiente .env")
        
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "RAG - Bruno Gabriel Nunes Educacional"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": augmented_prompt
            }
        ],
        "temperature": 0.1,
        "max_tokens": 800
    }
    
    response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=40)
    
    if response.status_code != 200:
        raise RuntimeError(f"Erro na API do OpenRouter ({response.status_code}): {response.text}")
        
    data = response.json()
    choice = data.get("choices", [{}])[0]
    message_content = choice.get("message", {}).get("content", "")
    
    return {
        "response_text": message_content.strip(),
        "model_used": data.get("model", model),
        "usage": data.get("usage", {}),
        "finish_reason": choice.get("finish_reason")
    }
