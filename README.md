# Discord OAuth2 Library

A simple and elegant Discord OAuth2 library for Python that makes implementing Discord authentication easy and straightforward.

## Features

- 🚀 **Simple API** - Clean and intuitive interface for Discord OAuth2
- 🔐 **Complete OAuth2 Flow** - Handles authorization, token exchange, and user info retrieval
- 📝 **Type Safe** - Full type annotations with Pydantic models
- 🛡️ **Error Handling** - Proper HTTP error handling with informative exceptions
- 📚 **Well Documented** - Comprehensive docstrings and examples
- ⚡ **Modern Python** - Uses modern Python features and async-ready httpx

## Installation

Install the library using pip:

```bash
pip install discordauth
```

## Quick Start

Here's a simple example to get you started with Discord OAuth2:

```python
from discordauth import Application, Endpoint

# 1. Create your Discord application instance
app = Application(
    id="your_discord_client_id",
    secret="your_discord_client_secret"
)

# 2. Create an OAuth2 endpoint
endpoint = Endpoint(
    app=app,
    scopes=["identify"],  # Request permission to identify the user
    redirect_uri="http://localhost:8000/callback"
)

# 3. Get the authorization URL
auth_url = endpoint.url
print(f"Visit this URL to authorize: {auth_url}")

# 4. After user authorizes, exchange the code for a token
# (You'll receive this code in your callback endpoint)
authorization_code = "code_from_discord_callback"
token = endpoint.exchange(authorization_code)

# 5. Get user information
user = endpoint.get_user(token)
print(f"Hello, {user.username}!")
```

## Complete Example: Web Application

Here's a more complete example using Flask:

```python
from flask import Flask, request, redirect, session
from discordauth import Application, Endpoint

app = Flask(__name__)
app.secret_key = "your-secret-key"

# Configure Discord OAuth2
discord_app = Application(
    id="your_discord_client_id",
    secret="your_discord_client_secret"
)

endpoint = Endpoint(
    app=discord_app,
    scopes=["identify", "email"],
    redirect_uri="http://localhost:5000/callback"
)

@app.route("/")
def home():
    if "user" in session:
        return f"Welcome back, {session['user']['username']}!"
    return f'<a href="/login">Login with Discord</a>'

@app.route("/login")
def login():
    return redirect(endpoint.url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization failed", 400
    
    try:
        # Exchange code for token
        token = endpoint.exchange(code)
        
        # Get user information
        user = endpoint.get_user(token)
        
        # Store user info in session
        session["user"] = {
            "id": user.id,
            "username": user.username,
            "avatar_url": user.avatar_url
        }
        
        return redirect("/")
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)
```

## Available Scopes

Discord provides several OAuth2 scopes that determine what information and actions your application can access:

| Scope | Description |
|-------|-------------|
| `identify` | Access to user's basic account info (username, avatar, etc.) |
| `email` | Access to user's email address |
| `guilds` | Access to user's guilds (servers) |
| `guilds.join` | Ability to join guilds on behalf of the user |
| `guilds.members.read` | Access to guild member information |
| `connections` | Access to user's connected accounts |
| `role_connections.write` | Ability to update role connection metadata |

## API Reference

### Application

Represents a Discord application with authentication credentials.

```python
app = Application(id="client_id", secret="client_secret")
```

**Parameters:**
- `id` (str): Your Discord application's client ID
- `secret` (str): Your Discord application's client secret

### Endpoint

Manages the OAuth2 flow and API requests.

```python
endpoint = Endpoint(app, scopes, redirect_uri)
```

**Parameters:**
- `app` (Application): Your Discord application instance
- `scopes` (List[str]): List of OAuth2 scopes to request
- `redirect_uri` (str): Where Discord redirects after authorization

**Methods:**

#### `endpoint.url`
Returns the authorization URL for users to visit.

#### `endpoint.exchange(code: str) -> DiscordToken`
Exchanges an authorization code for an access token.

#### `endpoint.get_user(token: DiscordToken) -> UserInfo`
Retrieves user information using an access token.

### UserInfo

Contains Discord user information with convenient properties.

**Key Properties:**
- `id`: User's Discord ID
- `username`: User's username
- `global_name`: User's display name
- `avatar_url`: URL to user's avatar image
- `banner_url`: URL to user's banner image (Nitro only)
- `premium_type`: User's Nitro subscription level

### DiscordToken

Contains OAuth2 token information.

**Properties:**
- `access_token`: The access token for API requests
- `expires_in`: Token lifetime in seconds
- `scopes`: List of granted scopes

## Error Handling

The library raises `httpx.HTTPStatusError` for API errors. Always wrap API calls in try-catch blocks:

```python
try:
    token = endpoint.exchange(code)
    user = endpoint.get_user(token)
except httpx.HTTPStatusError as e:
    print(f"API Error: {e.response.status_code} - {e.response.text}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Common Error Codes

| Status Code | Meaning |
|-------------|---------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid token or credentials |
| 403 | Forbidden - Missing required scope |
| 429 | Rate Limited - Too many requests |
| 500 | Internal Server Error - Discord API issue |

## Setting Up Your Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "OAuth2" section
4. Add your redirect URIs under "Redirects"
5. Copy your Client ID and Client Secret
6. Select the required scopes for your application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Discord API Documentation](https://discord.com/developers/docs/topics/oauth2)
2. Open an issue on GitHub
3. Make sure your Discord application is properly configured

## Changelog

### Version 0.1.0
- Initial release
- Basic OAuth2 flow implementation
- User information retrieval
- Type-safe models with Pydantic