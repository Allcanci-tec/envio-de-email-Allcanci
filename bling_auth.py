# bling_auth.py
# Sistema de autenticação OAuth2 com Bling
# Com refresh automático e proativo de tokens

import os
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("BLING_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLING_CLIENT_SECRET")
TOKEN_URL = "https://www.bling.com.br/Api/v3/oauth/token"
BASE_URL = "https://api.bling.com.br/Api/v3"

# Arquivo para persistir tokens
TOKENS_FILE = "tokens.json"

# Cache em memória — persiste enquanto o processo roda
_token_cache = {
    "access_token": os.getenv("BLING_ACCESS_TOKEN") or "",
    "refresh_token": os.getenv("BLING_REFRESH_TOKEN") or "",
    "expires_at": 0,
    "obtained_at": 0,
}

# Lock para evitar múltiplos refreshes simultâneos
_refresh_lock = False


def _load_tokens_from_cache():
    """Carrega tokens do arquivo tokens.json se existir."""
    global _token_cache
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, "r", encoding="utf-8") as f:
                cached = json.load(f)
                # Usar tokens em cache se ainda forem válidos
                if cached.get("expires_at", 0) > time.time():
                    _token_cache.update(cached)
                    print(f"✅ Tokens carregados do cache (expira em {int((cached['expires_at'] - time.time()) / 60)} min)")
                    return True
        except Exception as e:
            print(f"⚠️  Erro ao carregar cache de tokens: {e}")
    return False


def _save_tokens_to_cache():
    """Salva tokens no arquivo tokens.json para persistir entre reinicializações."""
    try:
        with open(TOKENS_FILE, "w", encoding="utf-8") as f:
            json.dump(_token_cache, f, indent=2)
    except Exception as e:
        print(f"⚠️  Erro ao salvar cache de tokens: {e}")


def _refresh_token():
    """Renova o access_token usando o refresh_token."""
    global _refresh_lock, _token_cache
    
    # Evitar múltiplos refreshes simultâneos
    if _refresh_lock:
        print("⏳ Refresh já em progresso, aguardando...")
        wait_time = 0
        while _refresh_lock and wait_time < 30:
            time.sleep(0.1)
            wait_time += 0.1
        return _token_cache["access_token"]
    
    _refresh_lock = True
    try:
        refresh = _token_cache.get("refresh_token")
        if not refresh:
            raise RuntimeError("BLING_REFRESH_TOKEN não configurado no .env.")

        print(f"🔄 Renovando token Bling... ({datetime.now().strftime('%H:%M:%S')})")
        
        r = requests.post(
            TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": refresh},
            auth=(CLIENT_ID, CLIENT_SECRET),
            headers={"Accept": "application/json"},
            timeout=30,
        )
        
        if r.status_code != 200:
            print(f"❌ Erro ao renovar token: {r.status_code} - {r.text}")
            r.raise_for_status()
        
        data = r.json()

        # Atualizar cache
        _token_cache["access_token"] = data["access_token"]
        _token_cache["refresh_token"] = data.get("refresh_token", refresh)
        _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 300  # Renova 5 min antes
        _token_cache["obtained_at"] = time.time()
        
        # Atualizar .env e cache persistente
        _update_env_file(data["access_token"], _token_cache["refresh_token"])
        _save_tokens_to_cache()
        
        expires_in_min = int((data.get("expires_in", 3600)) / 60)
        print(f"✅ Token renovado! Expira em {expires_in_min} minutos ({datetime.now().strftime('%H:%M:%S')})")
        
        return data["access_token"]
        
    except Exception as e:
        print(f"❌ Erro crítico ao renovar token: {e}")
        raise
    finally:
        _refresh_lock = False


def get_token() -> str:
    """Retorna um access_token válido, renovando automaticamente se expirado.
    
    Renova proativamente 5 minutos antes da expiração.
    """
    current_time = time.time()
    expires_at = _token_cache.get("expires_at", 0)
    
    # Se nunca foi inicializado, tentar carregar do cache
    if _token_cache["obtained_at"] == 0:
        _load_tokens_from_cache()
    
    # Renovar se:
    # 1. Ainda não foi obtido
    # 2. Token expirou
    # 3. Token vai expirar em menos de 5 minutos
    if current_time >= expires_at:
        return _refresh_token()
    
    return _token_cache["access_token"]


def get_token_info() -> dict:
    """Retorna informações sobre o token atual."""
    token = _token_cache.get("access_token", "")
    expires_at = _token_cache.get("expires_at", 0)
    current_time = time.time()
    
    if expires_at > current_time:
        time_remaining = expires_at - current_time
        return {
            "status": "✅ Válido",
            "expires_in_seconds": int(time_remaining),
            "expires_in_minutes": int(time_remaining / 60),
            "token": f"{token[:20]}..." if token else "N/A",
        }
    else:
        return {
            "status": "❌ Expirado",
            "expires_in_seconds": 0,
            "expires_in_minutes": 0,
            "token": f"{token[:20]}..." if token else "N/A",
        }


def bling_get(endpoint: str, params: dict = None) -> dict:
    """GET na API do Bling.
    
    Exemplo:
        bling_get("/contatos")
        bling_get("/pedidos/vendas", params={"limite": 10})
    """
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Accept": "application/json",
    }
    r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def bling_post(endpoint: str, payload: dict) -> dict:
    """POST na API do Bling.
    
    Exemplo:
        bling_post("/pedidos/vendas", {"contato": {"id": 123}, ...})
    """
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    r = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def bling_put(endpoint: str, payload: dict) -> dict:
    """PUT na API do Bling.
    
    Exemplo:
        bling_put("/pedidos/vendas/123", {"situacao": {"id": 9}})
    """
    headers = {
        "Authorization": f"Bearer {get_token()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    r = requests.put(f"{BASE_URL}{endpoint}", headers=headers, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()


def _update_env_file(new_access: str, new_refresh: str):
    """Grava os novos tokens no .env local para persistir entre reinicializações."""
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    
    try:
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
            
    except Exception as e:
        print(f"⚠️  Erro ao atualizar .env: {e}")
