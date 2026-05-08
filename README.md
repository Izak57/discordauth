# discordauth

A simple Discord OAuth2 library for Python, built on top of [httpx](https://www.python-httpx.org/).

## Installation

```bash
pip install discordauth
```

## Quick Start

```python
from discordauth import Application, Endpoint, get_user

# 1. Create an Application with your Discord app credentials
app = Application(id="YOUR_CLIENT_ID", secret="YOUR_CLIENT_SECRET")

# 2. Define an OAuth2 endpoint with the scopes you need
endpoint = Endpoint(app=app, scopes=["identify", "email"], redirect_uri="https://yoursite.com/callback")

# 3. Redirect the user to the authorization URL
print(endpoint.url)

# 4. After the user authorizes, exchange the code for a token
token = endpoint.exchange(code="AUTH_CODE_FROM_DISCORD")

# 5. Fetch the authenticated user's info
user = get_user(token)
print(user.username, user.avatar_url)
```

---

## Models & Types

### `Application`

Represents your Discord application. Pass it to `Endpoint` to authorize users.

| Attribute     | Type            | Description                                               |
|---------------|-----------------|-----------------------------------------------------------|
| `id`          | `str`           | Your Discord application's client ID                      |
| `secret`      | `str`           | Your Discord application's client secret                  |
| `bot_token`   | `str \| None`   | Optional bot token, required for `join_guild`             |

```python
# Basic usage (OAuth2 only)
app = Application(id="123456789", secret="abc123secret")

# With bot token (enables join_guild)
app = Application(id="123456789", secret="abc123secret", bot_token="your.bot.token.here")
```

**Methods**

| Method                                              | Returns | Description                                                         |
|-----------------------------------------------------|---------|---------------------------------------------------------------------|
| `join_guild(guild_id, user_id, access_token)`       | `None`  | Adds a user to a guild. `guild_id` is `int`; `user_id` is `int \| str`. Requires `bot_token` and the `guilds.join` OAuth2 scope. |

```python
# After the user authorizes with the "guilds.join" scope:
token = endpoint.exchange(code="AUTH_CODE")
user  = get_user(token)

app.join_guild(guild_id=123456789, user_id=user.id, access_token=token)
```

---

### `Endpoint`

Represents an OAuth2 authorization endpoint. Generates the redirect URL and exchanges authorization codes for tokens.

| Attribute      | Type            | Description                                         |
|----------------|-----------------|-----------------------------------------------------|
| `app`          | `Application`   | The Discord application credentials                 |
| `scopes`       | `List[str]`     | List of OAuth2 scopes (e.g. `["identify", "email"]`) |
| `redirect_uri` | `str`           | The URI Discord redirects to after authorization    |

**Properties**

| Property | Type  | Description                          |
|----------|-------|--------------------------------------|
| `url`    | `str` | The full Discord authorization URL to redirect the user to |

**Methods**

| Method              | Returns        | Description                                         |
|---------------------|----------------|-----------------------------------------------------|
| `exchange(code)`    | `DiscordToken` | Exchanges an authorization code for an access token |

```python
endpoint = Endpoint(
    app=app,
    scopes=["identify", "guilds"],
    redirect_uri="https://yoursite.com/callback"
)

# Get the URL to redirect users to
auth_url = endpoint.url

# Exchange the code Discord returns after authorization
token = endpoint.exchange(code="returned_code")
```

---

### `DiscordToken`

Holds the OAuth2 token returned by Discord. A Pydantic model.

| Field           | Type            | Description                                      |
|-----------------|-----------------|--------------------------------------------------|
| `access_token`  | `str`           | The bearer access token                          |
| `refresh_token` | `str \| None`   | Token used to get a new access token (may be `None`) |
| `token_type`    | `str`           | Token type (usually `"Bearer"`)                  |
| `expires_in`    | `int`           | Seconds until the token expires                  |
| `scope`         | `str`           | Space-separated string of granted scopes         |

**Properties**

| Property  | Type        | Description                              |
|-----------|-------------|------------------------------------------|
| `scopes`  | `List[str]` | The granted scopes as a list of strings  |

**Methods**

| Method                           | Returns        | Description                              |
|----------------------------------|----------------|------------------------------------------|
| `refresh(httpclient=None)`       | `DiscordToken` | Uses the refresh token to get a new token. Raises `ValueError` if no refresh token is available. |

```python
print(token.access_token)
print(token.scopes)       # ["identify", "guilds"]
print(token.expires_in)   # 604800

# Refresh the token
new_token = token.refresh()
```

---

### `UserInfo`

Represents a Discord user returned by the `/users/@me` endpoint. A Pydantic model.

| Field          | Type           | Description                                |
|----------------|----------------|--------------------------------------------|
| `id`           | `str`          | The user's Discord ID (snowflake)          |
| `username`     | `str`          | The user's username                        |
| `discriminator`| `str`          | The user's legacy discriminator (e.g. `"0"`) |
| `global_name`  | `str \| None`  | The user's display name                    |
| `avatar`       | `str \| None`  | Avatar image hash                          |
| `banner`       | `str \| None`  | Banner image hash                          |
| `accent_color` | `int \| None`  | Profile accent color as an integer         |
| `public_flags` | `int`          | Public user flags bitmask                  |
| `flags`        | `int`          | All user flags bitmask                     |
| `mfa_enabled`  | `bool`         | Whether the user has MFA enabled           |
| `locale`       | `str \| None`  | User's preferred locale (e.g. `"en-US"`)  |
| `premium_type` | `int`          | Nitro subscription type (`0` = none)       |

**Properties**

| Property     | Type           | Description                                            |
|--------------|----------------|--------------------------------------------------------|
| `avatar_url` | `str \| None`  | Full CDN URL of the user's avatar, or `None` if not set |
| `banner_url` | `str \| None`  | Full CDN URL of the user's banner, or `None` if not set |

```python
user = get_user(token)

print(user.id)           # "123456789012345678"
print(user.username)     # "cooluser"
print(user.global_name)  # "Cool User"
print(user.avatar_url)   # "https://cdn.discordapp.com/avatars/.../abc123.png"
print(user.banner_url)   # None (if no banner is set)
```

---

## Functions

### `get_user(token, httpclient=None) -> UserInfo`

Fetches the authenticated user's information from Discord's API.

| Parameter    | Type                    | Description                                           |
|--------------|-------------------------|-------------------------------------------------------|
| `token`      | `DiscordToken \| str`   | A `DiscordToken` object or a raw access token string  |
| `httpclient` | `httpx.Client \| None`  | Optional custom httpx client                          |

```python
from discordauth import get_user

# Using a DiscordToken object
user = get_user(token)

# Using a raw access token string
user = get_user("my_raw_access_token")
```

### `grant_token(grant_type, data, httpclient=None) -> DiscordToken`

Low-level function to request a token from Discord's OAuth2 token endpoint. Prefer using `Endpoint.exchange()` or `DiscordToken.refresh()` instead.

| Parameter    | Type                   | Description                              |
|--------------|------------------------|------------------------------------------|
| `grant_type` | `str`                  | OAuth2 grant type string                 |
| `data`       | `dict`                 | Additional form data for the request     |
| `httpclient` | `httpx.Client \| None` | Optional custom httpx client             |

---

## Full Example — FastAPI Integration

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from discordauth import Application, Endpoint, get_user

app_server = FastAPI()

discord_app = Application(id="YOUR_CLIENT_ID", secret="YOUR_CLIENT_SECRET")
endpoint = Endpoint(
    app=discord_app,
    scopes=["identify", "email"],
    redirect_uri="http://localhost:8000/callback"
)


@app_server.get("/login")
def login():
    return RedirectResponse(endpoint.url)


@app_server.get("/callback")
def callback(code: str):
    token = endpoint.exchange(code=code)
    user = get_user(token)
    return {
        "id": user.id,
        "username": user.username,
        "global_name": user.global_name,
        "avatar_url": user.avatar_url,
        "scopes": token.scopes,
    }
```

---

## Ideas to Make the Module Easier to Use & FastAPI Compatible

### 1. Async support (`AsyncApplication` / async methods)
Add an `AsyncApplication` class (or `async` variants of `exchange`, `get_user`, `join_guild`) backed by `httpx.AsyncClient`. FastAPI is fully async, so avoiding `asyncio.run()` / thread-pool workarounds matters a lot for performance.

### 2. FastAPI dependency helpers
Provide ready-made FastAPI `Depends`-compatible callables, e.g.:

```python
from discordauth.fastapi import DiscordUser

@router.get("/me")
async def me(user: UserInfo = Depends(DiscordUser(endpoint))):
    return user
```

### 3. `state` parameter & CSRF protection
Add an optional `state` parameter to `Endpoint.url` and a `verify_state()` helper so developers can protect their OAuth2 flow against CSRF with minimal boilerplate.

### 4. Token storage / session helpers
Ship a thin wrapper that stores `DiscordToken` in an HTTP-only cookie (or a FastAPI `Request`'s session), with automatic refresh when expired, so callers never touch raw tokens.

### 5. Guild membership helpers
Build on `join_guild` with complementary utilities:
- `get_guilds(token)` – list guilds the user is in.
- `is_member(guild_id, user_id)` – check membership without trying to add.

### 6. Pydantic `Application` model / settings integration
Make `Application` a Pydantic `BaseSettings` subclass so credentials can be loaded automatically from environment variables (`DISCORD_CLIENT_ID`, `DISCORD_CLIENT_SECRET`, `DISCORD_BOT_TOKEN`), which is the standard FastAPI/12-factor pattern.

---

## License

MIT
