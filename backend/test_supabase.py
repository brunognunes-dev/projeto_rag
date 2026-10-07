import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not supabase_url or not supabase_key:
    print("SUPABASE: falha na conexão (variáveis de ambiente ausentes)")
    exit(1)

try:
    client: Client = create_client(supabase_url, supabase_key)
    # Tenta uma operação mínima para validar as credenciais e rede
    res = client.auth.get_session()
    print("SUPABASE: conexão estabelecida com sucesso")
except Exception as e:
    print("SUPABASE: falha na conexão")
