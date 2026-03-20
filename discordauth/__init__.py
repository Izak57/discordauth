from typing import LiteralString, Optional, List
from urllib.parse import urlencode

from httpx import Client
from pydantic import BaseModel


def http_client() -> Client:
    client = Client()
    client.headers.update({
        "User-Agent": "DiscordOauth"
    })
    return client


class Application:

    def __init__(self, id: str, secret: str) -> None:
        self.id = id
        self.secret = secret
        self.client = http_client()


class UserInfo(BaseModel):
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
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        return None

    @property
    def banner_url(self) -> Optional[str]:
        if self.banner:
            return f"https://cdn.discordapp.com/banners/{self.id}/{self.banner}.png"
        return None



class DiscordToken(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    expires_in: int
    scope: str

    @property
    def scopes(self) -> List[str]:
        return self.scope.split(" ")


    def refresh(self, httpclient: Client | None = None) -> "DiscordToken":
        if self.refresh_token is None:
            raise ValueError("No refresh token available")
        return grant_token("refresh_token", {"refresh_token": self.refresh_token}, httpclient)



class Endpoint:

    def __init__(self,
                 app: Application,
                 scopes: List[LiteralString],
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

        return grant_token("authorization_code", data, self.app.client)



def grant_token(grant_type: str, data: dict, httpclient: Client | None = None) -> DiscordToken:
    if httpclient is None:
        httpclient = http_client()

    response = httpclient.post(
        "https://discord.com/api/oauth2/token",
        data={
            "grant_type": grant_type,
            **data
        },
    )

    response.raise_for_status()
    token = DiscordToken.model_validate(response.json())
    return token


def get_user(token: DiscordToken | str, httpclient: Client | None = None) -> UserInfo:
    if httpclient is None:
        httpclient = http_client()

    if isinstance(token, DiscordToken):
        access_token = token.access_token
        token_type = token.token_type
    else:
        access_token = token
        token_type = "Bearer"

    response = httpclient.get(
        "https://discord.com/api/v10/users/@me",
        headers={
            "Authorization": f"{token_type} {access_token}"
        }
    )

    response.raise_for_status()
    return UserInfo.model_validate(response.json())
