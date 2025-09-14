#!/usr/bin/env python3
"""
Basic Discord OAuth2 Example

This example demonstrates the fundamental usage of the discordauth library.
It shows how to create an application, set up an endpoint, and handle the
OAuth2 flow step by step.

Prerequisites:
- A Discord application created at https://discord.com/developers/applications
- Your client ID and secret from the Discord Developer Portal
- A redirect URI configured in your Discord application

Usage:
    python basic_usage.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from discordauth import Application, Endpoint
import webbrowser
import sys


def main():
    # Replace these with your actual Discord application credentials
    CLIENT_ID = "your_discord_client_id_here"
    CLIENT_SECRET = "your_discord_client_secret_here"
    REDIRECT_URI = "http://localhost:8000/callback"
    
    print("=== Discord OAuth2 Basic Example ===\n")
    
    # Step 1: Create Discord application instance
    print("1. Creating Discord application instance...")
    app = Application(id=CLIENT_ID, secret=CLIENT_SECRET)
    print(f"   ✓ Application created with ID: {CLIENT_ID}")
    
    # Step 2: Create OAuth2 endpoint
    print("\n2. Setting up OAuth2 endpoint...")
    endpoint = Endpoint(
        app=app,
        scopes=["identify"],  # Basic user identification
        redirect_uri=REDIRECT_URI
    )
    print(f"   ✓ Endpoint created with redirect URI: {REDIRECT_URI}")
    print(f"   ✓ Requested scopes: {endpoint.scopes}")
    
    # Step 3: Generate authorization URL
    print("\n3. Generating authorization URL...")
    auth_url = endpoint.url
    print(f"   ✓ Authorization URL: {auth_url}")
    
    # Step 4: User authorization (simulated)
    print("\n4. User Authorization Process:")
    print("   In a real application, you would:")
    print("   a) Redirect the user to the authorization URL")
    print("   b) User grants permission on Discord")
    print("   c) Discord redirects back with an authorization code")
    print("   d) Your app exchanges the code for a token")
    
    # Open the authorization URL in the browser (optional)
    try:
        response = input("\n   Would you like to open the auth URL in your browser? (y/n): ")
        if response.lower() == 'y':
            webbrowser.open(auth_url)
            print("   ✓ Authorization URL opened in browser")
    except KeyboardInterrupt:
        print("\n   Operation cancelled by user")
        sys.exit(0)
    
    # Step 5: Token exchange example (simulated)
    print("\n5. Token Exchange (Example):")
    print("   After receiving the authorization code from Discord, you would:")
    print("   ```python")
    print("   try:")
    print("       token = endpoint.exchange(authorization_code)")
    print("       print(f'Token received! Expires in {token.expires_in} seconds')")
    print("       print(f'Granted scopes: {token.scopes}')")
    print("   except Exception as e:")
    print("       print(f'Token exchange failed: {e}')")
    print("   ```")
    
    # Step 6: User info retrieval example (simulated)
    print("\n6. User Information Retrieval (Example):")
    print("   With a valid token, you can get user information:")
    print("   ```python")
    print("   try:")
    print("       user = endpoint.get_user(token)")
    print("       print(f'Welcome, {user.username}!')")
    print("       print(f'User ID: {user.id}')")
    print("       print(f'Display name: {user.global_name}')")
    print("       if user.avatar_url:")
    print("           print(f'Avatar: {user.avatar_url}')")
    print("   except Exception as e:")
    print("       print(f'Failed to get user info: {e}')")
    print("   ```")
    
    print("\n=== Example Complete ===")
    print("\nNext steps:")
    print("1. Replace CLIENT_ID and CLIENT_SECRET with your actual values")
    print("2. Configure your redirect URI in the Discord Developer Portal")
    print("3. Implement the callback endpoint to handle the authorization code")
    print("4. See flask_example.py for a complete web application implementation")


if __name__ == "__main__":
    main()