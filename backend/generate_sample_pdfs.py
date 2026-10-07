import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sample_invoices")
os.makedirs(DOCS_DIR, exist_ok=True)

invoices_data = [
    {
        "filename": "NF_001_TechCorp.pdf",
        "numero_nota": "0001045",
        "data_emissao": "12/03/2026",
        "fornecedor": "TechCorp Suprimentos de TI Ltda",
        "cnpj": "12.345.678/0001-90",
        "cliente": "Escola de Tecnologia AprendaMais",
        "cliente_cnpj": "98.765.432/0001-10",
        "produtos": [
            {"item": "1", "desc": "Notebook Dell Inspiron 15 i7 16GB", "qtd": "5", "unit": "R$ 4.200,00", "total": "R$ 21.000,00"},
            {"item": "2", "desc": "Mouse Sem Fio Logitech Master 3S", "qtd": "10", "unit": "R$ 450,00", "total": "R$ 4.500,00"},
            {"item": "3", "desc": "Teclado Mecânico Keychron K2", "qtd": "5", "unit": "R$ 680,00", "total": "R$ 3.400,00"}
        ],
        "valor_total": "R$ 28.900,00",
        "valor_total_num": 28900.00,
        "obs": "Pagamento em 30 dias via boleto bancario. Garantia de hardware: 12 meses direto com fabricante."
    },
    {
        "filename": "NF_002_OfficePaper.pdf",
        "numero_nota": "0002190",
        "data_emissao": "18/03/2026",
        "fornecedor": "Papelaria & Escritorio OfficePaper Ltda",
        "cnpj": "23.456.789/0001-01",
        "cliente": "Escola de Tecnologia AprendaMais",
        "cliente_cnpj": "98.765.432/0001-10",
        "produtos": [
            {"item": "1", "desc": "Papel Sulfite A4 Chamex 75g (Caixa 10 pct)", "qtd": "8", "unit": "R$ 240,00", "total": "R$ 1.920,00"},
            {"item": "2", "desc": "Quadro Branco Magnetico 120x90cm", "qtd": "2", "unit": "R$ 310,00", "total": "R$ 620,00"},
            {"item": "3", "desc": "Caneta Marcador Recarregavel Pilot Kit", "qtd": "15", "unit": "R$ 38,00", "total": "R$ 570,00"}
        ],
        "valor_total": "R$ 3.110,00",
        "valor_total_num": 3110.00,
        "obs": "Entrega realizada no campus principal. Faturamento liquido para 15 dias."
    },
    {
        "filename": "NF_003_MoveisConfort.pdf",
        "numero_nota": "0003501",
        "data_emissao": "22/03/2026",
        "fornecedor": "Moveis Confort & Ergonomia S.A.",
        "cnpj": "34.567.890/0001-12",
        "cliente": "Escola de Tecnologia AprendaMais",
        "cliente_cnpj": "98.765.432/0001-10",
        "produtos": [
            {"item": "1", "desc": "Cadeira Ergonomica Cavaletti C3 NR17", "qtd": "12", "unit": "R$ 1.150,00", "total": "R$ 13.800,00"},
            {"item": "2", "desc": "Mesa Plataforma 4 Lugares com Calha de Rede", "qtd": "3", "unit": "R$ 2.400,00", "total": "R$ 7.200,00"}
        ],
        "valor_total": "R$ 21.000,00",
        "valor_total_num": 21000.00,
        "obs": "Montagem inclusa no local. Certificado NR17 de ergonomia emitido e anexo."
    },
    {
        "filename": "NF_004_NetServer.pdf",
        "numero_nota": "0004812",
        "data_emissao": "29/03/2026",
        "fornecedor": "NetServer Infraestrutura e Conectividade Ltda",
        "cnpj": "45.678.901/0001-23",
        "cliente": "Escola de Tecnologia AprendaMais",
        "cliente_cnpj": "98.765.432/0001-10",
        "produtos": [
            {"item": "1", "desc": "Switch Gerenciavel Cisco Catalyst 24P Gigabit", "qtd": "2", "unit": "R$ 3.850,00", "total": "R$ 7.700,00"},
            {"item": "2", "desc": "Access Point Wi-Fi 6 Ubiquiti UniFi Pro", "qtd": "4", "unit": "R$ 1.250,00", "total": "R$ 5.000,00"},
            {"item": "3", "desc": "Patch Cord Furukawa Cat6 2.5m (Pacote c/ 20)", "qtd": "2", "unit": "R$ 220,00", "total": "R$ 440,00"}
        ],
        "valor_total": "R$ 13.140,00",
        "valor_total_num": 13140.00,
        "obs": "Instalacao de cabeamento estruturado e homologacao da rede do laboratorio de IA."
    }
]

def generate_pdf(doc_data):
    filepath = os.path.join(DOCS_DIR, doc_data["filename"])
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1e293b"),
        alignment=1 # Center
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        alignment=1
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155")
    )
    
    bold_style = ParagraphStyle(
        'BoldStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a")
    )
    
    elements = []
    
    elements.append(Paragraph("DANFE - DOCUMENTO AUXILIAR DA NOTA FISCAL ELETRÔNICA", title_style))
    elements.append(Paragraph(f"Número: <b>{doc_data['numero_nota']}</b> | Série: 1 | Emissão: <b>{doc_data['data_emissao']}</b>", subtitle_style))
    elements.append(Spacer(1, 14))
    
    # Cabeçalho Fornecedor e Destinatário
    header_data = [
        [
            Paragraph(f"<b>EMITENTE / FORNECEDOR:</b><br/>{doc_data['fornecedor']}<br/>CNPJ: {doc_data['cnpj']}<br/>Inscrição Estadual: 109.283.475.110", normal_style),
            Paragraph(f"<b>DESTINATÁRIO / CLIENTE:</b><br/>{doc_data['cliente']}<br/>CNPJ: {doc_data['cliente_cnpj']}<br/>Endereço: Av. Paulista, 1000 - São Paulo/SP", normal_style)
        ]
    ]
    t_header = Table(header_data, colWidths=[270, 270])
    t_header.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 14))
    
    # Tabela de Itens
    items_table_data = [
        [
            Paragraph("<b>Item</b>", bold_style),
            Paragraph("<b>Descrição do Produto / Serviço</b>", bold_style),
            Paragraph("<b>Qtd</b>", bold_style),
            Paragraph("<b>Valor Unitário</b>", bold_style),
            Paragraph("<b>Valor Total</b>", bold_style)
        ]
    ]
    for p in doc_data["produtos"]:
        items_table_data.append([
            Paragraph(p["item"], normal_style),
            Paragraph(p["desc"], normal_style),
            Paragraph(p["qtd"], normal_style),
            Paragraph(p["unit"], normal_style),
            Paragraph(p["total"], normal_style)
        ])
    
    t_items = Table(items_table_data, colWidths=[35, 265, 50, 90, 100])
    t_items.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_items)
    elements.append(Spacer(1, 12))
    
    # Rodapé com Totais e Informações Adicionais
    total_data = [
        [Paragraph(f"<b>INFORMAÇÕES COMPLEMENTARES:</b><br/>{doc_data['obs']}", normal_style),
         Paragraph(f"<para align='right'><b>VALOR TOTAL DA NOTA:</b><br/><font size='14' color='#0284c7'><b>{doc_data['valor_total']}</b></font></para>", normal_style)]
    ]
    t_total = Table(total_data, colWidths=[360, 180])
    t_total.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_total)
    
    doc.build(elements)
    print(f"Gerado: {filepath}")

if __name__ == "__main__":
    for item in invoices_data:
        generate_pdf(item)
    print("Sucesso: 4 PDFs fictícios de notas fiscais gerados.")
