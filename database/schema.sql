-- Ativa extensão pgvector
create extension if not exists vector;

-- Tabela de documentos / bases
create table if not exists documents (
    id uuid default gen_random_uuid() primary key,
    base_name text not null default 'default',
    filename text not null,
    doc_type text default 'nota_fiscal',
    numero_nota text,
    data_emissao text,
    fornecedor text,
    cnpj text,
    cliente text,
    produtos text,
    quantidade text,
    valor_unitario text,
    valor_total numeric,
    texto_extraido text,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Tabela de chunks com embeddings
create table if not exists document_chunks (
    id uuid default gen_random_uuid() primary key,
    document_id uuid references documents(id) on delete cascade,
    base_name text not null default 'default',
    numero_nota text,
    fornecedor text,
    chunk_index integer not null,
    content text not null,
    tokens_count integer,
    tokens_preview text,
    embedding vector(384),
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Índice vetorial ivfflat ou hnsw
create index if not exists document_chunks_embedding_idx 
on document_chunks 
using hnsw (embedding vector_cosine_ops);

-- Função RPC para busca vetorial com filtro por base
create or replace function match_document_chunks (
  query_embedding vector(384),
  match_threshold float default 0.1,
  match_count int default 5,
  filter_base text default null
)
returns table (
  id uuid,
  document_id uuid,
  base_name text,
  numero_nota text,
  fornecedor text,
  chunk_index int,
  content text,
  tokens_count int,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    document_chunks.id,
    document_chunks.document_id,
    document_chunks.base_name,
    document_chunks.numero_nota,
    document_chunks.fornecedor,
    document_chunks.chunk_index,
    document_chunks.content,
    document_chunks.tokens_count,
    1 - (document_chunks.embedding <=> query_embedding) as similarity
  from document_chunks
  where 
    (filter_base is null or filter_base = '' or document_chunks.base_name = filter_base)
    and (1 - (document_chunks.embedding <=> query_embedding)) >= match_threshold
  order by document_chunks.embedding <=> query_embedding
  limit match_count;
end;
$$;
