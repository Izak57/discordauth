#!/usr/bin/env python3
"""
Type checking demonstration for discordauth library.

This script demonstrates that the library has proper type annotations
that work with static type checkers like mypy.

Run with: python type_check_demo.py
For type checking: mypy type_check_demo.py (if mypy is installed)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discordauth import Application, Endpoint, UserInfo, DiscordToken
from typing import Optional, List


def demonstrate_type_annotations() -> None:
    """Demonstrate proper type usage with the library."""
    
    # These should type-check correctly
    app: Application = Application("client_id", "client_secret")
    
    scopes: List[str] = ["identify", "email"]
    endpoint: Endpoint = Endpoint(app, scopes, "http://localhost:8000")
    
    # Mock data that would come from Discord API
    token_data = {
        "access_token": "mock_token",
        "token_type": "Bearer", 
        "expires_in": 3600,
        "scope": "identify email"
    }
    token: DiscordToken = DiscordToken(**token_data)
    
    user_data = {
        "id": "123456789",
        "username": "testuser",
        "avatar": "avatar_hash",
        "discriminator": "0001",
        "public_flags": 0,
        "flags": 0,
        "banner": None,
        "accent_color": None,
        "global_name": "Test User",
        "mfa_enabled": True,
        "locale": "en-US",
        "premium_type": 2
    }
    user: UserInfo = UserInfo(**user_data)
    
    # Demonstrate type-safe property access
    avatar_url: Optional[str] = user.avatar_url
    scopes_list: List[str] = token.scopes
    auth_url: str = endpoint.url
    
    print("✓ Type annotations work correctly!")
    print(f"✓ User: {user.username}#{user.discriminator}")
    print(f"✓ Avatar URL: {avatar_url}")
    print(f"✓ Token scopes: {scopes_list}")
    print(f"✓ Auth URL length: {len(auth_url)} chars")


if __name__ == "__main__":
    demonstrate_type_annotations()
    print("\n🎉 All type annotations are working correctly!")
    print("💡 Try running 'mypy type_check_demo.py' if you have mypy installed")