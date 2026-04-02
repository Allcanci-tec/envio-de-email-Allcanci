#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║              GUIA DE CONFIGURAÇÃO - INTEGRAÇÃO RASTREAMENTO              ║
║                                                                          ║
║  Este guia explicará como integrar rastreamento com WhatsApp             ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

# ======================================================================
# 📦 COMPONENTES CRIADOS
# ======================================================================
"""
1. rastreio_service.py
   - Consulta API Wonca (SiteRastreio)
   - Retorna evento mais recente
   - Trata erros e timeouts
   
2. rastreamento_cache.py
   - Cache local com expiração de 4 horas
   - Evita gasto desnecessário de créditos
   - Limite inteligente por etiqueta
   
3. notificador_rastreamento.py
   - Integra rastreio_service + cache + whatsapp_service
   - Detecta mudanças de status automaticamente
   - Formata mensagens amigáveis
   
4. config_rastreamentos.json
   - Lista de rastreamentos a monitorar
   - Mapeia etiqueta → número do cliente
   
5. .gitignore (atualizado)
   - Protege .env e whatsapp_session
   - Evita vazar credenciais
   - Compatível com repositório público
"""

# ======================================================================
# ⚙️ SETUP INICIAL
# ======================================================================
"""
PASSO 1: Verificar .env
───────────────────────
O arquivo .env precisa ter:

    WONCA_API_KEY=seu_token_aqui
    WONCA_API_URL=https://api-labs.wonca.com.br
    WONCA_SERVICE_PATH=wonca.labs.v1.LabsService/Track

Nota: Já está configurado! Execute para testar:

    python -c "from rastreio_service import RastreioService; print('✅ API configurada')"


PASSO 2: Configurar rastreamentos (config_rastreamentos.json)
──────────────────────────────────────────────────────────────
Edite o arquivo com seus rastreamentos:

{
  "rastreamentos": [
    {
      "etiqueta": "AA123456789BR",
      "numero_cliente": "31984163357"
    },
    {
      "etiqueta": "BB987654321BR",
      "numero_cliente": "11987654321"
    }
  ]
}

Formato do número:
  ✅ Aceita: "31984163357" ou "11987654321" (apenas dígitos)
  ✅ Aceita: "+5531984163357" (com +55)
  ✅ Aceita: "(31) 98416-3357" (com formatação)
  ❌ Não: "011 98416-3357" (com 0 inicial)


PASSO 3: Fazer commit seguro
────────────────────────────
O .gitignore agora protege:

    .env                    → Suas credenciais não vazam
    whatsapp_session/       → Sessão do WhatsApp privada
    *.log                   → Logs com dados sensíveis
    *.json (históricos)     → Dados de rastreamento
    tokens.json             → Tokens da API

Execute:

    git add .
    git commit -m "Add rastreamento com WhatsApp"
    git push origin main

✅ Seu repositório continua público e seguro!
"""

# ======================================================================
# 💻 USO EM CÓDIGO
# ======================================================================
"""
EXEMPLO 1: Enviar notificação para um cliente
───────────────────────────────────────────────

    from notificador_rastreamento import notificar
    
    etiqueta = "AA123456789BR"
    numero = "31984163357"
    
    sucesso, msg = notificar(etiqueta, numero)
    
    if sucesso:
        print("✅ " + msg)
    else:
        print("❌ " + msg)


EXEMPLO 2: Processar múltiplos rastreamentos
────────────────────────────────────────────

    from notificador_rastreamento import notificar_lote
    
    rastreamentos = [
        ("AA123456789BR", "31984163357"),
        ("BB987654321BR", "11987654321"),
    ]
    
    stats = notificar_lote(rastreamentos)
    
    print(f"✅ {stats['notificacoes_enviadas']} mensagens enviadas")
    print(f"❌ {stats['falha']} erros")


EXEMPLO 3: Apenas consultar status (sem enviar WhatsApp)
────────────────────────────────────────────────────────

    from rastreio_service import obter_status_atual
    
    sucesso, status = obter_status_atual("AA123456789BR")
    
    if sucesso:
        print(status)  # "✅ Objeto entregue - São Paulo"
    else:
        print(f"Erro: {status}")


EXEMPLO 4: Consultar detalhes completos
────────────────────────────────────────

    from rastreio_service import obter_detalhes_completos
    
    dados = obter_detalhes_completos("AA123456789BR")
    
    if dados['sucesso']:
        evento = dados['evento_recente']
        print(f"{evento['emoji']} {evento['status']}")
        print(f"📍 {evento['local']}")
        
        # Ver histórico completo
        for evt in dados['historico']:
            print(f"  - {evt['data']}: {evt['status']}")
"""

# ======================================================================
# 🚀 EXECUÇÃO AUTOMÁTICA
# ======================================================================
"""
AUTOSTART NO WINDOWS (rodar.py)
───────────────────────────────

O script rodar.py foi atualizado para incluir WhatsApp.

Agora executa a cada 5 minutos:

    1. Monitora EMAILs (Bling)
    2. Envia EMAILS (rastreamento)
    3. Envia WHATSAPP (notificações)

Compatível com: INICIAR_AUTOSTART.ps1 ✅


ADICIONAR AO AUTOSTART DO WINDOWS
───────────────────────────────────

1. Crie um arquivo: INICIAR_RASTREAMENTO.ps1

    @echo off
    cd /d c:\SISTEMAS\envio-de-email-Allcanci\envio-de-email-Allcanci
    python rodar.py

2. Abra "Agendador de Tarefas" (Task Scheduler)

3. Crie uma nova tarefa:
   - Nome: "Rastreamento Allcanci"
   - Gatilho: "Na inicialização do computador"
   - Ação: "Inicie um programa"
   - Programa: C:\\Windows\\System32\\cmd.exe
   - Argumentos: /k c:\\caminho\\para\\INICIAR_RASTREAMENTO.ps1

4. Clique em OK e pronto! ✅
"""

# ======================================================================
# 📊 MONITORAMENTO
# ======================================================================
"""
ARQUIVOS DE LOG
───────────────

rastreio_service.log        → Log de consultas à API
rastreamento_cache.log      → Log do cache
notificador_rastreamento.log → Log de notificações WhatsApp

VERIFICAR STATUS:

    tail -f rastreamento_cache.log
    tail -f notificador_rastreamento.log


ARQUIVOS DE DADOS
──────────────────

rastreamento_cache.json          → Cache de consultas (4h expiry)
historico_rastreamento_completo.json → Histórico de mudanças
config_rastreamentos.json        → Configuração de rastreamentos

Estes são IGNORADOS pelo git (protegidos) ✅
"""

# ======================================================================
# 🔐 SEGURANÇA
# ======================================================================
"""
✅ CHECKLIST DE SEGURANÇA

1. ✅ .env está no .gitignore?
   → Verifique: grep -w "^.env$" .gitignore

2. ✅ whatsapp_session/ está no .gitignore?
   → Verifique: grep -w "^whatsapp_session/" .gitignore

3. ✅ Históricos não vão para git?
   → Verifique: git status (não deve mostrar *.json)

4. ✅ Tokens.json não está no git?
   → Verifique: git status | grep tokens.json

Para limpar se já foi adicionado:

    git rm --cached .env whatsapp_session tokens.json
    git commit -m "Remove sensitive files"
    git push origin main

Nota: O arquivo .gitignore já está configurado! ✅
"""

# ======================================================================
# 🧪 TESTES RÁPIDOS
# ======================================================================
"""
TESTE 1: Verificar API Wonca
────────────────────────────

    python -c "
from rastreio_service import RastreioService
service = RastreioService()
print('✅ API Wonca configurada corretamente')
"


TESTE 2: Verificar Cache
────────────────────────

    python rastreamento_cache.py

Saída esperada:
    🧪 TESTE DO CACHE DE RASTREAMENTO
    1️⃣ Guardando dados de AA123456789BR
    2️⃣ Verificando se pode consultar API
    ...


TESTE 3: Verificar Rastreio Service
───────────────────────────────────

    python rastreio_service.py

Saída esperada:
    🧪 TESTE DO SERVIÇO DE RASTREAMENTO
    Consultando: AA123456789BR
    Erro (esperado - etiqueta fictícia)
    ...


TESTE 4: Teste completo (com etiqueta real)
───────────────────────────────────────────

    python -c "
from notificador_rastreamento import notificar
resultado = notificar('AA123456789BR', '31984163357')
print(resultado)
"
"""

# ======================================================================
# ❓ PERGUNTAS FREQUENTES
# ======================================================================
"""
P: Por quanto tempo o cache mantém dados?
R: 4 horas. Após isso, consulta a API novamente.

P: Posso configurar tempo diferente de cache?
R: Sim, edite TEMPO_CACHE_HORAS em rastreamento_cache.py

P: Quantas vezes posso consultar a API por dia?
R: Sem limite teórico, mas cache reduz consumo em ~95%

P: O WhatsApp vai enviar spam?
R: Não! Só envia se status mudar (cache + histórico evitam duplicatas)

P: Minhas credenciais ficarão públicas no GitHub?
R: Não! .env e whatsapp_session estão no .gitignore

P: Como remover dados sensíveis já commitados?
R: git rm --cached .env && git commit

P: Posso usar com números internacionais?
R: Sim, identifica automaticamente. Use +5531984163357

P: Erro "Token inválido"?
R: Verifique WONCA_API_KEY no .env
"""

# ======================================================================
# 📞 SUPORTE
# ======================================================================
"""
CASO ALGO NÃO FUNCIONE:

1️⃣ Verificar logs:
   tail -50f notificador_rastreamento.log

2️⃣ Testar conexão API:
   ping api-labs.wonca.com.br

3️⃣ Verificar .env:
   cat .env | grep WONCA

4️⃣ Testar WhatsApp:
   python -c "from whatsapp_service import enviar_mensagem; enviar_mensagem('31984163357', 'Teste')"

5️⃣ Ver cache:
   python -c "import json; print(json.dumps(json.load(open('rastreamento_cache.json')), indent=2, ensure_ascii=False))"
"""

# ======================================================================

print(__doc__)
