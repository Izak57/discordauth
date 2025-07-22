from typing import LiteralString
from urllib.parse import urlencode
from httpx import Client
from pydantic import BaseModel



class Application:

    def __init__(self, id: str, secret: str) -> None:
        self.id = id
        self.secret = secret
        self.client = Client()
        self.client.headers.update({
            "User-Agent": "DiscordOauth"
        })



class UserInfo(BaseModel):
    id: str
    username: str
    avatar: str | None
    discriminator: str
    public_flags: int
    flags: int
    banner: str | None
    accent_color: int | None
    global_name: str | None
    mfa_enabled: bool
    locale: str | None
    premium_type: int

    @property
    def avatar_url(self) -> str | None:
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return None



class DiscordToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    scope: str

    @property
    def scopes(self) -> list[str]:
        return self.scope.split(" ")



class Endpoint:

    def __init__(self,
                 app: Application,
                 scopes: list[LiteralString],
                 redirect_uri: str) -> None:
        self.app = app
        self.scopes = scopes
        self.redirect_uri = redirect_uri


    @property
    def url(self) -> str:
        params = {
            "client_id": self.app.id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes)
        }
        return f"https://discord.com/api/oauth2/authorize?{urlencode(params)}"


    def exchange(self, code: str) -> DiscordToken:
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
        headers = {
            "Authorization": f"Bearer {token.access_token}"
        }

        response = self.app.client.get(
            "https://discord.com/api/v10/users/@me",
            headers=headers
        )
        response.raise_for_status()
        return UserInfo.model_validate(response.json())
