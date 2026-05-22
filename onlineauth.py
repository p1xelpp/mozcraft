# onlineauth.py
# Handles online-mode authentication for Minecraft

import os
import json
import requests
import uuid as uuid_lib
from datetime import datetime
from urllib.parse import urlencode

def get_microsoft_token(username: str = None, password: str = None) -> dict:
    """
    Authenticate with Microsoft and get Minecraft auth token.
    Uses Microsoft OAuth2 Device Flow for browser-based login.
    Returns dict with access_token, uuid, username.
    """
    try:
        print("\n=== Microsoft OAuth2 Authentication ===")
        print("Opening Microsoft login in your default browser...")
        
        # Step 1: Start device flow
        device_flow_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode"
        device_flow_data = {
            "client_id": "00000000402b5328",  # Minecraft Launcher client ID
            "scope": "XboxLive.signin",
        }
        
        device_response = requests.post(device_flow_url, data=device_flow_data, timeout=10)
        if device_response.status_code != 200:
            print(f"ERROR: Device flow failed: {device_response.text}")
            return None
        
        device_data = device_response.json()
        user_code = device_data.get("user_code")
        device_code = device_data.get("device_code")
        
        if not user_code or not device_code:
            print("ERROR: Failed to get device code")
            return None
        
        print(f"\nPlease visit: {device_data.get('verification_uri')}")
        print(f"Enter code: {user_code}\n")
        input("Press Enter after you've completed login in the browser...")
        
        # Step 2: Poll for token
        token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
        token_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": "00000000402b5328",
            "device_code": device_code,
        }
        
        max_attempts = 60
        for attempt in range(max_attempts):
            token_response = requests.post(token_url, data=token_data, timeout=10)
            token_json = token_response.json()
            
            if token_response.status_code == 200 and "access_token" in token_json:
                break
            elif token_json.get("error") == "authorization_pending":
                if attempt % 5 == 0:
                    print(f"Waiting for authorization... ({attempt}s)")
                requests.adapters.DEFAULT_RETRIES = requests.packages.urllib3.util.retry.Retry()
                continue
            else:
                print(f"ERROR: Token request failed: {token_json}")
                return None
        
        if "access_token" not in token_json:
            print("ERROR: Failed to get access token")
            return None
        
        ms_token = token_json.get("access_token")
        
        # Step 3: Authenticate with Xbox Live
        xbox_auth_url = "https://user.auth.xboxlive.com/user/authenticate"
        xbox_payload = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f"d={ms_token}"
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }
        
        xbox_response = requests.post(xbox_auth_url, json=xbox_payload, timeout=10)
        if xbox_response.status_code != 200:
            print(f"ERROR: Xbox auth failed: {xbox_response.text}")
            return None
        
        xbox_data = xbox_response.json()
        xbox_token = xbox_data.get("Token")
        xbox_uhs = xbox_data.get("DisplayClaims", {}).get("xui", [{}])[0].get("uhs")
        
        if not xbox_token or not xbox_uhs:
            print("ERROR: Failed to get Xbox token")
            return None
        
        # Step 4: Get XBox XSTS token
        xsts_auth_url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        xsts_payload = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [xbox_token]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }
        
        xsts_response = requests.post(xsts_auth_url, json=xsts_payload, timeout=10)
        if xsts_response.status_code != 200:
            print(f"ERROR: XSTS auth failed: {xsts_response.text}")
            return None
        
        xsts_data = xsts_response.json()
        xsts_token = xsts_data.get("Token")
        
        if not xsts_token:
            print("ERROR: Failed to get XSTS token")
            return None
        
        # Step 5: Authenticate with Minecraft services
        mc_auth_url = "https://api.minecraftservices.com/authentication/login_with_xbox"
        mc_payload = {
            "identityToken": f"XBL3.0 x={xbox_uhs};{xsts_token}"
        }
        
        mc_response = requests.post(mc_auth_url, json=mc_payload, timeout=10)
        if mc_response.status_code != 200:
            print(f"ERROR: Minecraft auth failed: {mc_response.text}")
            return None
        
        mc_data = mc_response.json()
        access_token = mc_data.get("access_token")
        
        if not access_token:
            print("ERROR: Failed to get Minecraft access token")
            return None
        
        # Step 6: Get player profile
        profile_url = "https://api.minecraftservices.com/minecraft/profile"
        profile_response = requests.get(profile_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
        
        if profile_response.status_code != 200:
            print(f"ERROR: Profile fetch failed: {profile_response.text}")
            return None
        
        profile_data = profile_response.json()
        player_uuid = profile_data.get("id")
        player_name = profile_data.get("name")
        
        if not player_uuid or not player_name:
            print("ERROR: Failed to get player profile")
            return None
        
        print(f"Successfully authenticated as: {player_name}")
        
        return {
            "access_token": access_token,
            "uuid": player_uuid,
            "username": player_name,
            "user_type": "msa"
        }
        
    except Exception as e:
        print(f"ERROR: Microsoft auth failed: {e}")
        return None

def get_legacy_mojang_token(username: str, password: str) -> dict:
    """
    Authenticate with legacy Mojang servers (deprecated but kept for reference).
    Returns dict with access_token, uuid, username.
    """
    try:
        # Mojang auth endpoint (deprecated)
        auth_url = "https://authserver.mojang.com/authenticate"
        
        payload = {
            "agent": {
                "name": "Minecraft",
                "version": 1
            },
            "username": username,
            "password": password,
            "requestUser": True
        }
        
        response = requests.post(auth_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "access_token": data.get("accessToken"),
                "uuid": data.get("selectedProfile", {}).get("id"),
                "username": data.get("selectedProfile", {}).get("name"),
                "user_type": "mojang"
            }
        else:
            print(f"ERROR: Mojang auth failed with status {response.status_code}")
            return None
    except Exception as e:
        print(f"ERROR: Failed to authenticate with Mojang: {e}")
        return None

def load_cached_auth() -> dict:
    """
    Load previously cached auth token if available.
    """
    cache_file = os.path.join(os.path.dirname(__file__), ".auth_cache.json")
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cache = json.load(f)
                # Check if token is still valid (simple check)
                if cache.get("access_token"):
                    print(f"Loaded cached auth for: {cache.get('username')}")
                    return cache
        except:
            pass
    
    return None

def save_auth_cache(auth_data: dict) -> None:
    """
    Cache auth token locally for faster login next time.
    """
    cache_file = os.path.join(os.path.dirname(__file__), ".auth_cache.json")
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(auth_data, f)
        os.chmod(cache_file, 0o600)  # Restrict file permissions
        print(f"Cached auth token")
    except Exception as e:
        print(f"WARNING: Could not cache auth: {e}")

def apply_online_auth(values: dict, use_cache: bool = True) -> dict:
    """
    Apply online-mode authentication to launcher values.
    Uses Microsoft OAuth2 by default, with caching support.
    
    Args:
        values: Dict of launcher argument values
        use_cache: Whether to use cached auth token if available
    
    Returns:
        Updated values dict with auth info, or None if auth failed
    """
    
    # Try cached auth first
    if use_cache:
        cached = load_cached_auth()
        if cached:
            values["auth_player_name"] = cached.get("username", "Steve")
            values["auth_uuid"] = cached.get("uuid", "00000000-0000-0000-0000-000000000000")
            values["auth_access_token"] = cached.get("access_token", "0")
            values["user_type"] = cached.get("user_type", "msa")
            return values
    
    # Try Microsoft auth first (modern accounts)
    print("\nAttempting Microsoft authentication...")
    auth_data = get_microsoft_token(None, None)
    
    if auth_data:
        save_auth_cache(auth_data)
        values["auth_player_name"] = auth_data.get("username", "Steve")
        values["auth_uuid"] = auth_data.get("uuid", "00000000-0000-0000-0000-000000000000")
        values["auth_access_token"] = auth_data.get("access_token", "0")
        values["user_type"] = auth_data.get("user_type", "msa")
        return values
    
    # Fallback to legacy Mojang auth
    print("\nMicrosoft auth failed. Trying legacy Mojang authentication...")
    print("Enter Mojang credentials (for old accounts only):")
    username = input("Enter email or username: ").strip()
    
    if not username:
        print("ERROR: Username/email required for online mode")
        return None
    
    password = input("Enter password (will not be shown): ").strip()
    
    if not password:
        print("ERROR: Password required for online mode")
        return None
    
    auth_data = get_legacy_mojang_token(username, password)
    
    if not auth_data:
        print("ERROR: Authentication failed. Check credentials.")
        return None
    
    save_auth_cache(auth_data)
    values["auth_player_name"] = auth_data.get("username", "Steve")
    values["auth_uuid"] = auth_data.get("uuid", "00000000-0000-0000-0000-000000000000")
    values["auth_access_token"] = auth_data.get("access_token", "0")
    values["user_type"] = auth_data.get("user_type", "msa")
    
    print(f"Successfully logged in as: {values['auth_player_name']}")
    
    return values

def clear_auth_cache() -> None:
    """
    Clear the cached auth token.
    """
    cache_file = os.path.join(os.path.dirname(__file__), ".auth_cache.json")
    if os.path.exists(cache_file):
        os.remove(cache_file)
        print("Cleared cached authentication")
