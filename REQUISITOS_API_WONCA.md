# ✅ O QUE A API WONCA ESTÁ PEDINDO

## 🔍 O Erro que você recebeu

```
[invalid_argument] link não encontrado na página inicial do site
```

---

## 📌 O que significa?

A API faz uma **verificação automática** no seu site:

1. Acessa: `https://rastreio.allcanci.com.br/`
2. Procura por: `<a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>`
3. Se achar → ✅ Aprova
4. Se não achar → ❌ Rejeita com erro

---

## ✨ O que você enviou

```
Domínio: rastreio.allcanci.com.br
Link no footer: <a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
```

---

## ❌ Por que foi rejeitado?

Porque quando a API tentou acessar `https://rastreio.allcanci.com.br/`:

1. **Site não existe** (página 404 ou não hospedada)
2. **OU** site existe mas não tem o link

---

## ✅ O que você precisa fazer

### **Mínimo necessário:**

Ter uma página em `https://rastreio.allcanci.com.br/` que contenha:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Rastreamento</title>
</head>
<body>
    <h1>Rastreamento de Pedidos</h1>
    
    <!-- Seu conteúdo aqui -->
    
    <footer>
        <!-- ⭐ ESTE LINK É OBRIGATÓRIO ⭐ -->
        <a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
    </footer>
</body>
</html>
```

---

## 📊 Exemplo Real - O que a API fez:

```python
# O verificador da API fez isso:
import requests
from bs4 import BeautifulSoup

url = 'https://rastreio.allcanci.com.br/'
response = requests.get(url)

html = response.text

# Procurou por este link exato:
if '<a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>' in html:
    print("✅ Link encontrado - API Key válida")
else:
    print("❌ Link não encontrado - Rejeitado")
```

---

## 🚀 Solução Rápida (em 3 minutos)

### **Via Hostinger:**

1. **Painel** → Gerenciador de Arquivos
2. **Navegar** para `/public_html/`
3. **Criar pasta** `rastreio`
4. **Criar arquivo** `index.html` com:

```html
<!DOCTYPE html>
<html>
<head><title>Rastreamento</title></head>
<body>
<h1>Rastreamento</h1>
<p>Rastreie seu pedido abaixo:</p>
<input type="text" placeholder="Código de rastreio">
<footer>
<a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
</footer>
</body>
</html>
```

5. **Testar**: Abrir `https://rastreio.allcanci.com.br/`
6. **Confirmar**: F12 > procurar por "siterastreio"

---

## 🎯 Arquivos que já criamos para você

```
✅ rastreamento.html          → Página HTML completa (pronta para usar)
✅ servidor_rastreamento.py   → Servidor local com integração
✅ SITE_RASTREAMENTO_SETUP.md → Guia detalhado de deploy
✅ GUIA_RAPIDO_SETUP.md       → Checklist de 5 passos
```

---

## 🔄 Fluxo Correto

```
1️⃣ Upload arquivo (rastreamento.html)
        ↓
2️⃣ Verificar que site está online
        ↓
3️⃣ Confirmar links estão presentes (F12)
        ↓
4️⃣ Voltar à API Wonca e recriar chave
        ↓
5️⃣ Atualizar .env com nova chave
        ↓
6️⃣ Testar: python test_wonca_api.py
        ↓
7️⃣ ✅ Funcionando!
```

---

## 📝 Resumo em 1 linha

> **Você precisa hospedar um arquivo HTML em `rastreio.allcanci.com.br` que contenha um link apontando para `https://www.siterastreio.com.br/`**

---

## 💡 Dica: Teste localmente ANTES

```bash
# Abra este arquivo direto no navegador
rastreamento.html

# Ou use o servidor:
python servidor_rastreamento.py
# Acesse: http://localhost:5001
```

Se funcionar localmente, vai funcionar online! ✅

---

## ❓ Dúvidas frequentes

**P: O domínio rastreio.allcanci.com.br já está configurado?**  
R: Sim, mas não está em uso. Se não tiver subdomain configurado no Hostinger, vai precisar criar.

**P: Existe forma de verificar se está certo?**  
R: Sim! Após upload, fazer:
```bash
curl https://rastreio.allcanci.com.br/ | grep "siterastreio"
```
Se aparecer a URL, está OK ✅

**P: Posso usar qualquer domínio?**  
R: Não! Tem que ser exatamente `rastreio.allcanci.com.br` (ou subdomínio que você especificou)

**P: Pode ser HTTP ao invés de HTTPS?**  
R: Recomendado HTTPS, mas pode testar antes com HTTP no localhost

---

## 🎉 Quando tudo estiver certo

```
✅ Site acessível
✅ Link encontrado
✅ API Key válida
✅ Crédito ativo
✅ Integrando com seu projeto!
```

Aí sim você consegue rastrear os pedidos com a API Wonca! 🚀
