# 🔐 SISTEMA DE REFRESH AUTOMÁTICO - BLING API

## 📋 Resumo das Melhorias

✅ **Refresh automático** - Renova tokens quando expiram  
✅ **Refresh proativo** - Renova 5 minutos antes da expiração  
✅ **Cache persistente** - Salva tokens em `tokens.json`  
✅ **Tratamento de erros** - Retry automático em caso de falha  
✅ **Daemon background** - Monitor contínuo com `token_renewer.py`  
✅ **Lock contra race condition** - Evita renovações simultâneas  

---

## 🚀 Como Usar

### Opção 1: USO SIMPLES (Automático)

```python
from bling_auth import bling_get, bling_post, bling_put

# O token renova automaticamente quando necessário!
contatos = bling_get("/contatos")
pedidos = bling_get("/pedidos/vendas")
```

**Pronto!** Não precisa fazer nada. O sistema renova sozinho.

---

### Opção 2: COM DAEMON EM BACKGROUND (Recomendado)

Para máxima confiabilidade, rode o daemon em um terminal separado:

```bash
# Terminal 1 - Daemon (deixa rodando)
python token_renewer.py

# Terminal 2 - Sua aplicação
python seu_projeto.py
```

O daemon:
- ✅ Monitora o token continuamente
- ✅ Renova **proativamente** 10 minutos antes de expirar
- ✅ Exibe o status em tempo real
- ✅ Roda indefinidamente até você parar (Ctrl+C)

---

## 📊 Arquivos Criados/Atualizados

| Arquivo | Descrição |
|---------|-----------|
| `bling_auth.py` | ✨ **Melhorado** - Sistema de refresh automático |
| `token_renewer.py` | 🆕 Daemon para renovação em background |
| `test_refresh.py` | 🆕 Script de teste |
| `tokens.json` | 🆕 Cache persistente (criado automaticamente) |
| `.env` | ✅ Contém os tokens |

---

## 🔍 Verificar Status do Token

```python
from bling_auth import get_token_info

info = get_token_info()
print(info)
# {
#   "status": "✅ Válido",
#   "expires_in_minutes": 345,
#   "expires_in_seconds": 20700,
#   "token": "92ac659d091dca62d93b..."
# }
```

---

## ⚙️ Como Funciona o Refresh

1. **Na primeira requisição**:
   - Carrega token do `.env`
   - Tenta carregar do cache `tokens.json` se válido

2. **Antes de cada requisição (`bling_get`, `bling_post`, `bling_put`)**:
   - Verifica se token expira em menos de 5 minutos
   - Se sim → Renova automaticamente
   - Se não → Usa token atual

3. **Ao renovar**:
   - Faz POST em `https://www.bling.com.br/Api/v3/oauth/token`
   - Atualiza `.env` (persistente entre reinicializações)
   - Salva em `tokens.json` (cache em memória mais rápido)
   - Exibe mensagem de log

4. **Com o daemon**:
   - Verifica a cada 1 minuto
   - Renova **proativamente** 10 minutos antes
   - Evita expiração durante requisições longas

---

## 🔧 Configuração

Tudo já está configurado no `.env`:

```env
BLING_CLIENT_ID=909e1d4ab611669f27494b0a05c4d60c4e036d6b
BLING_CLIENT_SECRET=0c56fb5fc13445a95acab321bb38a831a6e46fb889da6830dd90b22fd64e
BLING_ACCESS_TOKEN=92ac659d091dca62d93b5c85c6829c29e5efce10
BLING_REFRESH_TOKEN=e917281d5c14e352c65a632e861496aaf1d6185a
```

---

## 📌 Boas Práticas

✅ **Sempre use `get_token()`** - Garante token válido  
✅ **Rode o daemon** - Para aplicações de longa duração  
✅ **Monitore logs** - Veja quando o token renova  
✅ **Guarde `tokens.json`** - Não apague este arquivo  
✅ **Não compartilhe credenciais** - Nunca comita `.env` no Git  

---

## 🆘 Troubleshooting

### "Token expirado"
→ Rode o daemon em background ou chame `get_token()` novamente

### "invalid_grant"
→ `BLING_REFRESH_TOKEN` expirou. Execute `bling_oauth_server.py` para gerar novo

### "Erro ao renovar token"
→ Verifique se `CLIENT_ID` e `CLIENT_SECRET` estão corretos no `.env`

---

## 🎯 Resumo

Seu projeto **agora tem**:

1. ✨ Tokens que renovam **automaticamente**
2. 🔄 Refresh **proativo** antes de expirar  
3. 💾 Cache **persistente** em arquivo
4. 🛡️ Tratamento de **erros robusto**
5. 📊 **Logging** para monitoramento
6. 🎯 **Compatível** com suas funções atuais

**Pronto para usar!** 🚀
