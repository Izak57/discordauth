# Discord OAuth2 Examples

This directory contains practical examples demonstrating how to use the `discordauth` library in various scenarios.

## Examples Overview

### 1. `basic_usage.py` - Getting Started
**Best for:** First-time users, understanding the OAuth2 flow

A step-by-step walkthrough of the basic Discord OAuth2 process:
- Creating an Application instance
- Setting up an Endpoint
- Generating authorization URLs
- Token exchange concepts
- User information retrieval

```bash
python basic_usage.py
```

**Features:**
- Detailed explanations of each step
- Interactive browser opening (optional)
- Code examples for token exchange and user info
- Clear next-step guidance

### 2. `flask_example.py` - Complete Web Application
**Best for:** Building web applications with user authentication

A full-featured Flask web application demonstrating:
- Complete OAuth2 flow implementation
- Session management
- User profile display
- Error handling and user feedback
- Multiple scope requests

```bash
pip install flask
python flask_example.py
```

Then visit: http://localhost:5000

**Features:**
- ✅ Login/logout functionality
- ✅ User profile display with avatar
- ✅ Session management
- ✅ Error handling with user-friendly messages
- ✅ Responsive HTML interface
- ✅ Scope demonstration (identify + email)

### 3. `advanced_example.py` - Production-Ready Patterns
**Best for:** Production applications, advanced error handling

Advanced patterns and best practices:
- Retry logic with exponential backoff
- Comprehensive error handling
- Token validation and expiration checking
- Scope validation and descriptions
- Structured logging
- Input validation

```bash
python advanced_example.py
```

**Features:**
- ✅ Robust error handling
- ✅ Retry mechanisms
- ✅ Token validation
- ✅ Scope management
- ✅ Production-ready patterns
- ✅ Comprehensive logging

## Prerequisites

### Discord Application Setup
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to OAuth2 settings
4. Add redirect URIs:
   - For basic example: `http://localhost:8000/callback`
   - For Flask example: `http://localhost:5000/auth/callback`
5. Copy your Client ID and Client Secret

### Environment Setup
```bash
# Install required dependencies
pip install discordauth

# For Flask example
pip install flask

# Set your Discord credentials (recommended)
export DISCORD_CLIENT_ID="your_client_id_here"
export DISCORD_CLIENT_SECRET="your_client_secret_here"
```

## Common Scopes

| Scope | Description | Example Use Case |
|-------|-------------|------------------|
| `identify` | Basic user info | User profiles, authentication |
| `email` | User's email address | Account linking, communication |
| `guilds` | List of user's servers | Server-specific features |
| `guilds.join` | Join servers on behalf of user | Auto-join functionality |
| `connections` | Linked accounts (Steam, YouTube, etc.) | Social features |

## Error Handling Examples

### Basic Error Handling
```python
try:
    token = endpoint.exchange(code)
    user = endpoint.get_user(token)
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("Invalid token or credentials")
    elif e.response.status_code == 403:
        print("Missing required scope")
    else:
        print(f"API Error: {e.response.status_code}")
```

### Advanced Error Handling
```python
from advanced_example import AdvancedDiscordAuth

auth = AdvancedDiscordAuth(client_id, client_secret, redirect_uri)
endpoint = auth.create_endpoint(["identify"])

# With retry logic
token = auth.exchange_with_retry(endpoint, code, max_retries=3)
if token and auth.validate_token(token):
    user = auth.get_user_with_validation(endpoint, token)
```

## Security Considerations

### Production Checklist
- [ ] Use HTTPS for redirect URIs
- [ ] Store client secret securely (environment variables)
- [ ] Implement proper session management
- [ ] Add CSRF protection
- [ ] Validate all user inputs
- [ ] Use secure session cookies
- [ ] Implement rate limiting
- [ ] Log security events

### Example Secure Configuration
```python
# Use environment variables
import os
CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")

# Secure Flask settings
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JS access
    SESSION_COOKIE_SAMESITE='Lax'  # CSRF protection
)
```

## Next Steps

1. **Start with `basic_usage.py`** to understand the fundamentals
2. **Try `flask_example.py`** for a complete web application
3. **Study `advanced_example.py`** for production patterns
4. **Build your own application** using these patterns
5. **Review the main library documentation** in the parent README

## Getting Help

- Check the main README.md for API documentation
- Review the Discord API documentation
- Open an issue on GitHub for bugs or questions
- Make sure your Discord application is properly configured