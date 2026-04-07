#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DASHBOARD SERVER - Acompanhar envios de emails em tempo real
- Porta: 3001
- Lê contatos_rastreamento.json (sem chamar Bling)
- API REST para frontend fazer polling a cada 5 minutos
- Zero impacto no rate limit do Bling
"""

from flask import Flask, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)
CONTATOS_FILE = 'contatos_rastreamento.json'

# Mapeamento de situações para categorias
SITUACOES_ENTREGUE = ['entregue']
SITUACOES_EM_ANDAMENTO = ['encaminhado', 'saiu para entrega', 'em trânsito', 'postado']
SITUACOES_PROBLEMA = ['não pode ser efetuada', 'devolvido', 'aguardando retirada']


def classificar_situacao(situacao):
    """Classifica a situação do rastreamento em uma categoria"""
    if not situacao:
        return 'nao_postado', 'Não Postado', '#6c757d'
    s = situacao.lower()
    if any(k in s for k in SITUACOES_ENTREGUE):
        return 'entregue', 'Entregue', '#4CAF50'
    if any(k in s for k in SITUACOES_PROBLEMA):
        return 'problema', 'Problema', '#f44336'
    if any(k in s for k in SITUACOES_EM_ANDAMENTO):
        return 'em_andamento', 'Em Andamento', '#2196F3'
    # Qualquer outra situação preenchida = em andamento
    return 'em_andamento', 'Em Andamento', '#2196F3'


def carregar_contatos():
    """Carrega contatos do JSON local - ZERO chamadas Bling"""
    try:
        with open(CONTATOS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []


def processar_dados():
    """Processa dados dos contatos para o dashboard"""
    contatos = carregar_contatos()

    stats = {
        'total': len(contatos),
        'com_email': 0,
        'sem_email': 0,
        'emails_enviados': 0,
        'emails_vendedor_enviados': 0,
        'entregue': 0,
        'em_andamento': 0,
        'nao_postado': 0,
        'problema': 0,
    }

    # Contador por situação exata
    situacoes_contagem = {}

    pedidos = []

    for c in contatos:
        numero = c.get('numero')
        cliente = c.get('cliente', 'Desconhecido')
        email = c.get('email', '')
        etiqueta = c.get('etiqueta', '')
        ultima_situacao = c.get('ultima_situacao', '')
        emails_enviados = c.get('emails_enviados', [])
        vendedor_email = c.get('vendedor_email', '')
        vendedor_nome = c.get('vendedor_nome', '')
        vendedor_emails_enviados = c.get('emails_vendedor_enviados', [])

        # Contadores email
        if email:
            stats['com_email'] += 1
        else:
            stats['sem_email'] += 1

        stats['emails_enviados'] += len(emails_enviados)
        stats['emails_vendedor_enviados'] += len(vendedor_emails_enviados)

        # Classificar situação do rastreamento
        sit_categoria, sit_label, sit_cor = classificar_situacao(ultima_situacao)
        stats[sit_categoria] = stats.get(sit_categoria, 0) + 1

        # Contar situações exatas
        sit_display = ultima_situacao if ultima_situacao else 'Não Postado'
        situacoes_contagem[sit_display] = situacoes_contagem.get(sit_display, 0) + 1

        # Status de email
        if not email and not vendedor_email:
            email_status = 'SEM_EMAIL'
        elif emails_enviados:
            email_status = 'OK_ESCOLA'
        elif vendedor_emails_enviados:
            email_status = 'OK_VENDEDOR'
        else:
            email_status = 'AGUARDANDO'

        # Último envio
        ultimo_envio = ''
        if emails_enviados:
            ultimo_envio = emails_enviados[-1].get('data', '')
        elif vendedor_emails_enviados:
            ultimo_envio = vendedor_emails_enviados[-1].get('data', '')

        pedidos.append({
            'numero': numero,
            'cliente': cliente,
            'email': email,
            'telefone': c.get('telefone_celular', ''),
            'etiqueta': etiqueta,
            'ultima_situacao': sit_display,
            'sit_categoria': sit_categoria,
            'sit_cor': sit_cor,
            'vendedor_nome': vendedor_nome,
            'vendedor_email': vendedor_email,
            'emails_escola': len(emails_enviados),
            'emails_vendedor': len(vendedor_emails_enviados),
            'email_status': email_status,
            'ultimo_envio': ultimo_envio,
            'emails_enviados': emails_enviados,
            'vendedor_emails_enviados': vendedor_emails_enviados,
        })

    # Ordenar: pedidos mais recentes primeiro
    pedidos.sort(key=lambda x: x['numero'], reverse=True)

    return stats, pedidos, situacoes_contagem


@app.route('/')
def index():
    """Serve o HTML do dashboard"""
    html = r'''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Allcanci - Rastreamento</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <style>
        * { box-sizing: border-box; }
        body {
            background: #f0f2f5;
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
        }
        .top-bar {
            background: linear-gradient(135deg, #0000F3 0%, #0051DB 100%);
            color: white;
            padding: 16px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .top-bar .brand {
            font-size: 1.25rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .top-bar .meta {
            font-size: 0.85rem;
            opacity: 0.9;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .live-dot {
            width: 8px; height: 8px;
            border-radius: 50%;
            background: #4CAF50;
            display: inline-block;
            animation: blink 1.5s infinite;
        }
        @keyframes blink {
            0%,100%{opacity:1;} 50%{opacity:0.3;}
        }
        .main-wrap { padding: 20px 24px; max-width: 1400px; margin: 0 auto; }

        /* ---- STATS CARDS ---- */
        .stats-row { display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; margin-bottom: 20px; }
        @media(max-width:1100px){ .stats-row{grid-template-columns:repeat(3,1fr);} }
        @media(max-width:600px){ .stats-row{grid-template-columns:repeat(2,1fr);} }
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border-left: 4px solid;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .stat-card .num { font-size: 1.8rem; font-weight: 700; line-height: 1; }
        .stat-card .lbl { font-size: 0.78rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-card.clickable { cursor: pointer; transition: transform 0.15s, box-shadow 0.15s; }
        .stat-card.clickable:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.12); }

        /* ---- FILTERS ---- */
        .filters-bar {
            background: white;
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
        }
        .filters-bar .label { font-weight: 600; font-size: 0.9rem; margin-right: 6px; }
        .fbtn {
            border: 1px solid #ddd;
            background: white;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 0.82rem;
            cursor: pointer;
            transition: all 0.15s;
            white-space: nowrap;
        }
        .fbtn:hover { border-color: #0051DB; color: #0051DB; }
        .fbtn.active { background: #0051DB; color: white; border-color: #0051DB; }
        .fbtn .cnt { font-weight: 700; margin-left: 4px; }
        .search-box {
            margin-left: auto;
            padding: 6px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 0.85rem;
            width: 240px;
            outline: none;
        }
        .search-box:focus { border-color: #0051DB; box-shadow: 0 0 0 2px rgba(0,81,219,0.15); }

        /* ---- TABLE ---- */
        .table-wrap {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            overflow: hidden;
        }
        table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
        thead {
            background: linear-gradient(135deg, #0000F3 0%, #0051DB 100%);
            color: white;
            position: sticky;
            top: 56px;
            z-index: 10;
        }
        thead th {
            padding: 12px 14px;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            white-space: nowrap;
        }
        tbody td { padding: 10px 14px; border-bottom: 1px solid #eee; vertical-align: middle; }
        tbody tr { transition: background 0.15s; cursor: pointer; }
        tbody tr:hover { background: #f5f7ff; }

        /* ---- BADGES ---- */
        .sit-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.78rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .sit-entregue { background: #c8e6c9; color: #1b5e20; }
        .sit-em_andamento { background: #bbdefb; color: #0d47a1; }
        .sit-nao_postado { background: #e0e0e0; color: #616161; }
        .sit-problema { background: #ffcdd2; color: #b71c1c; }

        .etiqueta-code {
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.82rem;
            background: #f5f5f5;
            padding: 3px 8px;
            border-radius: 4px;
            color: #333;
            letter-spacing: 0.3px;
        }

        .email-chip {
            display: inline-block;
            background: #e3f2fd;
            color: #0d47a1;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 0.78rem;
            margin: 1px 0;
        }
        .email-chip.vendedor { background: #f3e5f5; color: #6a1b9a; }
        .email-chip.sem { background: #fafafa; color: #999; }

        .email-cnt {
            display: inline-block;
            background: #0051DB;
            color: white;
            padding: 1px 7px;
            border-radius: 10px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-left: 3px;
        }

        .table-footer {
            padding: 12px 18px;
            background: #fafafa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.82rem;
            color: #666;
        }

        /* ---- MODAL ---- */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        .modal-overlay.open { display: flex; }
        .modal-box {
            background: white;
            border-radius: 12px;
            width: 560px;
            max-width: 95vw;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .modal-header {
            background: linear-gradient(135deg, #0000F3 0%, #0051DB 100%);
            color: white;
            padding: 18px 24px;
            border-radius: 12px 12px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .modal-header h3 { margin: 0; font-size: 1.1rem; }
        .modal-close { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; line-height: 1; }
        .modal-body { padding: 20px 24px; }
        .detail-row { display: flex; margin-bottom: 10px; }
        .detail-label { width: 120px; font-weight: 600; color: #555; font-size: 0.85rem; flex-shrink: 0; }
        .detail-value { flex: 1; font-size: 0.88rem; }
        .history-list { list-style: none; padding: 0; margin: 8px 0 0 0; }
        .history-list li {
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 0.82rem;
            display: flex;
            justify-content: space-between;
        }
        .history-list li .sit { font-weight: 600; }
        .history-list li .dt { color: #888; }

        /* ---- PAINEL DE NOTIFICACOES ---- */
        .notif-panel {
            display: none;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .notif-panel.open { display: block; }
        .notif-panel-header {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .notif-panel-header h3 { margin: 0; font-size: 1rem; }
        .notif-panel-close { background: none; border: none; color: white; font-size: 1.3rem; cursor: pointer; }
        .notif-panel-body { padding: 0; max-height: 70vh; overflow-y: auto; }
        .school-card {
            border-bottom: 1px solid #eee;
            padding: 16px 20px;
        }
        .school-card:last-child { border-bottom: none; }
        .school-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        .school-name { font-weight: 700; font-size: 0.95rem; color: #333; }
        .school-pedido { font-size: 0.78rem; color: #888; }
        .school-info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px 20px;
            margin-bottom: 10px;
            font-size: 0.82rem;
        }
        .school-info-grid .inf-label { color: #888; font-size: 0.75rem; text-transform: uppercase; }
        .school-info-grid .inf-value { color: #333; word-break: break-all; }
        .notif-section { margin-top: 8px; }
        .notif-section-title {
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 6px;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
        }
        .notif-section-title.escola { background: #e3f2fd; color: #0d47a1; }
        .notif-section-title.vendedor { background: #f3e5f5; color: #6a1b9a; }
        .notif-section-title.whatsapp { background: #e8f5e9; color: #1b5e20; }
        .notif-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 5px 10px;
            background: #fafafa;
            border-radius: 4px;
            margin-bottom: 4px;
            font-size: 0.8rem;
        }
        .notif-item .n-sit { font-weight: 600; color: #333; }
        .notif-item .n-dt { color: #999; font-size: 0.75rem; }
        .notif-tabs { display: flex; gap: 6px; padding: 12px 20px; background: #fafafa; border-bottom: 1px solid #eee; }
        .ntab {
            padding: 5px 14px;
            border-radius: 16px;
            border: 1px solid #ddd;
            background: white;
            font-size: 0.8rem;
            cursor: pointer;
        }
        .ntab.active { background: #ff9800; color: white; border-color: #ff9800; }
        .ntab:hover { border-color: #ff9800; }
    </style>
</head>
<body>
    <div class="top-bar">
        <div class="brand">
            <i class="bi bi-truck"></i> Dashboard Allcanci - Rastreamento
        </div>
        <div class="meta">
            <span><span class="live-dot"></span> Auto-refresh 5min</span>
            <span id="ultimo-refresh">Carregando...</span>
        </div>
    </div>

    <div class="main-wrap">
        <!-- Stats -->
        <div class="stats-row">
            <div class="stat-card" style="border-color:#0051DB">
                <div class="num" id="stat-total">-</div>
                <div class="lbl">Total Pedidos</div>
            </div>
            <div class="stat-card" style="border-color:#2196F3">
                <div class="num" id="stat-andamento">-</div>
                <div class="lbl">Em Andamento</div>
            </div>
            <div class="stat-card" style="border-color:#4CAF50">
                <div class="num" id="stat-entregues">-</div>
                <div class="lbl">Entregues</div>
            </div>
            <div class="stat-card" style="border-color:#6c757d">
                <div class="num" id="stat-nao-postado">-</div>
                <div class="lbl">N&atilde;o Postado</div>
            </div>
            <div class="stat-card clickable" style="border-color:#ff9800" onclick="abrirPainelNotificacoes()">
                <div class="num" id="stat-emails">-</div>
                <div class="lbl">Emails Enviados <i class="bi bi-box-arrow-up-right" style="font-size:0.65rem"></i></div>
            </div>
            <div class="stat-card" style="border-color:#f44336">
                <div class="num" id="stat-problema">-</div>
                <div class="lbl">Problema</div>
            </div>
        </div>

        <!-- Filters -->
        <div class="filters-bar">
            <span class="label"><i class="bi bi-funnel"></i> Filtros:</span>
            <button class="fbtn active" onclick="filtrar('all', this)">Todos <span class="cnt" id="cnt-all"></span></button>
            <button class="fbtn" onclick="filtrar('em_andamento', this)">Em Andamento <span class="cnt" id="cnt-andamento"></span></button>
            <button class="fbtn" onclick="filtrar('entregue', this)">Entregues <span class="cnt" id="cnt-entregue"></span></button>
            <button class="fbtn" onclick="filtrar('nao_postado', this)">N&atilde;o Postado <span class="cnt" id="cnt-nao-postado"></span></button>
            <button class="fbtn" onclick="filtrar('problema', this)">Problema <span class="cnt" id="cnt-problema"></span></button>
            <button class="fbtn" onclick="filtrar('sem_email', this)">Sem Email <span class="cnt" id="cnt-sem-email"></span></button>
            <input class="search-box" type="text" placeholder="Buscar pedido, cliente, etiqueta..." oninput="buscar(this.value)" id="search-input">
        </div>

        <!-- Painel de Notificações -->
        <div class="notif-panel" id="notif-panel">
            <div class="notif-panel-header">
                <h3><i class="bi bi-envelope-check"></i> Hist&oacute;rico de Notifica&ccedil;&otilde;es por Escola</h3>
                <button class="notif-panel-close" onclick="fecharPainel()">&times;</button>
            </div>
            <div class="notif-tabs">
                <button class="ntab active" onclick="filtrarPainel('todos', this)">Todos</button>
                <button class="ntab" onclick="filtrarPainel('escola', this)">Email Escola</button>
                <button class="ntab" onclick="filtrarPainel('vendedor', this)">Email Vendedor</button>
                <button class="ntab" onclick="filtrarPainel('whatsapp', this)">WhatsApp</button>
            </div>
            <div class="notif-panel-body" id="notif-panel-body"></div>
        </div>

        <!-- Table -->
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Pedido</th>
                        <th>Cliente</th>
                        <th>Etiqueta</th>
                        <th>Situa&ccedil;&atilde;o</th>
                        <th>Email Escola</th>
                        <th>Vendedor</th>
                        <th>Notific.</th>
                    </tr>
                </thead>
                <tbody id="pedidos-tbody">
                    <tr><td colspan="7" style="text-align:center;color:#999;padding:40px;">Carregando...</td></tr>
                </tbody>
            </table>
            <div class="table-footer">
                <span id="table-info">-</span>
                <span id="table-total">-</span>
            </div>
        </div>
    </div>

    <!-- Modal de Detalhes -->
    <div class="modal-overlay" id="modal" onclick="if(event.target===this)fecharModal()">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-title">Detalhes</h3>
                <button class="modal-close" onclick="fecharModal()">&times;</button>
            </div>
            <div class="modal-body" id="modal-body"></div>
        </div>
    </div>

    <script>
        let filtroAtual = 'all';
        let buscaAtual = '';
        let dadosCache = null;

        async function atualizarDados() {
            try {
                const resp = await fetch('/api/contatos');
                const data = await resp.json();
                dadosCache = data;

                const s = data.stats;
                document.getElementById('stat-total').textContent = s.total;
                document.getElementById('stat-andamento').textContent = s.em_andamento || 0;
                document.getElementById('stat-entregues').textContent = s.entregue || 0;
                document.getElementById('stat-nao-postado').textContent = s.nao_postado || 0;
                document.getElementById('stat-emails').textContent = s.emails_enviados + s.emails_vendedor_enviados;
                document.getElementById('stat-problema').textContent = s.problema || 0;

                // Counters nos filtros
                const p = data.pedidos;
                document.getElementById('cnt-all').textContent = p.length;
                document.getElementById('cnt-andamento').textContent = p.filter(x=>x.sit_categoria==='em_andamento').length;
                document.getElementById('cnt-entregue').textContent = p.filter(x=>x.sit_categoria==='entregue').length;
                document.getElementById('cnt-nao-postado').textContent = p.filter(x=>x.sit_categoria==='nao_postado').length;
                document.getElementById('cnt-problema').textContent = p.filter(x=>x.sit_categoria==='problema').length;
                document.getElementById('cnt-sem-email').textContent = p.filter(x=>x.email_status==='SEM_EMAIL').length;

                renderizarTabela(data.pedidos);

                const agora = new Date();
                document.getElementById('ultimo-refresh').textContent =
                    'Atualizado ' + agora.toLocaleTimeString('pt-BR');
            } catch (e) {
                console.error('Erro:', e);
                document.getElementById('ultimo-refresh').textContent = 'Erro: ' + e.message;
            }
        }

        function aplicarFiltros(pedidos) {
            let resultado = pedidos;
            if (filtroAtual !== 'all') {
                if (filtroAtual === 'sem_email') {
                    resultado = resultado.filter(p => p.email_status === 'SEM_EMAIL');
                } else {
                    resultado = resultado.filter(p => p.sit_categoria === filtroAtual);
                }
            }
            if (buscaAtual) {
                const q = buscaAtual.toLowerCase();
                resultado = resultado.filter(p =>
                    String(p.numero).includes(q) ||
                    p.cliente.toLowerCase().includes(q) ||
                    (p.etiqueta||'').toLowerCase().includes(q) ||
                    (p.email||'').toLowerCase().includes(q) ||
                    (p.vendedor_nome||'').toLowerCase().includes(q)
                );
            }
            return resultado;
        }

        function renderizarTabela(pedidos) {
            const tbody = document.getElementById('pedidos-tbody');
            const filtrados = aplicarFiltros(pedidos);

            document.getElementById('table-info').textContent =
                filtrados.length === pedidos.length
                    ? `Mostrando ${filtrados.length} pedidos`
                    : `Mostrando ${filtrados.length} de ${pedidos.length} pedidos`;
            document.getElementById('table-total').textContent =
                `Emails: ${pedidos.reduce((a,p)=>a+p.emails_escola+p.emails_vendedor,0)} enviados`;

            if (!filtrados.length) {
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:#999;padding:40px;">Nenhum pedido encontrado</td></tr>';
                return;
            }

            tbody.innerHTML = filtrados.map(p => {
                const emailHtml = p.email
                    ? `<span class="email-chip">${p.email}</span>`
                    : '<span class="email-chip sem">sem email</span>';
                const vendHtml = p.vendedor_nome
                    ? `<span class="email-chip vendedor">${p.vendedor_nome}</span>`
                    : '<span style="color:#ccc;">-</span>';
                const totalNotif = p.emails_escola + p.emails_vendedor;
                const notifHtml = totalNotif > 0
                    ? `<span class="email-cnt">${totalNotif}</span>`
                    : '<span style="color:#ccc;">0</span>';

                return `
                    <tr onclick="mostrarDetalhes(${p.numero})">
                        <td><strong>#${p.numero}</strong></td>
                        <td>${p.cliente}</td>
                        <td><span class="etiqueta-code">${p.etiqueta || '-'}</span></td>
                        <td><span class="sit-badge sit-${p.sit_categoria}">${p.ultima_situacao}</span></td>
                        <td>${emailHtml}</td>
                        <td>${vendHtml}</td>
                        <td style="text-align:center">${notifHtml}</td>
                    </tr>`;
            }).join('');
        }

        function filtrar(status, el) {
            filtroAtual = status;
            document.querySelectorAll('.fbtn').forEach(b => b.classList.remove('active'));
            if (el) el.classList.add('active');
            if (dadosCache) renderizarTabela(dadosCache.pedidos);
        }

        function buscar(val) {
            buscaAtual = val.trim();
            if (dadosCache) renderizarTabela(dadosCache.pedidos);
        }

        function mostrarDetalhes(numero) {
            if (!dadosCache) return;
            const p = dadosCache.pedidos.find(x => x.numero === numero);
            if (!p) return;

            document.getElementById('modal-title').textContent = `Pedido #${numero}`;

            let html = `
                <div class="detail-row"><div class="detail-label">Cliente</div><div class="detail-value">${p.cliente}</div></div>
                <div class="detail-row"><div class="detail-label">Etiqueta</div><div class="detail-value"><span class="etiqueta-code">${p.etiqueta || '-'}</span></div></div>
                <div class="detail-row"><div class="detail-label">Situa&ccedil;&atilde;o</div><div class="detail-value"><span class="sit-badge sit-${p.sit_categoria}">${p.ultima_situacao}</span></div></div>
                <hr>
                <div class="detail-row"><div class="detail-label">Email Escola</div><div class="detail-value">${p.email || '<span style="color:#999">sem email</span>'}</div></div>
                <div class="detail-row"><div class="detail-label">Notif. Escola</div><div class="detail-value">${p.emails_escola} email(s)</div></div>
            `;
            if (p.emails_enviados.length) {
                html += '<ul class="history-list">';
                p.emails_enviados.forEach(e => {
                    html += `<li><span class="sit">${e.situacao}</span><span class="dt">${e.data}</span></li>`;
                });
                html += '</ul>';
            }
            html += `
                <hr>
                <div class="detail-row"><div class="detail-label">Vendedor</div><div class="detail-value">${p.vendedor_nome || '<span style="color:#999">sem vendedor</span>'}</div></div>
                <div class="detail-row"><div class="detail-label">Email Vend.</div><div class="detail-value">${p.vendedor_email || '<span style="color:#999">sem email</span>'}</div></div>
                <div class="detail-row"><div class="detail-label">Notif. Vend.</div><div class="detail-value">${p.emails_vendedor} email(s)</div></div>
            `;
            if (p.vendedor_emails_enviados.length) {
                html += '<ul class="history-list">';
                p.vendedor_emails_enviados.forEach(e => {
                    html += `<li><span class="sit">${e.situacao}</span><span class="dt">${e.data}</span></li>`;
                });
                html += '</ul>';
            }

            document.getElementById('modal-body').innerHTML = html;
            document.getElementById('modal').classList.add('open');
        }

        function fecharModal() {
            document.getElementById('modal').classList.remove('open');
        }

        // ---- PAINEL DE NOTIFICAÇÕES ----
        let painelFiltro = 'todos';

        function abrirPainelNotificacoes() {
            if (!dadosCache) return;
            renderizarPainel();
            document.getElementById('notif-panel').classList.add('open');
            document.getElementById('notif-panel').scrollIntoView({ behavior: 'smooth' });
        }

        function fecharPainel() {
            document.getElementById('notif-panel').classList.remove('open');
        }

        function filtrarPainel(tipo, el) {
            painelFiltro = tipo;
            document.querySelectorAll('.ntab').forEach(b => b.classList.remove('active'));
            if (el) el.classList.add('active');
            renderizarPainel();
        }

        function renderizarPainel() {
            if (!dadosCache) return;
            const body = document.getElementById('notif-panel-body');

            // Filtrar pedidos que tenham alguma notificação
            const notificados = dadosCache.pedidos.filter(p => {
                if (painelFiltro === 'todos') return p.emails_escola > 0 || p.emails_vendedor > 0 || (p.telefone && p.telefone !== 'N/A');
                if (painelFiltro === 'escola') return p.emails_escola > 0;
                if (painelFiltro === 'vendedor') return p.emails_vendedor > 0;
                if (painelFiltro === 'whatsapp') return p.telefone && p.telefone !== 'N/A';
                return false;
            });

            if (!notificados.length) {
                body.innerHTML = '<div style="padding:40px;text-align:center;color:#999">Nenhuma notifica&ccedil;&atilde;o encontrada para este filtro</div>';
                return;
            }

            body.innerHTML = notificados.map(p => {
                let sections = '';

                // Email Escola
                if ((painelFiltro === 'todos' || painelFiltro === 'escola') && p.emails_enviados.length) {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title escola"><i class="bi bi-envelope"></i> Email Escola &mdash; ' + (p.email || 'sem email') + '</div>';
                    p.emails_enviados.forEach(e => {
                        sections += `<div class="notif-item"><span class="n-sit">${e.situacao}</span><span class="n-dt">${e.data}</span></div>`;
                    });
                    sections += '</div>';
                }

                // Email Vendedor
                if ((painelFiltro === 'todos' || painelFiltro === 'vendedor') && p.vendedor_emails_enviados && p.vendedor_emails_enviados.length) {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title vendedor"><i class="bi bi-person-badge"></i> Email Vendedor &mdash; ' + (p.vendedor_nome || '?') + ' (' + (p.vendedor_email || 'sem email') + ')</div>';
                    p.vendedor_emails_enviados.forEach(e => {
                        sections += `<div class="notif-item"><span class="n-sit">${e.situacao}</span><span class="n-dt">${e.data}</span></div>`;
                    });
                    sections += '</div>';
                }

                // WhatsApp
                if ((painelFiltro === 'todos' || painelFiltro === 'whatsapp') && p.telefone && p.telefone !== 'N/A') {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title whatsapp"><i class="bi bi-whatsapp"></i> WhatsApp &mdash; ' + p.telefone + '</div>';
                    if (!p.emails_enviados.length && !p.vendedor_emails_enviados.length) {
                        sections += '<div class="notif-item"><span class="n-sit" style="color:#999">Dispon&iacute;vel para envio</span><span></span></div>';
                    } else {
                        sections += '<div class="notif-item"><span class="n-sit" style="color:#666">N&uacute;mero cadastrado</span><span></span></div>';
                    }
                    sections += '</div>';
                }

                return `
                    <div class="school-card">
                        <div class="school-header">
                            <div>
                                <div class="school-name">${p.cliente}</div>
                                <div class="school-info-grid">
                                    <div><span class="inf-label">Etiqueta</span><br><span class="etiqueta-code">${p.etiqueta || '-'}</span></div>
                                    <div><span class="inf-label">Situa&ccedil;&atilde;o</span><br><span class="sit-badge sit-${p.sit_categoria}">${p.ultima_situacao}</span></div>
                                </div>
                            </div>
                            <div class="school-pedido">#${p.numero}</div>
                        </div>
                        ${sections}
                    </div>`;
            }).join('');
        }

        document.addEventListener('keydown', e => { if (e.key === 'Escape') { fecharModal(); fecharPainel(); } });

        atualizarDados();
        setInterval(atualizarDados, 300000);
        window.addEventListener('focus', atualizarDados);
    </script>
</body>
</html>
    '''
    return render_template_string(html)


@app.route('/api/contatos')
def api_contatos():
    """API que retorna os dados processados - LEITURA LOCAL APENAS"""
    stats, pedidos, situacoes = processar_dados()
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'pedidos': pedidos,
        'situacoes': situacoes,
    })


if __name__ == '__main__':
    print('\n' + '='*70)
    print('  DASHBOARD ALLCANCI - SERVIDOR INICIADO')
    print('='*70)
    print('\n  Acesse: http://localhost:3001')
    print('  API:    http://localhost:3001/api/contatos')
    print('\n  Atualizando a cada 5 minutos (leitura local, sem impacto Bling)')
    print('  Lendo: contatos_rastreamento.json')
    print('\n' + '='*70 + '\n')

    app.run(debug=False, host='0.0.0.0', port=3001)
