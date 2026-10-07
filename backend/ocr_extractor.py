import re
import os
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> dict:
    """
    Realiza a leitura do documento PDF e extrai texto das páginas.
    (Emulando etapa OCR/Leitura de documento digital).
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
        
    reader = PdfReader(pdf_path)
    full_text = ""
    pages_text = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        pages_text.append({"page": i + 1, "text": text})
        full_text += text + "\n"
        
    clean_text = re.sub(r'[ \t]+', ' ', full_text).strip()
    
    # Extração de campos estruturados via Regex & Heurísticas
    numero_nota_match = re.search(r'N[^\n\d]*mero:\s*([0-9]+)', full_text, re.IGNORECASE)
    numero_nota = numero_nota_match.group(1) if numero_nota_match else "N/A"
    
    data_match = re.search(r'Emiss[^\n\d]*o:\s*([0-9]{2}/[0-9]{2}/[0-9]{4})', full_text, re.IGNORECASE)
    data_emissao = data_match.group(1) if data_match else "N/A"
    
    fornecedor_match = re.search(r'FORNECEDOR:\s*\n([^\n]+)', full_text, re.IGNORECASE)
    fornecedor = fornecedor_match.group(1).strip() if fornecedor_match else "N/A"
    
    cnpj_match = re.search(r'CNPJ:\s*([0-9]{2}\.[0-9]{3}\.[0-9]{3}/[0-9]{4}-[0-9]{2})', full_text)
    cnpj = cnpj_match.group(1) if cnpj_match else "N/A"
    
    cliente_match = re.search(r'CLIENTE:\s*\n([^\n]+)', full_text, re.IGNORECASE)
    cliente = cliente_match.group(1).strip() if cliente_match else "N/A"
    
    valor_total_match = re.search(r'VALOR TOTAL DA NOTA:\s*\n?\s*(?:R\$\s*)?([0-9\.\,]+)', full_text, re.IGNORECASE)
    valor_total_str = valor_total_match.group(1) if valor_total_match else "0,00"
    try:
        valor_total_num = float(valor_total_str.replace('.', '').replace(',', '.'))
    except Exception:
        valor_total_num = 0.0

    return {
        "raw_text": full_text,
        "clean_text": clean_text,
        "pages_count": len(reader.pages),
        "structured_fields": {
            "numero_nota": numero_nota,
            "data_emissao": data_emissao,
            "fornecedor": fornecedor,
            "cnpj": cnpj,
            "cliente": cliente,
            "valor_total_formatado": f"R$ {valor_total_str}",
            "valor_total": valor_total_num
        }
    }

if __name__ == "__main__":
    sample = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_invoices", "NF_001_TechCorp.pdf")
    res = extract_text_from_pdf(sample)
    print("Extração bem-sucedida:")
    print("Campos:", res["structured_fields"])
