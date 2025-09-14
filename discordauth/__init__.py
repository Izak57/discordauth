"""
Discord OAuth2 library for easy authentication and user information retrieval.

This module provides a simple interface for implementing Discord OAuth2 authentication
in your applications. It handles the complete OAuth2 flow including authorization URL
generation, token exchange, and user information retrieval.

Example:
    Basic usage of the Discord OAuth2 library:

    ```python
    from discordauth import Application, Endpoint

    # Create an application instance
    app = Application("your_client_id", "your_client_secret")
    
    # Create an endpoint for OAuth2 flow
    endpoint = Endpoint(app, ["identify"], "http://localhost:8000/callback")
    
    # Get authorization URL
    auth_url = endpoint.url
    
    # After user authorizes, exchange code for token
    token = endpoint.exchange(authorization_code)
    
    # Get user information
    user = endpoint.get_user(token)
    print(f"Hello, {user.username}!")
    ```
"""

from typing import LiteralString, Optional, List
from urllib.parse import urlencode
from httpx import Client
from pydantic import BaseModel


class Application:
    """
    Represents a Discord application with authentication credentials.
    
    This class manages the Discord application credentials and provides an HTTP client
    for making requests to Discord's API. It automatically sets appropriate headers
    for Discord API interactions.
    
    Attributes:
        id (str): The Discord application's client ID.
        secret (str): The Discord application's client secret.
        client (Client): HTTP client configured for Discord API requests.
    
    Example:
        Creating a Discord application instance:
        
        ```python
        app = Application("123456789012345678", "your_client_secret_here")
        ```
    """

    def __init__(self, id: str, secret: str) -> None:
        """
        Initialize a Discord application instance.
        
        Args:
            id (str): The Discord application's client ID. You can find this in your
                     Discord Developer Portal under your application's "General Information".
            secret (str): The Discord application's client secret. This is sensitive
                         information and should be kept secure.
        
        Example:
            ```python
            app = Application("123456789012345678", "abcdef123456789")
            ```
        """
        self.id = id
        self.secret = secret
        self.client = Client()
        self.client.headers.update({
            "User-Agent": "DiscordOauth"
        })



class UserInfo(BaseModel):
    """
    Represents Discord user information returned from the API.
    
    This model contains all the user data available through Discord's OAuth2 API
    when using the 'identify' scope. It provides convenient properties for accessing
    user avatar and banner URLs.
    
    Attributes:
        id (str): The user's unique Discord ID.
        username (str): The user's Discord username.
        avatar (str | None): The user's avatar hash, or None if no avatar is set.
        discriminator (str): The user's discriminator (e.g., "0001").
        public_flags (int): The user's public flags bitmask.
        flags (int): The user's flags bitmask.
        banner (str | None): The user's banner hash, or None if no banner is set.
        accent_color (int | None): The user's accent color as an integer, or None.
        global_name (str | None): The user's global display name, or None.
        mfa_enabled (bool): Whether the user has two-factor authentication enabled.
        locale (str | None): The user's locale/language preference.
        premium_type (int): The user's Nitro subscription type (0=None, 1=Classic, 2=Nitro).
    
    Example:
        Accessing user information:
        
        ```python
        user = endpoint.get_user(token)
        print(f"User: {user.username}#{user.discriminator}")
        print(f"Display name: {user.global_name}")
        print(f"Avatar URL: {user.avatar_url}")
        print(f"Has Nitro: {user.premium_type > 0}")
        ```
    """
    id: str
    username: str
    avatar: Optional[str]
    discriminator: str
    public_flags: int
    flags: int
    banner: Optional[str]
    accent_color: Optional[int]
    global_name: Optional[str]
    mfa_enabled: bool
    locale: Optional[str]
    premium_type: int

    @property
    def avatar_url(self) -> Optional[str]:
        """
        Get the full URL for the user's avatar image.
        
        Returns:
            str | None: The full Discord CDN URL for the user's avatar in PNG format,
                       or None if the user has no avatar set.
        
        Example:
            ```python
            user = endpoint.get_user(token)
            if user.avatar_url:
                print(f"Download avatar from: {user.avatar_url}")
            else:
                print("User has no custom avatar")
            ```
        """
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return None

    @property
    def banner_url(self) -> Optional[str]:
        """
        Get the full URL for the user's banner image.
        
        Returns:
            str | None: The full Discord CDN URL for the user's banner in PNG format,
                       or None if the user has no banner set.
        
        Note:
            User banners are only available to Discord Nitro subscribers.
        
        Example:
            ```python
            user = endpoint.get_user(token)
            if user.banner_url:
                print(f"Download banner from: {user.banner_url}")
            else:
                print("User has no banner (or no Nitro)")
            ```
        """
        if self.banner:
            return f"https://cdn.discordapp.com/banners/{self.id}/{self.banner}.png"
        return None



class DiscordToken(BaseModel):
    """
    Represents an OAuth2 access token returned by Discord.
    
    This model contains the access token and related information needed to make
    authenticated requests to Discord's API on behalf of a user.
    
    Attributes:
        access_token (str): The OAuth2 access token for API requests.
        token_type (str): The type of token (typically "Bearer").
        expires_in (int): Token lifetime in seconds from when it was issued.
        scope (str): Space-separated string of granted scopes.
    
    Example:
        Using a Discord token:
        
        ```python
        token = endpoint.exchange(code)
        print(f"Token expires in {token.expires_in} seconds")
        print(f"Granted scopes: {', '.join(token.scopes)}")
        
        # Use token to get user info
        user = endpoint.get_user(token)
        ```
    """
    access_token: str
    token_type: str
    expires_in: int
    scope: str

    @property
    def scopes(self) -> List[str]:
        """
        Get the list of scopes granted to this token.
        
        Returns:
            List[str]: A list of scope strings that were granted during authorization.
        
        Example:
            ```python
            token = endpoint.exchange(code)
            if "identify" in token.scopes:
                print("Can access user info")
            if "email" in token.scopes:
                print("Can access user email")
            ```
        """
        return self.scope.split(" ")



class Endpoint:
    """
    Manages Discord OAuth2 authentication flow and API requests.
    
    This class handles the complete OAuth2 flow including generating authorization URLs,
    exchanging authorization codes for access tokens, and making authenticated API requests
    to retrieve user information.
    
    Attributes:
        app (Application): The Discord application instance with credentials.
        scopes (List[LiteralString]): List of OAuth2 scopes to request.
        redirect_uri (str): The URI where Discord will redirect after authorization.
    
    Example:
        Complete OAuth2 flow:
        
        ```python
        # Setup
        app = Application("client_id", "client_secret")
        endpoint = Endpoint(app, ["identify", "email"], "http://localhost:8000/callback")
        
        # Step 1: Get authorization URL
        auth_url = endpoint.url
        print(f"Visit: {auth_url}")
        
        # Step 2: User visits URL, authorizes, gets redirected with code
        # Step 3: Exchange code for token
        token = endpoint.exchange("received_authorization_code")
        
        # Step 4: Get user information
        user = endpoint.get_user(token)
        ```
    """

    def __init__(self,
                 app: Application,
                 scopes: List[LiteralString],
                 redirect_uri: str) -> None:
        """
        Initialize an OAuth2 endpoint for Discord authentication.
        
        Args:
            app (Application): The Discord application instance containing client ID and secret.
            scopes (List[LiteralString]): List of OAuth2 scopes to request permission for.
                                        Common scopes include 'identify', 'email', 'guilds'.
            redirect_uri (str): The URI where Discord will redirect the user after authorization.
                               This must match exactly with what's configured in your Discord application.
        
        Example:
            ```python
            app = Application("123456789", "secret")
            endpoint = Endpoint(
                app=app,
                scopes=["identify", "email"],
                redirect_uri="https://myapp.com/auth/callback"
            )
            ```
        """
        self.app = app
        self.scopes = scopes
        self.redirect_uri = redirect_uri

    @property
    def url(self) -> str:
        """
        Generate the Discord OAuth2 authorization URL.
        
        Returns:
            str: The complete authorization URL that users should visit to grant permissions.
        
        Example:
            ```python
            endpoint = Endpoint(app, ["identify"], "http://localhost:8000/callback")
            auth_url = endpoint.url
            print(f"Visit this URL to authorize: {auth_url}")
            ```
        """
        params = {
            "client_id": self.app.id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes)
        }
        return f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"

    def exchange(self, code: str) -> DiscordToken:
        """
        Exchange an authorization code for an access token.
        
        After a user authorizes your application, Discord redirects them to your redirect_uri
        with an authorization code. Use this method to exchange that code for an access token.
        
        Args:
            code (str): The authorization code received from Discord's callback.
        
        Returns:
            DiscordToken: An object containing the access token and related information.
        
        Raises:
            httpx.HTTPStatusError: If the token exchange request fails (e.g., invalid code).
        
        Example:
            ```python
            # After user authorizes and you receive the code from the callback
            try:
                token = endpoint.exchange(authorization_code)
                print(f"Success! Token expires in {token.expires_in} seconds")
            except httpx.HTTPStatusError as e:
                print(f"Token exchange failed: {e}")
            ```
        """
        data = {
            "client_id": self.app.id,
            "client_secret": self.app.secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }

        response = self.app.client.post(
            "https://discord.com/api/oauth2/token",
            data=data,
        )
        response.raise_for_status()
        return DiscordToken.model_validate(response.json())
    
    def get_user(self, token: DiscordToken) -> UserInfo:
        """
        Retrieve user information using an access token.
        
        Uses the provided access token to fetch the authenticated user's information
        from Discord's API. Requires the 'identify' scope.
        
        Args:
            token (DiscordToken): A valid access token obtained from the exchange() method.
        
        Returns:
            UserInfo: An object containing the user's Discord profile information.
        
        Raises:
            httpx.HTTPStatusError: If the API request fails (e.g., invalid/expired token).
        
        Example:
            ```python
            token = endpoint.exchange(code)
            try:
                user = endpoint.get_user(token)
                print(f"Welcome, {user.username}!")
                print(f"User ID: {user.id}")
                if user.avatar_url:
                    print(f"Avatar: {user.avatar_url}")
            except httpx.HTTPStatusError as e:
                print(f"Failed to get user info: {e}")
            ```
        """
        headers = {
            "Authorization": f"Bearer {token.access_token}"
        }

        response = self.app.client.get(
            "https://discord.com/api/v10/users/@me",
            headers=headers
        )
        response.raise_for_status()
        return UserInfo.model_validate(response.json())
