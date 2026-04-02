# 📱 GUIA DE SOLUCAO DE PROBLEMAS - WHATSAPP PLAYWRIGHT

## Problema: "Nao conseguiu encontrar botao de envio apos 60 segundos"

A sessao do WhatsApp exp irou ou o QR Code nao foi lido corretamente.

---

## Solucao (Passo a Passo)

### **OPCAO 1: DEBUG (Ver o que esta acontecendo)**

1. Execute:
```bash
python debug_whatsapp.py
```

2. O navegador vai abrir VISIVEL
3. Você vai conseguir ver exatamente o que está acontecendo
4. Deixe aberto por 1 minuto para inspecionar
5. Verifique:
   - [ ] O WhatsApp Web carregou normalmente?
   - [ ] Apareceu QR Code?
   - [ ] A conversa abriu?
   - [ ] O campo de texto appears?
   - [ ] Consegue ver um botão de envio?

---

### **OPCAO 2: Limpar e Fazer Login Novamente (RECOMENDADO)**

1. Execute o limpador:
```bash
python limpar_sessao_whatsapp.py
```

2. Agora execute novamente:
```bash
python whatsapp_service.py
```

3. **NA PRIMEIRA EXECUCAO:**
   - O navegador vai abrir com o QR Code
   - Pegue seu celular
   - Abra WhatsApp > Configuracoes > WhatsApp Web
   - Escaneie o QR Code **COM CALMA**
   - Aguarde ate dizer "Aguardando 30 segundos..."
   - A mensagem deve ser enviada automaticamente

4. **NA SEGUNDA EXECUCAO:**
   - O script vai rodar INVISIVEL
   - A mensagem sera enviada automaticamente
   - Nao vai aparecer nada na tela (isso eh normal)

---

## Se ainda nao funcionar...

### **Verifique:**

1. **Internet conectada?**
   - Tente abrir https://web.whatsapp.com no navegador normal
   - Se nao abrir, eh problema de internet

2. **Numero de telefone correto?**
   - Use o formato: `31984163357` ou `(31) 98416-3357`
   - Nao use letras ou caracteres especiais

3. **Celular logado no WhatsApp?**
   - Seu numero de telefone precisa estar com WhatsApp ativo
   - Se estiver logado em outro computador/web, deslogue

4. **Firewall ou AntiVirus bloqueando?**
   - Tente desabilitar temporariamente
   - Ou faca uma excecao para Chromium na Firewall

---

## Arquivos de Diagnostico

### **Logs:**
```
whatsapp_service.log          - Logs detalhados de cada execucao
whatsapp_envios.json          - Historico de mensagens enviadas
```

### **Sessao:**
```
whatsapp_session/             - Cookies e configuracoes do navegador
```

---

## Para Importar em seu Codigo (Flask/FastAPI)

```python
from whatsapp_service import enviar_mensagem

# Enviar uma mensagem
sucesso, mensagem = enviar_mensagem(
    numero="31984163357",
    mensagem="Sua encomenda foi atualizada!"
)

if sucesso:
    print("Enviado com sucesso!")
else:
    print(f"Erro: {mensagem}")
```

---

## Proximos Passos (Apos funcionar)

1. **Integrar em `automatico_producao.py`**
   - Importar `enviar_mensagem` 
   - Chamar quando detectar mudanca de status

2. **Testar com multiplos numeros**
   - Certifique-se que cada numero esta válido
   - Respeite limites de taxa (don't spam)

3. **Adicionar tratamento de erros**
   - Salvar erros em log
   - Tentar reenviar apos falha

---

## Support

Se persistir o problema:
1. Execute `python debug_whatsapp.py` e observe a tela
2. Procure pela mensagem de erro exata no log
3. Se ver "QR Code", escaneie novamente
4. Se ver "Chat aberto", procure o botao de envio com F12
5. Se nada funcionar, delete whatsapp_session/ e comece do zero

---

**Importante**: WhatsApp pode mudar seletores CSS em qualquer momento.  
Se o script parar de funcionar, abra um dev tools (F12) e procure pelo novo seletor! 

