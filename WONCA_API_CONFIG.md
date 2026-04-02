# 🔧 Configuração da API Wonca Labs (SiteRastreio)

## ✅ Status Atual

- **API Key**: ✓ Criada e configurada
- **Estrutura**: ✓ Validada  
- **Integração**: ✓ Pronta para usar
- **Crédito**: ⚠️ Sem saldo (precisa adicionar)

---

## 📋 O que foi configurado

### 1. **.env atualizado**
```
WONCA_API_KEY=dg7Lzu3eoj9PT_-qGrOjF-RJ07C58UWQenw6Vc6iDiY
WONCA_API_URL=https://api-labs.wonca.com.br
WONCA_SERVICE_PATH=wonca.labs.v1.LabsService/Track
```

### 2. **Módulo Python criado**: `wonca_tracking.py`
- Cliente para a API Wonca
- Tratamento de erros robusto
- Logging integrado
- Fácil de usar

### 3. **Scripts de teste criados**
- `test_wonca_api.py` - Teste básico
- `exemplo_wonca_usage.py` - Exemplo de integração

---

## 🔑 Estrutura da API Wonca

### Requisição
```python
import requests

headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Apikey YOUR_API_KEY'  # ⚠️ "Apikey" não "Bearer"
}

payload = {"code": "AD292694916BR"}

response = requests.post(
    'https://api-labs.wonca.com.br/wonca.labs.v1.LabsService/Track',
    headers=headers,
    json=payload
)
```

### Resposta (exemplo com sucesso)
```json
{
  "code": "AD292694916BR",
  "status": "Entregue",
  "events": [
    {
      "timestamp": "2026-04-02T10:30:00",
      "status": "Entregue",
      "location": "São Paulo",
      "description": "Entregue ao destinatário"
    }
  ]
}
```

---

## ⚠️ Erro Atual: Sem Crédito

```
Status: 400
Message: "insufficient credit balance"
```

### Solução

1. **Entre no site**: https://www.siterastreio.com.br
2. **Acesse sua conta**
3. **Vá para**: Mensagem ou Configurações > Créditos
4. **Adicione crédito** (débito, cartão, boleto, etc.)
5. Depois teste novamente com:
   ```bash
   python test_wonca_api.py
   ```

---

## 🚀 Como usar no seu projeto

### Opção 1: Função simples
```python
from wonca_tracking import rastrear_wonca

# Rastrear um código
resultado = rastrear_wonca('AD292694916BR')

if resultado:
    print(resultado['situacao'])  # Ex: "Entregue ao destinatário"
```

### Opção 2: Cliente completo
```python
from wonca_tracking import WoncaTrackingAPI

api = WoncaTrackingAPI()

# Rastrear
dados = api.rastrear('AD292694916BR')

# Extrair situação
situacao = api.extrair_situacao(dados)

# Formatar resposta
resultado = api.formatar_resposta('AD292694916BR', dados)
```

### Opção 3: Integrar ao `automatico_producao.py`
```python
# No topo do arquivo
from wonca_tracking import rastrear_wonca

# Dentro da função de sincronização, após buscar do Bling:
# Se não encontrar no Bling, tenta Wonca
resultado_wonca = rastrear_wonca(codigo_rastreio)
if resultado_wonca:
    situacao = resultado_wonca['situacao']
    # Usar para comparar com histórico
```

---

## 📊 Diferenças: Bling vs Wonca

| Aspecto | Bling API | Wonca Labs |
|---------|-----------|-----------|
| URL | `api.bling.com.br/v3` | `api-labs.wonca.com.br` |
| Auth | Bearer | Apikey |
| Método | GET/POST | POST |
| Requisição | Query params | JSON body |
| Estrutura | Bling-específica | Wonca/Correios standard |
| Limite | Consultas |Por crédito |

---

## 🧪 Testes disponíveis

```bash
# Teste básico da API
python test_wonca_api.py

# Exemplo de uso
python exemplo_wonca_usage.py

# Teste com módulo Python
python -c "from wonca_tracking import rastrear_wonca; print(rastrear_wonca('AD292694916BR'))"
```

---

## 📝 Próximos Passos

1. ✅ Adicionar crédito à conta
2. ⏳ Testar novamente: `python test_wonca_api.py`
3. 📦 Integrar ao `automatico_producao.py`
4. 🔄 Configurar verificação periódica
5. 📧 Notificar via email/WhatsApp

---

## 🆘 Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| 400 - insufficient credit | Sem crédito | Adicionar crédito na conta |
| 401 - Unauthorized | API Key inválida | Verificar chave no .env |
| 404 - Not Found | URL errada | Usar URL de `api-labs.wonca.com.br` |
| Timeout | Conexão lenta | Verificar N de rede |

---

## 📞 Links úteis

- 🌐 SiteRastreio: https://www.siterastreio.com.br
- 📚 Docs Wonca: Consultar com suporte
- 💬 Suporte: suporte@siterastreio.com.br
