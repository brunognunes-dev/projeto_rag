# RAG - Bruno Gabriel Nunes

Sistema didático de **Retrieval-Augmented Generation (RAG)** completo e funcional, com interface web interativa e observabilidade detalhada de cada etapa do pipeline: **OCR ➔ Extração Tabular ➔ Chunking ➔ Tokenização ➔ Embeddings (FastEmbed) ➔ Retrieval Vetorial (top_k=5) ➔ Prompt Aumentado ➔ LLM (OpenRouter)**.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.11+ / FastAPI / Uvicorn
- **Frontend:** HTML5, CSS3 Moderno (Dark Mode & Glassmorphism) e JavaScript Puro
- **Embeddings:** [FastEmbed](https://github.com/qdrant/fastembed) (`BAAI/bge-small-en-v1.5` - 384 dimensões)
- **Banco de Dados & Vetores:** Supabase / PostgreSQL + PGVECTOR
- **LLM:** OpenRouter API (`openrouter/auto`)
- **Processamento de Documentos:** `pypdf`, `reportlab`

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar o ambiente virtual, instalar os pacotes e rodar a aplicação:

### 1. Criar o Ambiente Virtual (`venv`)

No terminal (PowerShell ou Bash), navegue até a raiz do projeto e crie o ambiente virtual:

```bash
# Windows (PowerShell ou Prompt de Comando)
python -m venv venv

# Linux / MacOS
python3 -m venv venv
```

### 2. Ativar o Ambiente Virtual

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Prompt de Comando / CMD)
.\venv\Scripts\activate.bat

# Linux / MacOS
source venv/bin/activate
```

> **Dica (PowerShell):** Caso receba um erro de permissão para executar scripts no PowerShell, execute antes:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 3. Instalar as Dependências do `requirements.txt`

Com o ambiente virtual ativado, instale todos os pacotes necessários:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar as Variáveis de Ambiente (`.env`)

Copie o arquivo de exemplo [.env.example](file:///.env.example) para criar seu `.env`:

```bash
cp .env.example .env
```

Abra o arquivo `.env` e preencha com suas credenciais:

```env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_PUBLISHABLE_KEY=sua_chave_publica_aqui
SUPABASE_SECRET_KEY=sua_chave_secreta_aqui
OPENROUTER_API_KEY=sk-or-v1-sua_chave_openrouter_aqui
```

### 5. Iniciar a Aplicação

Inicie o servidor backend da API:

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Acesse a interface no navegador:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📚 Funcionalidades Didáticas

1. **Aba Consulta / Chat RAG:**
   - Faça perguntas sobre as notas fiscais cadastradas.
   - Painel lateral em tempo real exibindo a **Tokenização**, o vetor de **Embedding (384d)**, os **5 candidatos recuperados com scores**, o **Prompt Aumentado** montado e os metadados da inferência LLM.
   - **Regra Anti-alucinação:** Se a busca vetorial não encontrar candidatos com o limiar de relevância, o sistema responde estritamente: `"Sem dados disponiveis na base"`, sem chamar a LLM para fabricar dados.

2. **Aba Ingestão & Pipeline:**
   - Botão para ingerir automaticamente **4 Notas Fiscais didáticas** de teste (geradas via ReportLab).
   - Suporte para envio de novos PDFs via upload.
   - Demonstração do OCR, extração de metadados, divisão em chunks e tokenização.

---

## 📂 Estrutura de Diretórios

```text
├── backend/
│   ├── main.py                 # API FastAPI e rotas de ingestão/query
│   ├── embedder.py             # Geração de embeddings reais com FastEmbed
│   ├── chunker.py              # Chunking com preservação de metadados
│   ├── tokenizer_service.py    # Tokenização e mapeamento de vocabulário
│   ├── ocr_extractor.py        # Extração de texto e estruturação dos PDFs
│   ├── storage_manager.py      # Persistência e busca vetorial de cosseno
│   ├── llm_service.py          # Prompt aumentado e integração OpenRouter
│   ├── generate_sample_pdfs.py # Gerador dos 4 PDFs fictícios de teste
│   └── test_supabase.py        # Teste seguro de conectividade com Supabase
├── database/
│   └── schema.sql              # Estrutura SQL com extensão PGVECTOR e RPC
├── frontend/
│   ├── index.html              # Interface web moderna com observabilidade
│   ├── style.css               # Estilos com Dark Mode e Glassmorphism
│   └── app.js                  # Lógica de integração e animação das etapas
├── data/
│   └── sample_invoices/        # 4 PDFs de notas fiscais fictícias geradas
├── .env.example                # Modelo de variáveis de ambiente
├── .gitignore                  # Proteção de credenciais, keys e caches
├── requirements.txt            # Dependências do projeto
└── README.md                   # Documentação completa de uso
```
