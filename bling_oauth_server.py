#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor local para autenticação OAuth2 com Bling.
Acesse http://localhost:5000 e clique no link para autorizar.
"""

import os
import requests
from flask import Flask, request, redirect
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("BLING_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
REDIRECT_URI = os.getenv("BLING_REDIRECT_URI", "http://localhost:5000/callback")
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"
AUTH_URL = "https://www.bling.com.br/Api/v3/oauth/authorize"


@app.route("/")
def index():
    authorize_url = (
        f"{AUTH_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state=bling_auth"
    )
    return f"""
    <html>
    <head><title>Bling OAuth</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px; background: #f5f5f5;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1>🔐 Autorização Bling</h1>
            <p>Clique no botão abaixo para autorizar o app no Bling:</p>
            <p style="font-size: 12px; color: #666;">Client ID: {CLIENT_ID[:20]}...</p>
            <p style="font-size: 12px; color: #666;">Redirect URI: {REDIRECT_URI}</p>
            <br>
            <a href="{authorize_url}" 
               style="background: #2196F3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 18px;">
                🚀 Autorizar no Bling
            </a>
        </div>
    </body>
    </html>
    """


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error:
        return f"""
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Erro na autorização</h1>
            <p>{error}: {request.args.get('error_description', '')}</p>
            <a href="/">Tentar novamente</a>
        </body></html>
        """

    if not code:
        return "<h1>❌ Nenhum código recebido</h1><a href='/'>Tentar novamente</a>"

    # Trocar o code por tokens
    try:
        r = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
            },
            auth=(CLIENT_ID, CLIENT_SECRET),
            headers={"Accept": "application/json"},
            timeout=30,
        )

        if r.status_code != 200:
            return f"""
            <html><body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Erro ao trocar código por token</h1>
                <p>Status: {r.status_code}</p>
                <p>Resposta: {r.text}</p>
                <a href="/">Tentar novamente</a>
            </body></html>
            """

        data = r.json()
        access_token = data["access_token"]
        refresh_token = data.get("refresh_token", "")
        expires_in = data.get("expires_in", "N/A")

        # Atualizar .env automaticamente
        _update_env(access_token, refresh_token)

        return f"""
        <html>
        <head><title>Bling - Autorizado!</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px; background: #e8f5e9;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h1>✅ Autorizado com sucesso!</h1>
                <p>Os tokens foram gerados e o <strong>.env foi atualizado automaticamente!</strong></p>
                <hr>
                <h3>📋 Novos Tokens:</h3>
                <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 5px;">
                    <strong>ACCESS_TOKEN:</strong><br>{access_token}
                </p>
                <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 5px;">
                    <strong>REFRESH_TOKEN:</strong><br>{refresh_token}
                </p>
                <p>⏱️ Expira em: {expires_in} segundos</p>
                <hr>
                <p style="color: green; font-weight: bold;">✨ Arquivo .env atualizado! Pode fechar esta página e parar o servidor (Ctrl+C).</p>
            </div>
        </body>
        </html>
        """

    except Exception as e:
        return f"""
        <html><body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>❌ Erro</h1>
            <p>{str(e)}</p>
            <a href="/">Tentar novamente</a>
        </body></html>
        """


def _update_env(new_access: str, new_refresh: str):
    """Atualiza os tokens no arquivo .env."""
    env_path = ".env"
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    found_access = found_refresh = False
    for line in lines:
        if line.startswith("BLING_ACCESS_TOKEN="):
            new_lines.append(f"BLING_ACCESS_TOKEN={new_access}\n")
            found_access = True
        elif line.startswith("BLING_REFRESH_TOKEN="):
            new_lines.append(f"BLING_REFRESH_TOKEN={new_refresh}\n")
            found_refresh = True
        else:
            new_lines.append(line)

    if not found_access:
        new_lines.append(f"BLING_ACCESS_TOKEN={new_access}\n")
    if not found_refresh:
        new_lines.append(f"BLING_REFRESH_TOKEN={new_refresh}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"\n✅ .env atualizado com novos tokens!")
    print(f"   ACCESS_TOKEN: {new_access[:30]}...")
    print(f"   REFRESH_TOKEN: {new_refresh[:30]}...")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  🔐 SERVIDOR DE AUTORIZAÇÃO BLING")
    print("=" * 60)
    print(f"\n  📌 Acesse: http://localhost:5000")
    print(f"  📌 Clique em 'Autorizar no Bling'")
    print(f"  📌 Faça login na sua conta Bling")
    print(f"  📌 Os tokens serão salvos automaticamente no .env\n")
    print("=" * 60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
