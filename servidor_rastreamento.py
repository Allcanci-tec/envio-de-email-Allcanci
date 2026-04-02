#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor local para testar a página de rastreamento
Acesse: http://localhost:5001
"""

from flask import Flask, render_template_string, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# HTML da página (mesmo do rastreamento.html)
HTML_RASTREAMENTO = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rastreamento - Allcanci</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .logo h1 {
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .logo p {
            color: #666;
            font-size: 14px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .info {
            background: #f0f4ff;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            font-size: 13px;
            color: #555;
            border-left: 4px solid #667eea;
        }
        
        footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 12px;
        }
        
        footer a {
            color: #667eea;
            text-decoration: none;
            margin: 0 10px;
        }
        
        footer a:hover {
            text-decoration: underline;
        }
        
        .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
            display: none;
        }
        
        .result.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
            display: block;
        }
        
        .result.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>📦 Rastreamento</h1>
            <p>Allcanci - Rastreie seu pedido</p>
        </div>
        
        <form id="trackingForm">
            <div class="form-group">
                <label for="trackingCode">Código de Rastreio:</label>
                <input 
                    type="text" 
                    id="trackingCode" 
                    placeholder="Ex: AD292694916BR"
                    required
                    maxlength="20"
                >
            </div>
            
            <button type="submit">🔍 Rastrear</button>
        </form>
        
        <div id="result" class="result"></div>
        
        <div class="info">
            <strong>💡 Dica:</strong> O código de rastreio é enviado por email junto com sua nota fiscal.
        </div>
        
        <footer>
            <p>Powered by <a href="https://www.siterastreio.com.br/" target="_blank">Rastreamento</a></p>
            <p>&copy; 2026 Allcanci - Todos os direitos reservados</p>
        </footer>
    </div>
    
    <script>
        document.getElementById('trackingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const code = document.getElementById('trackingCode').value.trim();
            const resultDiv = document.getElementById('result');
            
            if (code) {
                resultDiv.innerHTML = '⏳ Rastreando...';
                resultDiv.className = 'result';
                
                // Chamar API backend
                fetch('/api/track', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({code: code})
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        resultDiv.innerHTML = `
                            <strong>✅ ${data.status}</strong><br>
                            Código: ${data.code}<br>
                            <small>${data.timestamp}</small>
                        `;
                        resultDiv.className = 'result success';
                    } else {
                        resultDiv.innerHTML = `<strong>⚠️ ${data.message}</strong>`;
                        resultDiv.className = 'result error';
                    }
                })
                .catch(error => {
                    resultDiv.innerHTML = `<strong>❌ Erro:</strong> ${error.message}`;
                    resultDiv.className = 'result error';
                });
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Página principal de rastreamento"""
    return render_template_string(HTML_RASTREAMENTO)

@app.route('/api/track', methods=['POST'])
def track():
    """API para rastrear"""
    from wonca_tracking import rastrear_wonca
    
    data = request.json
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({'success': False, 'message': 'Código de rastreio inválido'}), 400
    
    # Tentar rastrear com Wonca
    resultado = rastrear_wonca(code)
    
    if resultado:
        return jsonify({
            'success': True,
            'code': code,
            'status': resultado.get('situacao', 'Status desconhecido'),
            'timestamp': resultado.get('timestamp', '')
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Erro ao rastrear. Verifique o código.'
        }), 404

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'OK', 'message': 'Servidor de rastreamento online'}), 200

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 SERVIDOR DE RASTREAMENTO INICIADO")
    print("=" * 70)
    print("\n📱 Acesse: http://localhost:5001")
    print("\n📋 Funcionalidades:")
    print("   ✓ Página principal: http://localhost:5001/")
    print("   ✓ API de rastreamento: POST /api/track")
    print("   ✓ Health check: http://localhost:5001/health")
    print("\n✅ Para testar na API Wonca, deploy este arquivo em:")
    print("   https://rastreio.allcanci.com.br/")
    print("\n⏹️  Pressione Ctrl+C para parar\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True,
        use_reloader=True
    )
