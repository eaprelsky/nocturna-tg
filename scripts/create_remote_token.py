"""
Script to create a service token for remote Nocturna API server.

This script helps create a service token when switching from local to remote server.
"""

import requests
import sys
import json
from typing import Optional


def create_service_token(
    api_url: str,
    admin_email: str,
    admin_password: str,
    days: int = 30,
    scope: str = "calculations",
    eternal: bool = False,
) -> Optional[str]:
    """
    Create a service token on remote server.

    Args:
        api_url: Base URL of the API (e.g., https://your-api-server.com/api)
        admin_email: Admin user email
        admin_password: Admin user password
        days: Token expiration in days (ignored if eternal=True)
        scope: Token scope (default: "calculations")
        eternal: Create eternal token (never expires)

    Returns:
        Service token string or None if failed
    """
    api_url = api_url.rstrip("/")

    # Step 1: Login as admin
    print(f"🔐 Logging in as admin: {admin_email}")
    login_url = f"{api_url}/auth/login"
    
    try:
        login_response = requests.post(
            login_url,
            data={
                "username": admin_email,
                "password": admin_password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        login_response.raise_for_status()
        login_data = login_response.json()
        admin_token = login_data.get("access_token")
        
        if not admin_token:
            print("❌ Failed to get admin token from login response")
            print(f"Response: {login_data}")
            return None
        
        print("✅ Admin login successful")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Login failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

    # Step 2: Create service token
    print(f"\n🔑 Creating service token (days={days}, scope={scope}, eternal={eternal})...")
    token_url = f"{api_url}/auth/admin/service-tokens"
    
    try:
        token_response = requests.post(
            token_url,
            json={
                "days": days,
                "scope": scope,
                "eternal": eternal,
            },
            headers={
                "Authorization": f"Bearer {admin_token}",
                "Content-Type": "application/json",
            },
        )
        token_response.raise_for_status()
        token_data = token_response.json()
        service_token = token_data.get("service_token")
        
        if not service_token:
            print("❌ Failed to get service token from response")
            print(f"Response: {token_data}")
            return None
        
        print("✅ Service token created successfully!")
        print(f"\n📋 Token details:")
        print(f"   Token ID: {token_data.get('token_id')}")
        print(f"   Scope: {token_data.get('scope')}")
        print(f"   Expires: {token_data.get('expires_at')}")
        
        print(f"\n🔐 SERVICE TOKEN:")
        print("-" * 80)
        print(service_token)
        print("-" * 80)
        
        print(f"\n💡 Add this to your .env file:")
        print(f"NOCTURNA_SERVICE_TOKEN=\"{service_token}\"")
        
        return service_token
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Token creation failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None


def main():
    """Main function."""
    if len(sys.argv) < 4:
        print("Usage: python create_remote_token.py <api_url> <admin_email> <admin_password> [days] [scope] [eternal]")
        print("\nExample:")
        print("  python create_remote_token.py https://your-api-server.com/api admin@example.com password123")
        print("  python create_remote_token.py https://your-api-server.com/api admin@example.com password123 90")
        print("  python create_remote_token.py https://your-api-server.com/api admin@example.com password123 0 calculations true")
        sys.exit(1)
    
    api_url = sys.argv[1]
    admin_email = sys.argv[2]
    admin_password = sys.argv[3]
    days = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    scope = sys.argv[5] if len(sys.argv) > 5 else "calculations"
    eternal = sys.argv[6].lower() == "true" if len(sys.argv) > 6 else False
    
    token = create_service_token(
        api_url=api_url,
        admin_email=admin_email,
        admin_password=admin_password,
        days=days,
        scope=scope,
        eternal=eternal,
    )
    
    if token:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

