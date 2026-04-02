# 🔧 SOLUÇÃO DE PROBLEMAS - API WONCA BLOQUEADA

## ❌ Erros Possíveis e Soluções

### 1️⃣ Erro 401 - Unauthorized
**Mensagem**: `Token de API inválido ou expirado`

**Causas**:
- Token expirou
- Token está incorreto
- Domínio não foi registrado na Wonca

**Solução**:
```bash
# A. Acesse https://labs.wonca.com.br
# B. Faça login
# C. Vá em "Aplicações"
# D. Crie/Edite sua aplicação:
#    - Nome: Allcanci Rastreamento
#    - Domínio: allcanci-tec.github.io
#    - Copie a nova API Key
# E. Atualize .env:

WONCA_API_KEY=nova_chave_aqui
```

---

### 2️⃣ Erro 403 - Forbidden
**Mensagem**: `Acesso negado`

**Causas**:
- API Key sem permissão para esse endpoint
- Conta suspensa ou bloqueada
- Domínio não registrado

**Solução**:
```bash
# Contate suporte Wonca:
# https://labs.wonca.com.br/suporte
# ou
# email: suporte@wonca.com.br
# 
# Cole este erro:
# "Error 403 Forbidden - Domain not registered or API Key invalid"
```

---

### 3️⃣ Erro 429 - Rate Limiting
**Mensagem**: `Muitas requisições`

**Causas**:
- Limite de requisições/minuto excedido
- Sistema fazendo muitas consultas

**Solução**:
```python
# O cache já resolve isso!
# rastreamento_cache.py garante:
# - 4 horas entre consultas mesma etiqueta
# - Reduz ~95% das requisições

# Mas se ainda tiver erro:
# Aguarde 60 segundos antes do próximo envio
import time
time.sleep(60)
```

---

### 4️⃣ Erro 500 - Server Error
**Mensagem**: `Erro interno do servidor`

**Causas**:
- Servidor Wonca fora do ar
- Manutenção em andamento
- Bug temporário

**Solução**:
```bash
# Aguarde alguns minutos
# Tente novamente
# Se persistir por >30min, contate suporte Wonca
```

---

### 5️⃣ Timeout - Servidor muito lento
**Mensagem**: `Timeout na requisição`

**Causas**:
- Conexão lenta
- Servidor sobrecarregado
- Problema de rede

**Solução**:
```bash
# A. Teste sua conexão:
ping api-labs.wonca.com.br

# B. Se tiver DNS lento, use IP direto (se Wonca fornecer)

# C. Aumentar timeout em rastreio_service.py:
TIMEOUT_REQUISICAO = 20  # aumentar de 15

# D. Usar cache:
python -c "from rastreamento_cache import obter_do_cache; print(obter_do_cache('AA123456789BR'))"
```

---

## 🧪 Teste Passo-a-Passo

### Passo 1: Verificar Token
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('WONCA_API_KEY'))"
```
**Esperado**: Deve mostrar sua chave API (algo como `dg7Lzu3...`)

### Passo 2: Executar Diagnostico Completo
```bash
python test_wonca_connection.py
```
**Esperado**: Teste de conexão bem-sucedido

### Passo 3: Testar com Etiqueta Real
```bash
python -c "
from rastreio_service import obter_status_atual
sucesso, msg = obter_status_atual('AA123456789BR')  # Substitua por etiqueta real
print('SUCCESS' if sucesso else 'FAILED')
print(msg)
"
```

### Passo 4: Testar Cache
```bash
python rastreamento_cache.py
```

### Passo 5: Teste de Integração Completa
```bash
python -c "
from notificador_rastreamento import notificar
resultado = notificar('AA123456789BR', '31984163357')  # Substitua valores
print(resultado)
"
```

---

## 🔐 Checklist de Configuração

- [ ] WONCA_API_KEY está em .env?
- [ ] Token foi gerado em https://labs.wonca.com.br?
- [ ] Domínio `allcanci-tec.github.io` está registrado na Wonca?
- [ ] .env não está no git (protegido por .gitignore)?
- [ ] Testou `test_wonca_connection.py`?
- [ ] Tem etiqueta real para testar (não fictícia)?

---

## 💡 Dicas de Debug

### Ver logs detalhados
```bash
# Terminal 1: Ver logs em tempo real
tail -f rastreio_service.log | grep -E "Tentativa|Status|Algoritmo"

# Terminal 2: Executar comando
python -c "from rastreio_service import obter_status_atual; print(obter_status_atual('AA123456789BR'))"
```

### Inspecionar requisição com curl
```bash
# Teste manualmente a API
curl -X POST https://api-labs.wonca.com.br/wonca.labs.v1.LabsService/Track \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code": "AA123456789BR"}' \
  -v
```

### Verificar DNS
```bash
# Se tiver problema de conexão
nslookup api-labs.wonca.com.br
# ou
ping api-labs.wonca.com.br
```

---

## 📞 Suporte Oficial

**Wonca Labs**:
- Site: https://labs.wonca.com.br
- Documentação: https://labs.wonca.com.br/doc
- Email: suporte@wonca.com.br
- Chat: Disponível no site

**SiteRastreio**:
- Site: https://www.siterastreio.com.br
- Documentação: Mesma da Wonca

---

## ✅ Solução Rápida

Se nada funcionar:

1. **Gere novo token**: https://labs.wonca.com.br → Aplicações → Nova API Key
2. **Atualize .env**:
   ```
   WONCA_API_KEY=seu_novo_token
   ```
3. **Teste**:
   ```
   python test_wonca_connection.py
   ```
4. **Se ainda não funcionar**, contate suporte Wonca com:
   - Seu ID de aplicação
   - Token que está usando
   - Código de erro exato
   - Timestamp do erro

---

## 🚀 Verificação Final

Quando tudo estiver funcionando:

```bash
# Deve retornar sucesso com ✅
python -c "
from notificador_rastreamento import notificar
sucesso, msg = notificar('CODIGO_REAL', '31984163357')
print('✅ TUDO OK!' if sucesso else f'❌ {msg}')
"
```

Pronto! Sistema em produção ✨
