const API_BASE = "http://localhost:8000/api";

function switchView(viewName) {
  const consultView = document.getElementById("view-consult");
  const ingestView = document.getElementById("view-ingest");
  const consultBtn = document.getElementById("tab-consult-btn");
  const ingestBtn = document.getElementById("tab-ingest-btn");

  if (viewName === "consult") {
    consultView.classList.add("active");
    ingestView.classList.remove("active");
    consultBtn.classList.add("active");
    ingestBtn.classList.remove("active");
  } else {
    ingestView.classList.add("active");
    consultView.classList.remove("active");
    ingestBtn.classList.add("active");
    consultBtn.classList.remove("active");
    loadDocumentsTable();
  }
}

async function loadBases() {
  try {
    const res = await fetch(`${API_BASE}/bases`);
    const data = await res.json();
    const select = document.getElementById("select-base");
    if (data.bases && data.bases.length > 0) {
      select.innerHTML = "";
      data.bases.forEach(b => {
        const opt = document.createElement("option");
        opt.value = b;
        opt.textContent = b;
        select.appendChild(opt);
      });
      const optAll = document.createElement("option");
      optAll.value = "Todas as bases";
      optAll.textContent = "Todas as bases";
      select.appendChild(optAll);
    }
  } catch (err) {
    console.error("Erro ao carregar bases:", err);
  }
}

async function loadDocumentsTable() {
  try {
    const res = await fetch(`${API_BASE}/documents`);
    const data = await res.json();
    const tbody = document.getElementById("documents-table-body");
    
    if (!data.documents || data.documents.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="5" style="padding:16px; text-align:center; color:var(--text-dim);">
            Nenhum documento carregado ainda. Clique em "Ingerir 4 Notas Fiscais de Demonstração" acima.
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = data.documents.map(d => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
        <td style="padding:10px; font-weight:600;">${d.filename}</td>
        <td style="padding:10px; font-family:monospace; color:var(--accent-cyan);">${d.numero_nota || 'N/A'}</td>
        <td style="padding:10px;">${d.fornecedor || 'N/A'}</td>
        <td style="padding:10px; font-family:monospace; font-size:0.75rem;">${d.cnpj || 'N/A'}</td>
        <td style="padding:10px; font-weight:700; color:var(--accent-emerald);">${d.valor_total_formatado || 'R$ ' + d.valor_total}</td>
      </tr>
    `).join('');
  } catch (err) {
    console.error("Erro ao carregar tabela:", err);
  }
}

function updateBaseSelection() {
  const currentBase = document.getElementById("select-base").value;
  console.log("Base selecionada:", currentBase);
}

// Manipulação do Chat de Pergunta RAG
async function handleSendQuestion(e) {
  e.preventDefault();
  const input = document.getElementById("question-input");
  const question = input.value.trim();
  if (!question) return;

  const currentBase = document.getElementById("select-base").value;
  const messagesBox = document.getElementById("chat-messages");

  // Adiciona mensagem do usuário
  const userBubble = document.createElement("div");
  userBubble.className = "message-bubble user";
  userBubble.textContent = question;
  messagesBox.appendChild(userBubble);
  input.value = "";
  messagesBox.scrollTop = messagesBox.scrollHeight;

  // Feedback visual de processamento
  const loadingBubble = document.createElement("div");
  loadingBubble.className = "message-bubble assistant";
  loadingBubble.innerHTML = `<i>Processando pipeline RAG (Tokenização ➔ FastEmbed ➔ Busca Vetorial ➔ LLM)...</i>`;
  messagesBox.appendChild(loadingBubble);
  messagesBox.scrollTop = messagesBox.scrollHeight;

  // Atualiza indicadores de observabilidade
  document.getElementById("badge-query-tokens").textContent = "Processando";
  document.getElementById("badge-query-emb").textContent = "Gerando vetor";

  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: question,
        base_name: currentBase,
        top_k: 5,
        threshold: 0.50
      })
    });

    const data = await res.json();
    messagesBox.removeChild(loadingBubble);

    const replyBubble = document.createElement("div");
    replyBubble.className = "message-bubble assistant";
    if (data.answer === "Sem dados disponiveis na base") {
      replyBubble.className = "message-bubble empty-alert";
      replyBubble.innerHTML = `⚠️ <b>${data.answer}</b><br><small style="font-weight:400; opacity:0.8;">Nenhum documento na base atingiu o limiar de relevância exigido pela busca vetorial.</small>`;
    } else {
      replyBubble.innerHTML = formatMarkdownText(data.answer);
    }
    messagesBox.appendChild(replyBubble);
    messagesBox.scrollTop = messagesBox.scrollHeight;

    // Atualiza Painel Didático
    renderQueryPipeline(data);

  } catch (err) {
    messagesBox.removeChild(loadingBubble);
    const errBubble = document.createElement("div");
    errBubble.className = "message-bubble empty-alert";
    errBubble.textContent = `Erro na requisição: ${err.message}`;
    messagesBox.appendChild(errBubble);
  }
}

function renderQueryPipeline(data) {
  const p = data.pipeline;

  // 1. Tokenização
  document.getElementById("badge-query-tokens").textContent = `${p.tokenization.tokens_count} Tokens`;
  document.getElementById("content-query-tokens").innerHTML = `
    <div>Tokens extraídos da pergunta:</div>
    <div style="margin-top:6px;">
      ${p.tokenization.tokens_list.map(t => `<span class="token-tag">${t}</span>`).join('')}
    </div>
  `;

  // 2. Embedding
  document.getElementById("badge-query-emb").textContent = `${p.dimension} Dimensões`;
  document.getElementById("content-query-emb").innerHTML = `
    <div>Modelo: <b>FastEmbed (bge-small-en-v1.5)</b></div>
    <div style="font-family:monospace; font-size:0.75rem; color:var(--accent-cyan); margin-top:4px;">
      [${p.embedding_preview.map(v => v.toFixed(4)).join(', ')}, ...]
    </div>
  `;

  // 3. Retrieval
  document.getElementById("badge-query-retrieval").textContent = `${p.candidates_count} Candidatos (Top_k=5)`;
  if (p.retrieved_candidates.length === 0) {
    document.getElementById("content-query-retrieval").innerHTML = `
      <div style="color:var(--accent-rose); font-weight:600;">Nenhum candidato relevante recuperado.</div>
    `;
  } else {
    document.getElementById("content-query-retrieval").innerHTML = p.retrieved_candidates.map((c, i) => `
      <div class="candidate-card">
        <div class="candidate-header">
          <span><b>#${i+1}</b> ${c.filename} (NF: ${c.numero_nota || 'N/A'})</span>
          <span class="score-badge">Score: ${c.score}</span>
        </div>
        <div style="font-size:0.78rem; color:var(--text-muted);">${c.content.replace(/\n/g, ' ')}</div>
      </div>
    `).join('');
  }

  // 4. Prompt Aumentado
  if (p.augmented_prompt) {
    document.getElementById("badge-query-prompt").textContent = "Construído";
    document.getElementById("content-query-prompt").innerHTML = `
      <div style="max-height:120px; overflow-y:auto; background:#0b0f19; padding:8px; border-radius:6px; font-family:monospace; font-size:0.72rem; white-space:pre-wrap;">
        ${escapeHtml(p.augmented_prompt)}
      </div>
    `;
  } else {
    document.getElementById("badge-query-prompt").textContent = "Não executado";
    document.getElementById("content-query-prompt").innerHTML = `Não gerado (ausência de dados relevantes).`;
  }

  // 5. LLM
  if (p.llm_called) {
    document.getElementById("badge-query-llm").textContent = p.llm_model;
    document.getElementById("content-query-llm").innerHTML = `
      <div>Chamada realizada com sucesso via OpenRouter API.</div>
      <div style="color:var(--accent-emerald); font-size:0.75rem; margin-top:4px;">Inferência concluída com contexto verificado.</div>
    `;
  } else {
    document.getElementById("badge-query-llm").textContent = "Ignorado";
    document.getElementById("content-query-llm").innerHTML = `
      <div>LLM não acionado para prevenir alucinações.</div>
    `;
  }
}

// Ingestão
async function loadSampleInvoices() {
  const btn = event.target;
  const originalText = btn.innerHTML;
  btn.innerHTML = "⏳ Processando 4 notas...";
  btn.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/load-sample-invoices`, { method: "POST" });
    const data = await res.json();
    alert(`Sucesso! Foram ingeridas ${data.ingested_files.length} Notas Fiscais fictícias na base.`);
    loadDocumentsTable();
    loadBases();
  } catch (err) {
    alert(`Erro ao ingerir: ${err.message}`);
  } finally {
    btn.innerHTML = originalText;
    btn.disabled = false;
  }
}

function onFileSelected(e) {
  const file = e.target.files[0];
  if (file) {
    document.getElementById("file-chosen-label").textContent = `Arquivo selecionado: ${file.name}`;
    document.getElementById("btn-upload-submit").style.display = "block";
  }
}

async function handleUploadPDF(e) {
  e.preventDefault();
  const fileInput = document.getElementById("pdf-file-input");
  const file = fileInput.files[0];
  if (!file) return;

  const currentBase = document.getElementById("select-base").value;
  const formData = new FormData();
  formData.append("file", file);
  formData.append("base_name", currentBase);

  // Status visual na barra de ingestão
  document.getElementById("badge-ingest-ocr").textContent = "Processando";
  document.getElementById("badge-ingest-chunking").textContent = "Aguardando";

  try {
    const res = await fetch(`${API_BASE}/ingest`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();

    if (data.success) {
      // 1. OCR
      document.getElementById("badge-ingest-ocr").textContent = "Concluído";
      document.getElementById("content-ingest-ocr").innerHTML = `
        <b>NF:</b> ${data.step_1_ocr.structured_fields.numero_nota || 'N/A'}<br>
        <b>Fornecedor:</b> ${data.step_1_ocr.structured_fields.fornecedor || 'N/A'}<br>
        <b>CNPJ:</b> ${data.step_1_ocr.structured_fields.cnpj || 'N/A'}<br>
        <b>Valor Total:</b> ${data.step_1_ocr.structured_fields.valor_total_formatado}
      `;

      // 2. Chunks
      document.getElementById("badge-ingest-chunking").textContent = `${data.step_2_chunking.total_chunks} Chunks`;
      document.getElementById("content-ingest-chunking").innerHTML = `
        Documento particionado em ${data.step_2_chunking.total_chunks} chunks preservando metadados fiscais.
      `;

      // 3. Tokenização
      document.getElementById("badge-ingest-tokenization").textContent = "Concluído";
      document.getElementById("content-ingest-tokenization").innerHTML = `
        <b>Amostra de Tokens:</b><br>
        ${data.step_3_tokenization.sample_tokens.slice(0, 10).map(t => `<span class="token-tag">${t}</span>`).join('')}
      `;

      // 4. Embeddings
      document.getElementById("badge-ingest-embedding").textContent = `${data.step_4_embeddings.dimension}d FastEmbed`;
      document.getElementById("content-ingest-embedding").innerHTML = `
        Vetor calculado: [${data.step_4_embeddings.first_chunk_vector_preview.map(v => v.toFixed(4)).join(', ')}...]
      `;

      // 5. Storage
      document.getElementById("badge-ingest-storage").textContent = "Armazenado";
      document.getElementById("content-ingest-storage").innerHTML = `
        Persistido em índice vetorial e registros relacionais.
      `;

      loadDocumentsTable();
      loadBases();
      alert("Documento ingerido e indexado com sucesso no RAG!");
    }
  } catch (err) {
    alert("Erro na ingestão: " + err.message);
  }
}

function formatMarkdownText(text) {
  return text
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
    .replace(/\*(.*?)\*/g, '<i>$1</i>');
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return text.replace(/[&<>"']/g, m => map[m]);
}

// Iniciar ao carregar página
window.addEventListener("DOMContentLoaded", () => {
  loadBases();
  loadDocumentsTable();
});
