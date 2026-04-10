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
    """Serve o HTML do dashboard com novo design"""
    html = r'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css">
    <link href="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" rel="preload" as="script">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {
            --bg:#0f1117; --surface:#1a1d27; --surface2:#21253a; --border:#2a2f45;
            --text:#e2e8f0; --muted:#64748b; --indigo:#6366f1; --blue:#3b82f6;
            --green:#22c55e; --slate:#94a3b8; --amber:#f59e0b; --red:#ef4444;
        }
        [data-theme="light"] {
            --bg:#f0f2f5; --surface:#ffffff; --surface2:#f1f3f8; --border:#e2e5eb;
            --text:#1e293b; --muted:#64748b; --indigo:#6366f1; --blue:#3b82f6;
            --green:#16a34a; --slate:#94a3b8; --amber:#d97706; --red:#dc2626;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            transition: background .3s, color .3s;
        }
        .topbar { 
            position: sticky; top: 0; z-index: 99;
            background: rgba(15,17,23,.92); backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 14px 28px;
            display: flex; align-items: center; justify-content: space-between;
            gap: 12px;
            transition: background .3s, border-color .3s;
        }
        [data-theme="light"] .topbar { background: rgba(255,255,255,.92); }
        .theme-toggle {
            background: var(--surface2); border: 1px solid var(--border);
            color: var(--text); width: 38px; height: 38px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.15rem; cursor: pointer; transition: all .2s;
            flex-shrink: 0;
        }
        .theme-toggle:hover { border-color: var(--blue); background: var(--surface); transform: scale(1.08); }
        .topbar-brand { display: flex; align-items: center; gap: 10px; }
        .topbar-logo {
            width: 34px; height: 34px; border-radius: 8px;
            background: linear-gradient(135deg, var(--indigo), var(--blue));
            display: flex; align-items: center; justify-content: center;
            font-size: 1.1rem;
        }
        .topbar-brand h1 { font-size: 1.05rem; font-weight: 700; letter-spacing: -.3px; }
        .topbar-brand span { color: var(--muted); font-size: .82rem; margin-left: 4px; }
        .topbar-meta { display: flex; align-items: center; gap: 12px; font-size: .8rem; color: var(--muted); }
        .live-dot { width: 7px; height: 7px; border-radius: 50%; background: #4ade80; animation: pulse 1.8s infinite; }
        @keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(.8)} }
        .wrap { max-width: 1280px; margin: 0 auto; padding: 24px 20px; }
        .section-title { font-size: .7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: var(--muted); margin-bottom: 14px; }
        
        .kpi-grid {
            display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-bottom: 20px;
        }
        @media(max-width:1100px){ .kpi-grid{grid-template-columns:repeat(3,1fr);} }
        @media(max-width:600px){ .kpi-grid{grid-template-columns:repeat(2,1fr);} }
        .kpi-card {
            background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
            padding: 16px; display: flex; flex-direction: column; gap: 6px;
            position: relative; overflow: hidden; transition: transform .2s, box-shadow .2s;
            cursor: pointer;
        }
        .kpi-card:hover { transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,.4); }
        .kpi-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
            background: var(--accent);
        }
        .kpi-icon { font-size: 1.2rem; margin-bottom: 4px; }
        .kpi-num { font-size: 1.8rem; font-weight: 800; color: var(--accent); font-variant-numeric: tabular-nums; }
        .kpi-label { font-size: .72rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }
        .kpi-pct { position: absolute; bottom: 14px; right: 14px; font-size: .72rem; font-weight: 700; color: var(--accent); }
        
        .card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 20px; }
        
        .filters-bar {
            background: var(--surface); border: 1px solid var(--border); border-radius: 10px;
            padding: 14px 16px; margin-bottom: 16px; display: flex; flex-wrap: wrap;
            align-items: center; gap: 8px;
        }
        .filters-bar .label { font-weight: 600; font-size: 0.9rem; margin-right: 6px; }
        .fbtn { border: 1px solid var(--border); background: transparent; color: var(--text); padding: 6px 14px; border-radius: 20px; font-size: .82rem; cursor: pointer; transition: all .15s; }
        .fbtn:hover { border-color: var(--blue); color: var(--blue); }
        .fbtn.active { background: var(--blue); color: white; border-color: var(--blue); }
        .search-box { margin-left: auto; padding: 6px 12px; border: 1px solid var(--border); background: transparent; color: var(--text); border-radius: 20px; font-size: .85rem; outline: none; }
        .search-box:focus { border-color: var(--blue); box-shadow: 0 0 0 2px rgba(59,130,246,.15); }
        .search-box::placeholder { color: var(--muted); }
        
        .table-wrap { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
        table { width: 100%; border-collapse: collapse; font-size: .88rem; }
        thead { background: linear-gradient(135deg, var(--indigo) 0%, var(--blue) 100%); color: white; position: sticky; top: 56px; z-index: 10; }
        [data-theme="light"] .kpi-card:hover { box-shadow: 0 8px 20px rgba(0,0,0,.1); }
        [data-theme="light"] .sit-entregue { background: rgba(22,163,74,.12); color: #15803d; }
        [data-theme="light"] .sit-em_andamento { background: rgba(59,130,246,.12); color: #2563eb; }
        [data-theme="light"] .sit-nao_postado { background: rgba(100,116,139,.12); color: #475569; }
        [data-theme="light"] .sit-problema { background: rgba(220,38,38,.12); color: #dc2626; }
        [data-theme="light"] .etiqueta-code { background: #e8ecf2; }
        [data-theme="light"] .email-chip { background: rgba(59,130,246,.1); color: #2563eb; }
        [data-theme="light"] .email-chip.vendedor { background: rgba(139,92,246,.1); color: #7c3aed; }
        [data-theme="light"] .modal-overlay { background: rgba(0,0,0,.4); }
        [data-theme="light"] tbody tr:hover { background: #f1f5f9; }
        thead th { padding: 12px 14px; font-weight: 600; font-size: .8rem; text-transform: uppercase; }
        tbody td { padding: 10px 14px; border-bottom: 1px solid var(--border); }
        tbody tr { cursor: pointer; transition: background .15s; }
        tbody tr:hover { background: var(--surface2); }
        .sit-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: .78rem; font-weight: 600; }
        .sit-entregue { background: rgba(34,197,94,.2); color: #4ade80; }
        .sit-em_andamento { background: rgba(59,130,246,.2); color: #60a5fa; }
        .sit-nao_postado { background: rgba(148,163,184,.2); color: #cbd5e1; }
        .sit-problema { background: rgba(239,68,68,.2); color: #fca5a5; }
        .etiqueta-code { font-family: monospace; font-size: .8rem; background: var(--surface2); padding: 3px 8px; border-radius: 4px; }
        .email-chip { display: inline-block; background: rgba(59,130,246,.15); color: #60a5fa; padding: 3px 8px; border-radius: 10px; font-size: .78rem; }
        .email-chip.vendedor { background: rgba(139,92,246,.15); color: #c4b5fd; }
        .email-cnt { display: inline-block; background: var(--blue); color: white; padding: 1px 7px; border-radius: 10px; font-size: .72rem; font-weight: 700; }
        .table-footer { padding: 12px 16px; background: var(--surface2); border-top: 1px solid var(--border); font-size: .82rem; color: var(--muted); }
        
        .modal-overlay { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,.7); z-index: 1000; justify-content: center; align-items: center; }
        .modal-overlay.open { display: flex; }
        .modal-box { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; width: 560px; max-width: 95vw; max-height: 85vh; overflow-y: auto; }
        .modal-header { background: linear-gradient(135deg, var(--indigo) 0%, var(--blue) 100%); color: white; padding: 18px 24px; border-radius: 12px 12px 0 0; display: flex; justify-content: space-between; align-items: center; }
        .modal-header h3 { margin: 0; font-size: 1.1rem; }
        .modal-close { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; }
        .modal-body { padding: 20px 24px; }
        .detail-row { display: flex; margin-bottom: 10px; }
        .detail-label { width: 120px; font-weight: 600; color: var(--muted); font-size: .85rem; flex-shrink: 0; }
        .detail-value { flex: 1; font-size: .88rem; }
        .history-list { list-style: none; padding: 0; margin: 8px 0 0 0; }
        .history-list li { padding: 8px 12px; background: var(--surface2); border-radius: 6px; margin-bottom: 6px; font-size: .82rem; display: flex; justify-content: space-between; }
        .history-list li .sit { font-weight: 600; }
        .history-list li .dt { color: var(--muted); }
        
        .notif-panel { display: none; background: var(--surface); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 20px; overflow: hidden; margin-top: 20px; }
        .notif-panel.open { display: block; }
        .notif-panel-header { background: linear-gradient(135deg, var(--amber), #d97706); color: white; padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; }
        .notif-panel-header h3 { margin: 0; font-size: 1rem; }
        .notif-panel-close { background: none; border: none; color: white; font-size: 1.3rem; cursor: pointer; }
        .notif-tabs { display: flex; gap: 6px; padding: 12px 20px; background: var(--surface2); border-bottom: 1px solid var(--border); }
        .ntab { padding: 5px 14px; border-radius: 16px; border: 1px solid var(--border); background: transparent; color: var(--text); font-size: .8rem; cursor: pointer; }
        .ntab:hover { border-color: var(--amber); }
        .ntab.active { background: var(--amber); color: #000; border-color: var(--amber); }
        .notif-panel-body { padding: 0; max-height: 60vh; overflow-y: auto; }
        .school-card { border-bottom: 1px solid var(--border); padding: 14px 16px; }
        .school-card:last-child { border-bottom: none; }
        .school-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }
        .school-name { font-weight: 700; font-size: .95rem; }
        .school-pedido { font-size: .78rem; color: var(--muted); }
        .school-info-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 16px; margin-bottom: 10px; font-size: .82rem; }
        .inf-label { color: var(--muted); font-size: .75rem; text-transform: uppercase; }
        .notif-section { margin-top: 8px; }
        .notif-section-title { font-size: .75rem; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; padding: 4px 8px; border-radius: 4px; display: inline-block; }
        .notif-section-title.escola { background: rgba(59,130,246,.2); color: #60a5fa; }
        .notif-section-title.vendedor { background: rgba(139,92,246,.2); color: #c4b5fd; }
        .notif-item { display: flex; justify-content: space-between; padding: 5px 10px; background: var(--surface2); border-radius: 4px; margin-bottom: 4px; font-size: .8rem; }
        .notif-item .n-sit { font-weight: 600; }
        .notif-item .n-dt { color: var(--muted); font-size: .75rem; }
        
        .footer { border-top: 1px solid var(--border); padding: 16px 28px; display: flex; justify-content: space-between; align-items: center; font-size: .75rem; color: var(--muted); }

        /* Page Navigation Tabs */
        .page-nav { display: flex; gap: 4px; }
        .ptab { padding: 7px 20px; border-radius: 8px; border: 1px solid transparent; background: transparent; color: var(--muted); font-size: .85rem; font-weight: 600; cursor: pointer; transition: all .15s; }
        .ptab:hover { color: var(--text); background: var(--surface2); }
        .ptab.active { background: var(--surface2); color: var(--text); border-color: var(--border); }
        .page { display: none; }
        .page.active { display: block; }
        /* Charts Page */
        .g-charts-grid { display: grid; grid-template-columns: 340px 1fr; gap: 16px; margin-bottom: 20px; }
        @media(max-width:900px){ .g-charts-grid { grid-template-columns: 1fr; } }
        .g-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 20px 22px; }
        .g-card-title { font-size: .82rem; font-weight: 700; color: var(--text); margin-bottom: 16px; display: flex; align-items: center; gap: 7px; }
        .g-card-title .icon { font-size: 1rem; }
        .donut-wrap { position: relative; display: flex; justify-content: center; align-items: center; width: 200px; height: 200px; margin: 0 auto 16px; }
        .donut-center { position: absolute; text-align: center; pointer-events: none; }
        .donut-center .big { font-size: 2.2rem; font-weight: 800; color: var(--text); }
        .donut-center .small { font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }
        .g-legend { display: flex; flex-direction: column; gap: 10px; }
        .g-legend-item { display: flex; align-items: center; justify-content: space-between; }
        .g-legend-left { display: flex; align-items: center; gap: 8px; font-size: .83rem; }
        .g-legend-dot { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
        .g-legend-pct { font-size: .78rem; font-weight: 700; color: var(--text); }
        .g-progress-list { display: flex; flex-direction: column; gap: 14px; }
        .g-progress-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: .82rem; }
        .g-progress-name { font-weight: 600; }
        .g-progress-val { font-size: .78rem; color: var(--muted); }
        .g-progress-bar { width: 100%; height: 8px; background: var(--surface2); border-radius: 4px; overflow: hidden; }
        .g-progress-fill { height: 100%; border-radius: 4px; background: var(--fill-color); transform-origin: left; animation: growBar .9s cubic-bezier(.4,0,.2,1) forwards; }
        @keyframes growBar { from{transform:scaleX(0)} to{transform:scaleX(1)} }
        .gauge-wrap { display: flex; align-items: center; justify-content: center; gap: 24px; flex-wrap: wrap; }
        .gauge-ring-wrap { position: relative; width: 140px; height: 140px; }
        .gauge-ring-wrap svg { transform: rotate(-90deg); }
        .gauge-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
        .gauge-text .big { font-size: 1.6rem; font-weight: 800; }
        .gauge-text .small { font-size: .65rem; color: var(--muted); text-transform: uppercase; letter-spacing: .5px; }
        .gauge-stats { display: flex; flex-direction: column; gap: 10px; }
        .gauge-stat { display: flex; align-items: center; gap: 10px; }
        .gauge-stat .dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
        .gauge-stat .lbl { font-size: .8rem; color: var(--muted); }
        .gauge-stat .val { font-size: .88rem; font-weight: 700; margin-left: auto; padding-left: 20px; }
        .g-feed { display: flex; flex-direction: column; gap: 0; }
        .g-feed-row { display: flex; align-items: center; gap: 10px; padding: 10px 0; border-bottom: 1px solid var(--border); font-size: .82rem; }
        .g-feed-row:last-child { border-bottom: none; }
        .g-feed-icon { font-size: 1rem; flex-shrink: 0; }
        .g-feed-text { flex: 1; color: var(--text); line-height: 1.4; }
        .g-feed-text b { color: var(--text); }
        .g-feed-time { color: var(--muted); font-size: .75rem; white-space: nowrap; }
        .g-bottom-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px; }
        @media(max-width:800px){ .g-bottom-grid { grid-template-columns: 1fr; } }
    </style>
    <script>if(localStorage.getItem('allcanci-theme')==='light')document.documentElement.setAttribute('data-theme','light');</script>
</head>
<body>
    <div class="topbar">
        <div class="topbar-brand">
            <div class="topbar-logo">📦</div>
            <h1>Allcanci <span>Dashboard</span></h1>
        </div>
        <nav class="page-nav">
            <button class="ptab active" onclick="irPara('pedidos', this)">📋 Pedidos</button>
            <button class="ptab" onclick="irPara('graficos', this)">📊 Gráficos</button>
        </nav>
        <button class="theme-toggle" onclick="toggleTheme()" title="Alternar tema claro/escuro" id="theme-btn">🌙</button>
        <div class="topbar-meta">
            <span><i class="bi bi-circle-fill" style="font-size:.5rem;margin-right:4px"></i> Ao Vivo</span>
            <span id="ultimo-refresh">—</span>
        </div>
    </div>

    <div class="wrap">
        <div id="page-pedidos" class="page active">
        <div class="section-title">Visão Geral — Pedidos</div>
        <div class="kpi-grid">
            <div class="kpi-card" style="--accent:var(--indigo)">
                <div class="kpi-icon">📋</div>
                <div class="kpi-num" id="stat-total">—</div>
                <div class="kpi-label">Total Pedidos</div>
            </div>
            <div class="kpi-card" style="--accent:var(--blue)">
                <div class="kpi-icon">🚚</div>
                <div class="kpi-num" id="stat-andamento">—</div>
                <div class="kpi-label">Em Andamento</div>
                <div class="kpi-pct" id="pct-andamento">—%</div>
            </div>
            <div class="kpi-card" style="--accent:var(--green)">
                <div class="kpi-icon">✅</div>
                <div class="kpi-num" id="stat-entregues">—</div>
                <div class="kpi-label">Entregues</div>
                <div class="kpi-pct" id="pct-entregues">—%</div>
            </div>
            <div class="kpi-card" style="--accent:var(--slate)">
                <div class="kpi-icon">📬</div>
                <div class="kpi-num" id="stat-nao-postado">—</div>
                <div class="kpi-label">Não Postado</div>
                <div class="kpi-pct" id="pct-npostado">—%</div>
            </div>
            <div class="kpi-card" style="--accent:var(--amber);cursor:pointer" onclick="abrirPainelNotificacoes()">
                <div class="kpi-icon">📧</div>
                <div class="kpi-num" id="stat-emails">—</div>
                <div class="kpi-label">Emails Enviados</div>
            </div>
            <div class="kpi-card" style="--accent:var(--red)">
                <div class="kpi-icon">⚠️</div>
                <div class="kpi-num" id="stat-problema">—</div>
                <div class="kpi-label">Problema</div>
                <div class="kpi-pct" id="pct-problema">—%</div>
            </div>
        </div>

        <div class="filters-bar">
            <span class="label"><i class="bi bi-funnel"></i> Filtros:</span>
            <button class="fbtn active" onclick="filtrar('all', this)">Todos <span id="cnt-all">0</span></button>
            <button class="fbtn" onclick="filtrar('em_andamento', this)">Em Andamento <span id="cnt-andamento">0</span></button>
            <button class="fbtn" onclick="filtrar('entregue', this)">Entregues <span id="cnt-entregue">0</span></button>
            <button class="fbtn" onclick="filtrar('nao_postado', this)">Não Postado <span id="cnt-nao-postado">0</span></button>
            <button class="fbtn" onclick="filtrar('problema', this)">Problema <span id="cnt-problema">0</span></button>
            <button class="fbtn" onclick="filtrar('sem_email', this)">Sem Email <span id="cnt-sem-email">0</span></button>
            <input class="search-box" type="text" placeholder="Buscar pedido, cliente, etiqueta..." oninput="buscar(this.value)">
        </div>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Pedido</th>
                        <th>Cliente</th>
                        <th>Etiqueta</th>
                        <th>Situação</th>
                        <th>Email Escola</th>
                        <th>Vendedor</th>
                        <th>Notif.</th>
                    </tr>
                </thead>
                <tbody id="pedidos-tbody">
                    <tr><td colspan="7" style="text-align:center;color:var(--muted);padding:40px;">Carregando...</td></tr>
                </tbody>
            </table>
            <div class="table-footer">
                <span id="table-info">—</span>
                <span id="table-total">—</span>
            </div>
        </div>

        <div class="notif-panel" id="notif-panel">
            <div class="notif-panel-header">
                <h3><i class="bi bi-envelope-check"></i> Histórico de Notificações</h3>
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
        </div><!-- /page-pedidos -->

        <div id="page-graficos" class="page">
            <div class="section-title">Dashboard Avançado — Análise Visual</div>

            <!-- Donut + Progress Bars -->
            <div class="g-charts-grid">
                <div class="g-card">
                    <div class="g-card-title"><span class="icon">🍩</span>Distribuição de Status</div>
                    <div class="donut-wrap">
                        <canvas id="donutChart" width="200" height="200"></canvas>
                        <div class="donut-center">
                            <div class="big" id="donut-center-num">—</div>
                            <div class="small">pedidos</div>
                        </div>
                    </div>
                    <div class="g-legend" id="donut-legend"></div>
                </div>
                <div class="g-card">
                    <div class="g-card-title"><span class="icon">📊</span>Proporção por Categoria</div>
                    <div class="g-progress-list" id="g-progress-list"></div>
                </div>
            </div>

            <!-- Gauge: Taxa de Entrega -->
            <div class="g-card" style="margin-bottom:20px">
                <div class="g-card-title"><span class="icon">🎯</span>Taxa de Entrega</div>
                <div class="gauge-wrap">
                    <div class="gauge-ring-wrap">
                        <svg width="140" height="140" viewBox="0 0 140 140">
                            <circle cx="70" cy="70" r="56" fill="none" stroke="var(--surface2)" stroke-width="12"/>
                            <circle id="gauge-circle" cx="70" cy="70" r="56" fill="none" stroke="var(--green)" stroke-width="12" stroke-linecap="round" stroke-dasharray="351.86" stroke-dashoffset="351.86" style="transition:stroke-dashoffset 1.2s cubic-bezier(.4,0,.2,1)"/>
                        </svg>
                        <div class="gauge-text">
                            <div class="big" id="gauge-pct" style="color:var(--green)">—%</div>
                            <div class="small">entrega</div>
                        </div>
                    </div>
                    <div class="gauge-stats" id="gauge-stats"></div>
                </div>
            </div>

            <!-- Bar Chart -->
            <div class="g-bottom-grid">
                <div class="g-card">
                    <div class="g-card-title"><span class="icon">📊</span>Volume por Status</div>
                    <div style="position:relative;height:260px"><canvas id="barChart"></canvas></div>
                </div>
                <div class="g-card">
                    <div class="g-card-title"><span class="icon">📧</span>Emails por Canal</div>
                    <div style="position:relative;height:260px"><canvas id="emailBarChart"></canvas></div>
                </div>
            </div>

            <!-- Activity Feed -->
            <div class="g-card" style="margin-bottom:20px">
                <div class="g-card-title"><span class="icon">⚡</span>Resumo Operacional</div>
                <div class="g-feed" id="g-feed"></div>
            </div>
        </div><!-- /page-graficos -->
    </div><!-- /wrap -->

    <div class="modal-overlay" id="modal" onclick="if(event.target===this)fecharModal()">
        <div class="modal-box">
            <div class="modal-header">
                <h3 id="modal-title">Detalhes</h3>
                <button class="modal-close" onclick="fecharModal()">&times;</button>
            </div>
            <div class="modal-body" id="modal-body"></div>
        </div>
    </div>

    <div class="footer">
        <span>Allcanci © 2026 — Dashboard de Rastreamento</span>
        <span id="footer-ts">—</span>
    </div>

    <script>
        // Theme toggle
        function toggleTheme() {
            const html = document.documentElement;
            const isLight = html.getAttribute('data-theme') === 'light';
            if (isLight) {
                html.removeAttribute('data-theme');
                localStorage.setItem('allcanci-theme','dark');
                document.getElementById('theme-btn').textContent = '\ud83c\udf19';
            } else {
                html.setAttribute('data-theme','light');
                localStorage.setItem('allcanci-theme','light');
                document.getElementById('theme-btn').textContent = '\u2600\ufe0f';
            }
            // Rebuild charts with correct border color
            Object.values(chartInstances).forEach(c => { if(c && c.data) { c.data.datasets.forEach(ds => { if(ds.borderColor === '#1a1d27' || ds.borderColor === '#ffffff') ds.borderColor = getComputedStyle(document.documentElement).getPropertyValue('--surface').trim(); }); c.update(); }});
        }
        // Set icon on load
        document.addEventListener('DOMContentLoaded', () => {
            if (document.documentElement.getAttribute('data-theme') === 'light') document.getElementById('theme-btn').textContent = '\u2600\ufe0f';
        });

        let filtroAtual = 'all';
        let buscaAtual = '';
        let dadosCache = null;
        let painelFiltro = 'todos';

        function pct(num, total) { return total ? ((num / total) * 100).toFixed(1) : '0'; }

        async function atualizarDados() {
            try {
                const resp = await fetch('/api/contatos');
                const data = await resp.json();
                dadosCache = data;

                const s = data.stats;
                const total = s.total;
                
                document.getElementById('stat-total').textContent = s.total;
                document.getElementById('stat-andamento').textContent = s.em_andamento || 0;
                document.getElementById('stat-entregues').textContent = s.entregue || 0;
                document.getElementById('stat-nao-postado').textContent = s.nao_postado || 0;
                document.getElementById('stat-emails').textContent = (s.emails_enviados || 0) + (s.emails_vendedor_enviados || 0);
                document.getElementById('stat-problema').textContent = s.problema || 0;

                document.getElementById('pct-andamento').textContent = pct(s.em_andamento || 0, total) + '%';
                document.getElementById('pct-entregues').textContent = pct(s.entregue || 0, total) + '%';
                document.getElementById('pct-npostado').textContent = pct(s.nao_postado || 0, total) + '%';
                document.getElementById('pct-problema').textContent = pct(s.problema || 0, total) + '%';

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
                    'Atualizado: ' + agora.toLocaleTimeString('pt-BR');
                document.getElementById('footer-ts').textContent =
                    agora.toLocaleString('pt-BR');
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
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:40px;">Nenhum pedido encontrado</td></tr>';
                return;
            }

            tbody.innerHTML = filtrados.map(p => {
                const emailHtml = p.email
                    ? `<span class="email-chip">${p.email}</span>`
                    : '<span style="color:var(--muted);">sem email</span>';
                const vendHtml = p.vendedor_nome
                    ? `<span class="email-chip vendedor">${p.vendedor_nome}</span>`
                    : '<span style="color:var(--muted);">-</span>';
                const totalNotif = p.emails_escola + p.emails_vendedor;
                const notifHtml = totalNotif > 0
                    ? `<span class="email-cnt">${totalNotif}</span>`
                    : '<span style="color:var(--muted);">0</span>';

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
                <div class="detail-row"><div class="detail-label">Situação</div><div class="detail-value"><span class="sit-badge sit-${p.sit_categoria}">${p.ultima_situacao}</span></div></div>
                <hr style="border-color:var(--border)">
                <div class="detail-row"><div class="detail-label">Email Escola</div><div class="detail-value">${p.email || '<span style="color:var(--muted)">sem email</span>'}</div></div>
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
                <hr style="border-color:var(--border)">
                <div class="detail-row"><div class="detail-label">Vendedor</div><div class="detail-value">${p.vendedor_nome || '<span style="color:var(--muted)">sem vendedor</span>'}</div></div>
                <div class="detail-row"><div class="detail-label">Email Vend.</div><div class="detail-value">${p.vendedor_email || '<span style="color:var(--muted)">sem email</span>'}</div></div>
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

            const notificados = dadosCache.pedidos.filter(p => {
                if (painelFiltro === 'todos') return p.emails_escola > 0 || p.emails_vendedor > 0 || (p.telefone && p.telefone !== 'N/A');
                if (painelFiltro === 'escola') return p.emails_escola > 0;
                if (painelFiltro === 'vendedor') return p.emails_vendedor > 0;
                if (painelFiltro === 'whatsapp') return p.telefone && p.telefone !== 'N/A';
                return false;
            });

            if (!notificados.length) {
                body.innerHTML = '<div style="padding:40px;text-align:center;color:var(--muted)">Nenhuma notificação encontrada</div>';
                return;
            }

            body.innerHTML = notificados.map(p => {
                let sections = '';

                if ((painelFiltro === 'todos' || painelFiltro === 'escola') && p.emails_enviados.length) {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title escola"><i class="bi bi-envelope"></i> Email Escola — ' + (p.email || 'sem email') + '</div>';
                    p.emails_enviados.forEach(e => {
                        sections += `<div class="notif-item"><span class="n-sit">${e.situacao}</span><span class="n-dt">${e.data}</span></div>`;
                    });
                    sections += '</div>';
                }

                if ((painelFiltro === 'todos' || painelFiltro === 'vendedor') && p.vendedor_emails_enviados && p.vendedor_emails_enviados.length) {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title vendedor"><i class="bi bi-person-badge"></i> Email Vendedor — ' + (p.vendedor_nome || '?') + '</div>';
                    p.vendedor_emails_enviados.forEach(e => {
                        sections += `<div class="notif-item"><span class="n-sit">${e.situacao}</span><span class="n-dt">${e.data}</span></div>`;
                    });
                    sections += '</div>';
                }

                if ((painelFiltro === 'todos' || painelFiltro === 'whatsapp') && p.telefone && p.telefone !== 'N/A') {
                    sections += '<div class="notif-section">';
                    sections += '<div class="notif-section-title whatsapp"><i class="bi bi-whatsapp"></i> WhatsApp — ' + p.telefone + '</div>';
                    sections += '<div class="notif-item"><span class="n-sit">Número cadastrado</span></div>';
                    sections += '</div>';
                }

                return `
                    <div class="school-card">
                        <div class="school-header">
                            <div>
                                <div class="school-name">${p.cliente}</div>
                                <div class="school-info-grid">
                                    <div><div class="inf-label">Etiqueta</div><span class="etiqueta-code">${p.etiqueta || '-'}</span></div>
                                    <div><div class="inf-label">Situação</div><span class="sit-badge sit-${p.sit_categoria}">${p.ultima_situacao}</span></div>
                                </div>
                            </div>
                            <div class="school-pedido">#${p.numero}</div>
                        </div>
                        ${sections}
                    </div>`;
            }).join('');
        }

        let chartInstances = {};

        function irPara(pagina, el) {
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.getElementById('page-' + pagina).classList.add('active');
            document.querySelectorAll('.ptab').forEach(b => b.classList.remove('active'));
            if (el) el.classList.add('active');
            if (pagina === 'graficos') requestAnimationFrame(() => renderizarGraficos());
        }

        function renderizarGraficos() {
            if (!dadosCache) return;
            const s = dadosCache.stats;
            const total = s.total || 1;
            const items = [
                { key:'andamento', label:'Em Andamento', val:s.em_andamento||0, color:'#3b82f6' },
                { key:'entregues', label:'Entregues',    val:s.entregue||0,     color:'#22c55e' },
                { key:'npostado',  label:'Não Postado',  val:s.nao_postado||0,  color:'#94a3b8' },
                { key:'problema',  label:'Problema',     val:s.problema||0,     color:'#ef4444' },
            ];

            // Donut
            document.getElementById('donut-center-num').textContent = total;
            if (chartInstances['donut']) chartInstances['donut'].destroy();
            chartInstances['donut'] = new Chart(document.getElementById('donutChart'), {
                type: 'doughnut',
                data: {
                    labels: items.map(i=>i.label),
                    datasets: [{ data: items.map(i=>i.val), backgroundColor: items.map(i=>i.color), borderColor:getComputedStyle(document.documentElement).getPropertyValue('--surface').trim(), borderWidth:3, hoverOffset:8 }]
                },
                options: {
                    cutout:'68%', responsive:false, maintainAspectRatio:true,
                    plugins: { legend:{display:false}, tooltip:{ callbacks:{ label: ctx => ' '+ctx.label+': '+ctx.parsed+' ('+pct(ctx.parsed,total)+'%)' } } },
                    animation: { animateRotate:true, duration:1000 }
                }
            });

            // Donut legend
            document.getElementById('donut-legend').innerHTML = items.map(it =>
                '<div class="g-legend-item"><div class="g-legend-left"><div class="g-legend-dot" style="background:'+it.color+'"></div><span>'+it.label+'</span></div><span class="g-legend-pct">'+it.val+' <span style="color:var(--muted);font-weight:400">('+pct(it.val,total)+'%)</span></span></div>'
            ).join('');

            // Progress bars
            document.getElementById('g-progress-list').innerHTML = items.map((it,i) => {
                const p2 = pct(it.val, total);
                return '<div><div class="g-progress-header"><span class="g-progress-name" style="color:'+it.color+'">'+it.label+'</span><span class="g-progress-val">'+it.val+' pedidos — <b>'+p2+'%</b></span></div><div class="g-progress-bar"><div class="g-progress-fill" style="--fill-color:'+it.color+';width:'+p2+'%;animation-delay:'+(i*0.12)+'s"></div></div></div>';
            }).join('');

            // Gauge
            const entregaPct = parseFloat(pct(s.entregue||0, total));
            const circumference = 2 * Math.PI * 56;
            document.getElementById('gauge-circle').style.strokeDashoffset = circumference * (1 - entregaPct/100);
            document.getElementById('gauge-pct').textContent = entregaPct + '%';
            document.getElementById('gauge-stats').innerHTML = [
                {label:'Entregues',val:s.entregue||0,color:'#22c55e'},
                {label:'Em Andamento',val:s.em_andamento||0,color:'#3b82f6'},
                {label:'Problema',val:s.problema||0,color:'#ef4444'},
                {label:'Não Postado',val:s.nao_postado||0,color:'#94a3b8'},
            ].map(it => '<div class="gauge-stat"><div class="dot" style="background:'+it.color+'"></div><span class="lbl">'+it.label+'</span><span class="val">'+it.val+'</span></div>').join('');

            // Bar chart
            if (chartInstances['bar']) chartInstances['bar'].destroy();
            chartInstances['bar'] = new Chart(document.getElementById('barChart'), {
                type:'bar', data:{ labels:items.map(i=>i.label), datasets:[{ label:'Pedidos', data:items.map(i=>i.val), backgroundColor:items.map(i=>i.color+'cc'), borderColor:items.map(i=>i.color), borderWidth:2, borderRadius:6 }] },
                options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ticks:{color:'#64748b',font:{size:11}},grid:{color:'#2a2f45'}}, y:{ticks:{color:'#64748b',font:{size:11}},grid:{color:'#2a2f45'},beginAtZero:true} }, plugins:{legend:{display:false}, tooltip:{callbacks:{label:ctx => ' '+ctx.parsed.y+' pedidos ('+pct(ctx.parsed.y,total)+'%)'}}}, animation:{duration:900} }
            });

            // Email bar chart
            const emailEscola = s.emails_enviados||0;
            const emailVend = s.emails_vendedor_enviados||0;
            if (chartInstances['emailBar']) chartInstances['emailBar'].destroy();
            chartInstances['emailBar'] = new Chart(document.getElementById('emailBarChart'), {
                type:'bar', data:{ labels:['Email Escola','Email Vendedor'], datasets:[{ label:'Emails', data:[emailEscola,emailVend], backgroundColor:['#6366f1cc','#8b5cf6cc'], borderColor:['#6366f1','#8b5cf6'], borderWidth:2, borderRadius:6 }] },
                options:{ responsive:true, maintainAspectRatio:false, scales:{ x:{ticks:{color:'#64748b',font:{size:11}},grid:{color:'#2a2f45'}}, y:{ticks:{color:'#64748b',font:{size:11}},grid:{color:'#2a2f45'},beginAtZero:true} }, plugins:{legend:{display:false}}, animation:{duration:900} }
            });

            // Activity Feed
            const taxaSucesso = pct(s.entregue||0, total);
            const totalEmails = (s.emails_enviados||0) + (s.emails_vendedor_enviados||0);
            document.getElementById('g-feed').innerHTML = [
                {icon:'✅',text:'<b>'+(s.entregue||0)+'</b> pedidos entregues com sucesso — taxa de '+taxaSucesso+'%',time:'agora'},
                {icon:'🚚',text:'<b>'+(s.em_andamento||0)+'</b> pedidos em trânsito aguardando atualização dos Correios',time:'agora'},
                {icon:'📧',text:'<b>'+totalEmails+'</b> notificações de email disparadas para clientes e vendedores',time:'hoje'},
                {icon:'⚠️',text:'<b>'+(s.problema||0)+'</b> pedidos com ocorrência — verificação manual recomendada',time:'pendente'},
                {icon:'📬',text:'<b>'+(s.nao_postado||0)+'</b> pedidos ainda sem código de rastreamento postado',time:'pendente'},
                {icon:'📦',text:'Base total de <b>'+total+'</b> pedidos monitorados no sistema Allcanci',time:'base'},
            ].map(r => '<div class="g-feed-row"><span class="g-feed-icon">'+r.icon+'</span><span class="g-feed-text">'+r.text+'</span><span class="g-feed-time">'+r.time+'</span></div>').join('');
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
