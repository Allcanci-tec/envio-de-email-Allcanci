# 🚀 GUIA RÁPIDO - Setup Completo da API Wonca

## 📊 O que você tem agora

```
✅ API Key criada: dg7Lzu3eoj9PT_-qGrOjF-RJ07C58UWQenw6Vc6iDiY
✅ Módulo Python: wonca_tracking.py
✅ Servidor local: servidor_rastreamento.py
✅ Página HTML: rastreamento.html
⚠️ Problema: Sem crédito na conta + site não está online
```

---

## 🎯 Próximos 5 Passos

### **Passo 1: Adicionar crédito à sua conta**

🌐 Acesse: https://www.siterastreio.com.br/

1. Faça login em sua conta
2. Vá para: **Créditos** ou **Saldo**
3. Escolha forma de pagamento (cartão, boleto, etc)
4. Adicione saldo mínimo (R$ 10-50)

---

### **Passo 2: Testar servidor localmente**

```bash
# Terminal - dentro do projeto
pip install flask requests

python servidor_rastreamento.py
```

Abra: **http://localhost:5001**

Deve ver:
- ✅ Formulário de rastreio
- ✅ Link "Rastreamento" no footer (apontando para siterastreio.com.br)

---

### **Passo 3: Fazer deploy do site**

Escolha **uma** opção:

#### **A) Hostinger (seu host atual)**

1. Painel Hostinger → **Arquivos**
2. Criar pasta: `/public_html/rastreio/`
3. Upload do `rastreamento.html`
4. Renomear para `index.html`
5. URL final: `https://rastreio.allcanci.com.br/`

#### **B) Vercel (+ rápido)**

```bash
npm install -g vercel
cd projeto
vercel
# Seguir instruções e apontar domínio
```

#### **C) GitHub Pages**

```bash
git init
git add rastreamento.html
git commit -m "Page rastreamento"
git push origin main
# Ativar Pages nas settings
```

---

### **Passo 4: Validar que o site está online**

Abrir: `https://rastreio.allcanci.com.br/`

Verificar:
- ✅ Página carrega normalmente
- ✅ Pode ver o formulário
- ✅ Link no footer está visível
- ✅ Link aponta para `https://www.siterastreio.com.br/`

Para confirmar (tecla F12):
```html
<!-- Procurar por isso na página -->
<a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
```

---

### **Passo 5: Revalidar na API Wonca**

1. Voltar para https://www.siterastreio.com.br/
2. **Deletar** a API Key antiga (se houver erro)
3. **Criar nova** API Key:
   - Domínio: `rastreio.allcanci.com.br` ✅
   - Aceitar termos
4. Copiar nova chave para `.env`:
   ```
   WONCA_API_KEY=nova_chave_aqui
   ```
5. Testar:
   ```bash
   python test_wonca_api.py
   ```

---

## ✨ Integração no seu projeto

Depois que tiver crédito e tudo validado:

### **No `automatico_producao.py`**

```python
# No topo
from wonca_tracking import rastrear_wonca

# Dentro do loop de sincronização
def sincronizar_clientes():
    # ... código existente ...
    
    # Tentar rastrear com Wonca se não tiver no Bling
    resultado = rastrear_wonca(codigo_rastreio)
    
    if resultado:
        situacao_atual = resultado['situacao']
        # Usar para comparar com histórico
```

### **Ou criar endpoint web**

```bash
# Iniciar servidor
python servidor_rastreamento.py

# Clientes acessam: https://rastreio.allcanci.com.br/
# Rastreiam códigos em tempo real
```

---

## 🧪 Testes para validar tudo

```bash
# 1. Testar API Wonca
python test_wonca_api.py

# 2. Testar servidor local
python servidor_rastreamento.py
# Abrir http://localhost:5001

# 3. Testar módulo Python
python -c "from wonca_tracking import rastrear_wonca; print(rastrear_wonca('AD292694916BR'))"

# 4. Verificar .env
cat .env | grep WONCA
```

---

## 🎯 Checklist Final

- [ ] Crédito adicionado na conta Wonca
- [ ] Site fazendo deploy em `rastreio.allcanci.com.br`
- [ ] Site está acessível (F5 confirma)
- [ ] Link do footer está visível na página
- [ ] API Key revalidada com novo domínio
- [ ] `.env` atualizado com nova chave
- [ ] Teste local funcionando (`localhost:5001`)
- [ ] `test_wonca_api.py` retorna dados (não erro de crédito)
- [ ] Pronto para integração no projeto!

---

## 📞 Referências

| Arquivo | Função |
|---------|--------|
| `wonca_tracking.py` | 🔄 Módulo de rastreamento |
| `test_wonca_api.py` | 🧪 Teste básico API |
| `servidor_rastreamento.py` | 🚀 Servidor Flask completo |
| `rastreamento.html` | 🌐 Página HTML estática |
| `.env` | 🔐 Configurações |
| `WONCA_API_CONFIG.md` | 📚 Documentação técnica |
| `SITE_RASTREAMENTO_SETUP.md` | 📖 Guia deploy site |

---

## 🆘 Troubleshooting

| Problema | Solução |
|----------|---------|
| 400 - insufficient credit | Adicionar crédito na conta |
| 404 - Page not found | Deploy o arquivo `rastreamento.html` |
| Link não encontrado | Verificar em `https://rastreio.allcanci.com.br/` (F12 > procura por `siterastreio`) |
| API retorna 401 | Validar chave no `.env` |
| Timeout | Verificar conexão N de rede |

---

**🎉 Quando tudo estiver pronto, seu sistema poderá:**
- Rastrear pedidos da API Wonca
- Notificar clientes por email
- Integrar com WhatsApp
- Atualizar histórico automaticamente

Boa sorte! 🚀
