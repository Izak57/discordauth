#!/usr/bin/env python3
"""
Flask Web Application Example with Discord OAuth2

This example demonstrates a complete web application using Flask and the
discordauth library. It includes login, logout, session management, and
user profile display.

Prerequisites:
- Flask: pip install flask
- A Discord application created at https://discord.com/developers/applications
- Redirect URI set to: http://localhost:5000/auth/callback

Usage:
    python flask_example.py

Then visit: http://localhost:5000
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from flask import Flask, request, redirect, session, render_template_string, url_for
except ImportError:
    print("Flask is required for this example. Install it with: pip install flask")
    exit(1)

from discordauth import Application, Endpoint
import os
from typing import Optional


# Configuration
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "your_discord_client_id_here")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "your_discord_client_secret_here")
REDIRECT_URI = "http://localhost:5000/auth/callback"
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")

# Flask app setup
app = Flask(__name__)
app.secret_key = SECRET_KEY

# Discord OAuth2 setup
discord_app = Application(id=CLIENT_ID, secret=CLIENT_SECRET)
discord_endpoint = Endpoint(
    app=discord_app,
    scopes=["identify", "email"],  # Request user info and email
    redirect_uri=REDIRECT_URI
)

# HTML Templates
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Discord OAuth2 Example</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .user-card { border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .avatar { width: 64px; height: 64px; border-radius: 50%; }
        .login-btn { background: #5865F2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
        .logout-btn { background: #ed4245; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; }
        .scope-badge { background: #57F287; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; margin: 2px; }
    </style>
</head>
<body>
    <h1>Discord OAuth2 Example</h1>
    
    {% if user %}
        <div class="user-card">
            <h2>Welcome, {{ user.username }}!</h2>
            {% if user.avatar_url %}
                <img src="{{ user.avatar_url }}" alt="Avatar" class="avatar">
            {% endif %}
            
            <p><strong>User ID:</strong> {{ user.id }}</p>
            <p><strong>Username:</strong> {{ user.username }}#{{ user.discriminator }}</p>
            {% if user.global_name %}
                <p><strong>Display Name:</strong> {{ user.global_name }}</p>
            {% endif %}
            {% if user.email %}
                <p><strong>Email:</strong> {{ user.email }}</p>
            {% endif %}
            <p><strong>Premium Type:</strong> 
                {% if user.premium_type == 0 %}None
                {% elif user.premium_type == 1 %}Nitro Classic
                {% elif user.premium_type == 2 %}Nitro
                {% else %}{{ user.premium_type }}
                {% endif %}
            </p>
            <p><strong>2FA Enabled:</strong> {{ "Yes" if user.mfa_enabled else "No" }}</p>
            
            {% if granted_scopes %}
                <p><strong>Granted Scopes:</strong> 
                {% for scope in granted_scopes %}
                    <span class="scope-badge">{{ scope }}</span>
                {% endfor %}
                </p>
            {% endif %}
            
            <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
        </div>
    {% else %}
        <p>You are not logged in.</p>
        <a href="{{ url_for('login') }}" class="login-btn">Login with Discord</a>
        
        <h2>How it works:</h2>
        <ol>
            <li>Click "Login with Discord" to start the OAuth2 flow</li>
            <li>You'll be redirected to Discord to authorize the application</li>
            <li>After authorization, you'll be redirected back here with your profile info</li>
            <li>The app requests the 'identify' and 'email' scopes</li>
        </ol>
    {% endif %}
    
    <h2>Example Features:</h2>
    <ul>
        <li>✅ Discord OAuth2 authentication</li>
        <li>✅ User profile display</li>
        <li>✅ Session management</li>
        <li>✅ Proper error handling</li>
        <li>✅ Scope demonstration</li>
    </ul>
</body>
</html>
"""

ERROR_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Error - Discord OAuth2 Example</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .error { background: #fed7d7; border: 1px solid #fc8181; padding: 20px; border-radius: 8px; color: #c53030; }
    </style>
</head>
<body>
    <h1>Authentication Error</h1>
    <div class="error">
        <p><strong>{{ error_type }}:</strong> {{ error_message }}</p>
    </div>
    <p><a href="{{ url_for('home') }}">← Back to Home</a></p>
</body>
</html>
"""


@app.route("/")
def home():
    """Home page showing login status and user info."""
    user_data = session.get("user")
    granted_scopes = session.get("scopes", [])
    
    return render_template_string(
        HOME_TEMPLATE, 
        user=user_data, 
        granted_scopes=granted_scopes
    )


@app.route("/login")
def login():
    """Redirect user to Discord OAuth2 authorization."""
    return redirect(discord_endpoint.url)


@app.route("/auth/callback")
def auth_callback():
    """Handle OAuth2 callback from Discord."""
    # Check for authorization code
    code = request.args.get("code")
    error = request.args.get("error")
    
    if error:
        return render_template_string(
            ERROR_TEMPLATE,
            error_type="Authorization Error",
            error_message=f"User denied authorization: {error}"
        ), 400
    
    if not code:
        return render_template_string(
            ERROR_TEMPLATE,
            error_type="Missing Code",
            error_message="No authorization code received from Discord"
        ), 400
    
    try:
        # Exchange code for token
        token = discord_endpoint.exchange(code)
        
        # Get user information
        user = discord_endpoint.get_user(token)
        
        # Store user info and scopes in session
        session["user"] = {
            "id": user.id,
            "username": user.username,
            "discriminator": user.discriminator,
            "global_name": user.global_name,
            "avatar_url": user.avatar_url,
            "banner_url": user.banner_url,
            "premium_type": user.premium_type,
            "mfa_enabled": user.mfa_enabled,
            "locale": user.locale,
        }
        session["scopes"] = token.scopes
        
        # Add email if available (requires email scope)
        if "email" in token.scopes:
            # Note: The basic get_user endpoint doesn't return email
            # You would need to make a separate request to get email
            # This is just for demonstration
            session["user"]["email"] = "Email scope granted (see Discord API docs for implementation)"
        
        return redirect(url_for("home"))
        
    except Exception as e:
        return render_template_string(
            ERROR_TEMPLATE,
            error_type="API Error",
            error_message=f"Failed to complete authentication: {str(e)}"
        ), 500


@app.route("/logout")
def logout():
    """Clear session and redirect to home."""
    session.clear()
    return redirect(url_for("home"))


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template_string(
        ERROR_TEMPLATE,
        error_type="Page Not Found",
        error_message="The requested page could not be found."
    ), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template_string(
        ERROR_TEMPLATE,
        error_type="Internal Server Error",
        error_message="An unexpected error occurred."
    ), 500


if __name__ == "__main__":
    print("=== Discord OAuth2 Flask Example ===")
    print(f"Starting server at http://localhost:5000")
    print(f"Make sure your Discord app redirect URI is set to: {REDIRECT_URI}")
    print(f"Client ID: {CLIENT_ID}")
    print("Press Ctrl+C to stop the server")
    
    if CLIENT_ID == "your_discord_client_id_here":
        print("\n⚠️  WARNING: Please set your Discord client ID and secret!")
        print("   Either set environment variables or edit the script:")
        print("   export DISCORD_CLIENT_ID=your_actual_client_id")
        print("   export DISCORD_CLIENT_SECRET=your_actual_client_secret")
        print()
    
    app.run(debug=True, port=5000)