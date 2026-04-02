# 📦 Configuração do Site de Rastreamento

## ⚠️ Problema Atual

```
[invalid_argument] link não encontrado na página inicial do site
```

**Causa**: A API Wonca verifica se existe o link `<a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>` na página inicial do seu site `rastreio.allcanci.com.br`

---

## ✅ Solução

### Arquivos criados:
1. **`rastreamento.html`** - Página de rastreamento com link no footer

### O que fazer:

#### **PASSO 1: Deploy da página**

Você tem 3 opções:

##### **Opção A: Hostinger (recomendado)**
```
1. Acesse seu painel Hostinger
2. Vá para: Arquivos > File Manager
3. Crie pasta: public_html/rastreio
4. Upload do arquivo rastreamento.html
5. Renomeie para index.html
6. URL fica: https://rastreio.allcanci.com.br/
```

##### **Opção B: Vercel (mais rápido)**
```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Na pasta do projeto
vercel

# 3. Configurar domínio: rastreio.allcanci.com.br
```

##### **Opção C: GitHub Pages
```
1. Criar repo: allcanci/rastreamento
2. Fazer upload do rastreamento.html
3. Ir em Settings > Pages
4. Deploy como site estático
5. Conectar domínio rastreio.allcanci.com.br
```

---

#### **PASSO 2: Verificar se está online**

Abrir no navegador:
```
https://rastreio.allcanci.com.br/
```

Deve ver:
- ✅ Página com campo de rastreio
- ✅ Footer com link "Rastreamento"
- ✅ Link apontando para `https://www.siterastreio.com.br/`

---

#### **PASSO 3: Re-validar na API Wonca**

Voltar para https://www.siterastreio.com.br e:

1. **Deletar** a API Key anterior (se necessário)
2. **Criar nova** com:
   - Domínio: `rastreio.allcanci.com.br`
   - Link no footer: OK ✅

---

## 📝 HTML Necessário

O arquivo `rastreamento.html` já contém:

```html
<footer>
    <!-- ⚠️ Este link é obrigatório! -->
    <a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
</footer>
```

---

## 🧪 Teste Local

Se quiser testar sem fazer deploy:

```bash
# Abrir o arquivo diretamente
# Windows
start rastreamento.html

# macOS
open rastreamento.html

# Linux
xdg-open rastreamento.html
```

Verá a página funcionando localmente!

---

## 🔗 Estrutura Mínima (se precisar criar manualmente)

Se você quiser criar sua própria página, inclua **obrigatoriamente**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Rastreamento - Allcanci</title>
</head>
<body>
    <h1>Rastreamento</h1>
    
    <!-- Conteúdo da página -->
    
    <footer>
        <!-- ⚠️ Este link é OBRIGATÓRIO -->
        <a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a>
    </footer>
</body>
</html>
```

---

## 🚀 Próximos Passos

1. **Deploy** o `rastreamento.html` em `rastreio.allcanci.com.br`
2. **Verifique** que o site está acessível
3. **Valide** o link na API Wonca
4. **Crie nova** API Key com o domínio correto
5. **Teste** o rastreamento com código real

---

## 💡 Dicas

- ✅ O link deve estar **visível** na página (pode ser no footer, menu, etc)
- ✅ Usar `target="_blank"` é importante
- ✅ URL deve ser exatamente: `https://www.siterastreio.com.br/`
- ✅ Testar em modo **privado/incógnito** do navegador

---

## 🆘 Se ainda der erro

Possíveis causas:
1. Site não está online
2. Link não está na página ou está com URL errada
3. Domínio não está apontando para a página correta
4. Firewall bloqueando acesso

**Solução**: 
- Abrir no navegador: `https://rastreio.allcanci.com.br/`
- Verificar se consegue ver a página
- Abrir página > Inspecionar (F12) > procurar por "siterastreio"
