#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RENOVAÇÃO AUTOMÁTICA DE TOKEN BLING
Sistema de refresh automático
"""

print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              RENOVAÇÃO DE TOKEN BLING - GUIA COMPLETO                       ║
╚══════════════════════════════════════════════════════════════════════════════╝

PROBLEMA ATUAL
═════════════════════════════════════════════════════════════════════════════

✗ Token expirado: 401 - invalid_token
✗ Não consegue consultar Bling
✗ Sistema para de funcionar

CAUSA: Token com vida útil de ~1 hora ou menos


SOLUÇÕES
═════════════════════════════════════════════════════════════════════════════

1️⃣ SOLUÇÃO RÁPIDA (5 minutos)
═════════════════════════════════════════════════════════════════════════════

Passo 1: Ir ao Painel Bling
  URL: https://www.bling.com.br
  Usuário: seu_email@gmail.com
  Senha: sua_senha

Passo 2: Gerar Novo Token
  • Menu → Integrações
  • Procure por "Aplicações" ou "API"
  • Clique Aplicação "Allcanci" ou "Envio de Email"
  • Botão "Gerar novo token" ou "Regenerar"

Passo 3: Copiar Token
  • Token será algo como: 1a2b3c4d5e6f7g8h9i0j...
  • Copie completamente

Passo 4: Atualizar tokens.json
  • Abra arquivo: tokens.json
  • Substitua valor em "access_token"
  • Salve arquivo

Passo 5: Testar
  $ python DIAGNOSTICO_FALHAS.py
  
  Deve retornar: Status 200 ✓

Tempo: ~5 minutos
Frequência: A cada 1 hora (Token vence)


2️⃣ SOLUÇÃO INTELIGENTE (Sistema de Auto-Refresh)
═════════════════════════════════════════════════════════════════════════════

Pelo .env, vejo que você tem sistema de renovação via Vercel!

Seu .env contém:
  VERCEL_API_TOKEN=vcp_2eeSWqpNQ75iGgFWtBzTfj2lTpk5DpflN8BEENsEN2M...
  VERCEL_PROJECT_ID=prj_QrM99V2dycHyot59rB48JoMIZs7L

Isso significa:
  ✓ Existe backend remoto (Vercel) para renovaçãoautomática
  ✓ Token deveria renovar automaticamente
  ✗ Algo quebrou nesse fluxo

Próxima ação:
  1. Verificar backend Vercel (se ainda está rodando)
  2. Limpar e regenerar token Bling via Vercel


3️⃣ SOLUÇÃO PERMANENTE (Implementar Refresh)
═════════════════════════════════════════════════════════════════════════════

O arquivo automatico_producao.py poderia ter sistema de renovação:

  def refresh_token_se_necessario():
      '''Se houver 401, roda script de renovação automática'''
      
      # Se status 401 → Chamar endpoint de refresh
      # Guardar novo token em tokens.json
      # Tentar novamente


Isso evitaria parar o sistema a toda hora.
PRIORIDADE: MÉDIA (para depois)


PRÓXIMOS PASSOS
═════════════════════════════════════════════════════════════════════════════

1. IMEDIATO: Use Solução Rápida (5 min) para voltar a funcionar

2. DEPOIS: Implemente auto-refresh (quando tiver tempo)

3. MONITORAR: Verifique se token vence sempre na mesma hora
   $ grep "401" rastreamento.log


SE O PROBLEMA PERSISTIR
═════════════════════════════════════════════════════════════════════════════

A. Token sempre expira em menos de 1 hora?
   └─ Verificar se há limite de tempo em Bling (normalmente 1-2 horas)

B. Bling mudou de política?
   └─ Verificar: https://developer.bling.com.br

C. Aplicação foi revogada?
   └─ Recriar aplicação "Allcanci" no painel Bling


COMO GERAR TOKEN BLING (Passo-a-Passo Detalhado)
═════════════════════════════════════════════════════════════════════════════

1. Acesse https://www.bling.com.br
2. Faça login com suas credenciais
3. Menu topo → Integrações/Configurações
4. Procure por "Minhas Aplicações", "API" ou "Autorizações"
5. Procure por "Allcanci" ou "Envio de Email"
6. Se não houver, clique "Adicionar Nova Aplicação"
7. Autorizar acesso às seguintes permissões:
   • Leitura de Pedidos (consultar rastreamento)
   • Leitura de Contatos (email/telefone)
8. Clique "Gerar Token" ou "Renovar Token"
9. Copie token (formato: letras e números, ~40 caracteres)
10. Cole em tokens.json no campo "access_token"


TESTE DE SUCESSO
═════════════════════════════════════════════════════════════════════════════

Após atualizar token, rode:

$ python DIAGNOSTICO_FALHAS.py

Esperado:
  ✓ Status: 200
  ✓ CONEXÃO OK
  ✓ Rastreamento encontrado!

Se vir status 200 → SUCESSO! Sistema volta a funcionar.


═════════════════════════════════════════════════════════════════════════════

🚀 AÇÃO AGORA: Gerar novo token no painel Bling!

═════════════════════════════════════════════════════════════════════════════
""")
