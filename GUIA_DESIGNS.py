#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUIA COMPLETO - DESIGNS DE NOTIFICAÇÃO
Documentação do sistema de envio de emails e WhatsApp
"""

GUIA = """
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║   🎨 DESIGNS DE NOTIFICAÇÃO - ALLCANCI RASTREAMENTO                      ║
║                                                                            ║
║   Guia Completo de Email e WhatsApp                                       ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


═══════════════════════════════════════════════════════════════════════════════
📧 1. EMAIL PARA CLIENTE/ESCOLA
═══════════════════════════════════════════════════════════════════════════════

CARACTERÍSTICAS:
  ✓ Design limpo e profissional
  ✓ Gradient AZUL (temas corporativo)
  ✓ HTML responsivo
  ✓ Emojis para melhor visual
  ✓ Todas as informações importantes

ESTRUTURA:
  ┌─────────────────────────────────┐
  │  🎨 Gradient Azul (Header)      │  ← Cor primária Allcanci
  │  ────────────────────────────   │
  │  📦 Atualização de Rastreamento │
  └─────────────────────────────────┘
  
  Olá [CLIENTE],
  
  Seu pedido teve uma atualização importante:
  
  ┌─────────────────────────────────┐
  │  ✅ [STATUS]                    │  ← Status em destaque
  │     SAIU PARA ENTREGA           │
  └─────────────────────────────────┘
  
  📋 DETALHES:
  • 📦 Pedido: 2024001
  • 📍 Rastreamento: AA123456789BR
  • 📅 Atualizado em: 08/04/2026 08:23
  • 📝 Descrição: Saiu para entrega

EMAILS:
  Remetente: suporte1@allcanci.com.br
  Assunto: "Pedido [NUMERO] - [STATUS]"
  Exemplo: "Pedido 2024001 - Saiu para entrega"


═══════════════════════════════════════════════════════════════════════════════
📨 2. EMAIL PARA VENDEDOR
═══════════════════════════════════════════════════════════════════════════════

CARACTERÍSTICAS:
  ✓ Design diferenciado com gradient LARANJA
  ✓ Informação do cliente incluída
  ✓ Contexto de quem vende
  ✓ Rastreamento de suas vendas

ESTRUTURA:
  ┌─────────────────────────────────┐
  │  🎨 Gradient Laranja (Header)   │  ← Destaca vendedor
  │  ────────────────────────────   │
  │  🚀 Atualização de Pedido       │
  │     do Cliente                  │
  └─────────────────────────────────┘
  
  Olá [VENDEDOR],
  
  O pedido do cliente [CLIENTE] teve uma atualização importante:
  
  ┌─────────────────────────────────┐
  │  ✅ [STATUS]                    │  ← Status em destaque
  │     SAIU PARA ENTREGA           │
  └─────────────────────────────────┘
  
  📋 DETALHES:
  • 👤 Cliente: Israel Pinheiro
  • 📦 Pedido: 2024001
  • 📍 Rastreamento: AA123456789BR
  • 📅 Atualizado em: 08/04/2026 08:23
  • 📝 Descrição: Saiu para entrega

EMAILS:
  Remetente: suporte1@allcanci.com.br
  Assunto: "Pedido [NUMERO] ([CLIENTE]) - [STATUS]"
  Exemplo: "Pedido 2024001 (Israel Pinheiro) - Saiu para entrega"


═══════════════════════════════════════════════════════════════════════════════
💬 3. MENSAGEM WHATSAPP
═══════════════════════════════════════════════════════════════════════════════

CARACTERÍSTICAS:
  ✓ Sem HTML (texto puro)
  ✓ Usa emojis para expressão
  ✓ Formatação markdown (*negrito*)
  ✓ Link para rastreamento Correios
  ✓ Informal mas profissional

FORMATO:
  📦 *ATUALIZAÇÃO DE RASTREAMENTO*

  Olá *[CLIENTE]*,

  Seu pedido teve uma atualização importante:

  ✅ *[STATUS]*

  *Detalhes:*
  🔹 Pedido: [NUMERO]
  🔹 Rastreamento: [ETIQUETA]
  🔹 Atualizado em: [DATA/HORA]

  🔗 Acompanhe: https://www.correios.com.br

  _Allcanci Tecnologia_

EXEMPLO:
  📦 *ATUALIZAÇÃO DE RASTREAMENTO*

  Olá *Israel Pinheiro*,

  Seu pedido teve uma atualização importante:

  ✅ *SAIU PARA ENTREGA*

  *Detalhes:*
  🔹 Pedido: 2024001
  🔹 Rastreamento: AA123456789BR
  🔹 Atualizado em: 08/04/2026 08:23

  🔗 Acompanhe: https://www.correios.com.br

  _Allcanci Tecnologia_

COMO FUNCIONA:
  1. Script valida o número de telefone
  2. Integração com whatsapp_service.py
  3. Respeita anti-spam automaticamente
  4. Se falhar, adiciona à fila de processamento


═══════════════════════════════════════════════════════════════════════════════
🔄 FLUXO DE ENVIO AUTOMÁTICO
═══════════════════════════════════════════════════════════════════════════════

AUTOMÁTICO (automatico_producao.py):
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Verifica mudanças de status (Bling → Local JSON)    │
  │ 2. Se mudou:                                            │
  │    ├─ Email para cliente (se tiver email)              │
  │    ├─ Email para vendedor (se configurado)             │
  │    └─ WhatsApp para cliente (se tiver telefone)        │
  │ 3. Salva registro em contatos_rastreamento.json        │
  │ 4. Salva email em INBOX.Sent (IMAP)                    │
  │ 5. Log com histórico completo                          │
  └─────────────────────────────────────────────────────────┘

VALIDAÇÕES:
  ✓ Email: deve ser válido (contem @, domínio)
  ✓ Telefone: mínimo 10 dígitos
  ✓ Status: não envia duplicado para mesma situação
  ✓ IMAP: detecta automaticamente pasta Enviados


═══════════════════════════════════════════════════════════════════════════════
🧪 COMO TESTAR - SCRIPTS DISPONÍVEIS
═══════════════════════════════════════════════════════════════════════════════

1️⃣  TESTE IMAP (teste_imap_connection.py)
   Valida conexão com servidor IMAP
   ✓ Conecta e autentica
   ✓ Lista pastas
   ✓ Salva email de teste em INBOX.Sent
   
   Comando: python teste_imap_connection.py

2️⃣  TESTE COMPLETO (teste_envio_completo.py)
   Mostra todos os designs e pode enviar
   ✓ Exibe design cliente
   ✓ Exibe design vendedor
   ✓ Exibe mensagem WhatsApp
   ✓ Valida emails e telefone
   ✓ Envia email real (opcional)
   
   Comando: python teste_envio_completo.py

3️⃣  PREVIEW HTML (preview_designs.html)
   Visualiza os designs em navegador
   ✓ Designs lado-a-lado
   ✓ Dados de exemplo
   ✓ Info sobre validações
   
   Abrir: double-click no arquivo


═══════════════════════════════════════════════════════════════════════════════
⚙️ CONFIGURAÇÕES (.env)
═══════════════════════════════════════════════════════════════════════════════

SMTP (Envio):
  EMAIL_USUARIO=seu-email@allcanci.com.br
  EMAIL_SENHA=sua-senha
  EMAIL_SMTP=smtp.hostinger.com
  EMAIL_PORTA=465

IMAP (Salvar em Enviados):
  EMAIL_IMAP=imap.hostinger.com
  EMAIL_IMAP_PORTA=993

Pasta Detectada:
  ✓ INBOX.Sent (Hostinger)


═══════════════════════════════════════════════════════════════════════════════
📊 ESTRUTURA DE DADOS (contatos_rastreamento.json)
═══════════════════════════════════════════════════════════════════════════════

Cada contato tem:

{
  "numero": "2024001",
  "cliente": "Israel Pinheiro",
  "email": "israel@example.com",
  "telefone": "(85) 98888-9999",
  "vendedor_nome": "Carlos Santos",
  "vendedor_email": "carlos@example.com",
  "etiqueta": "AA123456789BR",
  "ultima_situacao": "Saiu para entrega",
  "emails_enviados": [
    {
      "situacao": "saiu para entrega",
      "data": "08/04/2026 08:23"
    }
  ],
  "emails_vendedor_enviados": [
    {
      "situacao": "saiu para entrega",
      "data": "08/04/2026 08:23",
      "vendedor": "Carlos Santos"
    }
  ]
}


═══════════════════════════════════════════════════════════════════════════════
🚀 COMO USAR EM PRODUÇÃO
═══════════════════════════════════════════════════════════════════════════════

1. Crie um arquivo .env com credenciais reais
2. Execute: python automatico_producao.py
3. Sistema roda continuamente monitorando Bling
4. Cada mudança de status → emails e WhatsApp automáticos
5. Verifique logs: rastreamento.log
6. Confirme em "Enviados" do seu email


═══════════════════════════════════════════════════════════════════════════════
📋 CHECKLIST DE IMPLEMENTAÇÃO
═══════════════════════════════════════════════════════════════════════════════

PRÉ-REQUISITOS:
  ✓ Python 3.7+
  ✓ Credenciais Hostinger/Email
  ✓ Conta Bling com API configurada
  ✓ (Opcional) WhatsApp Business API

INSTALAÇÃO:
  ✓ pip install -r requirements.txt
  ✓ Configurar .env
  ✓ Testar IMAP: python teste_imap_connection.py
  ✓ Adicionar contatos: contatos_rastreamento.json

VALIDAÇÃO:
  ✓ Emails aparecem em "Enviados"
  ✓ Clientes recebem notificações
  ✓ Vendedores recebem notificações
  ✓ Logs registram tudo

MONITORAMENTO:
  ✓ Verifique rastreamento.log
  ✓ Dashboard: python dashboard_server.py
  ✓ Monitore rate limiting do Bling


═══════════════════════════════════════════════════════════════════════════════
💡 DICAS IMPORTANTES
═══════════════════════════════════════════════════════════════════════════════

1. ANTI-SPAM:
   • Sistema não envia 2x o mesmo email para mesma situação
   • Throttling entre envios (2 segundos)
   • Máximo X emails por ciclo

2. ERROS COMUNS:
   • Email não salva em "Enviados"
     → Valide IMAP com teste_imap_connection.py
   
   • Cliente não recebe email
     → Verifique spam/lixo
     → Valide email no contatos_rastreamento.json
   
   • WhatsApp não funciona
     → Verifique whatsapp_service.py
     → Valide número de telefone
     → Verifique integração com API

3. CUSTOMIZAÇÃO:
   • Mudança cores: edite gradientes em automatico_producao.py
   • Nova situação: adicione em SITUACOES_* no arquivo
   • Novo texto: altere templates HTML


═══════════════════════════════════════════════════════════════════════════════

Dúvidas? Consulte:
  • automatico_producao.py - Código principal
  • teste_envio_completo.py - Exemplo de uso
  • preview_designs.html - Visualizar designs
  • rastreamento.log - Logs de execução

═══════════════════════════════════════════════════════════════════════════════
"""

if __name__ == '__main__':
    print(GUIA)
