import discordauth as discord
from rich import print


scope = "identify guilds.join"
app = discord.Application("1396858352734175324", "QIPSIF7BcCxUPP1dX4ftU0UCBPDqlWfD")
endpoint = discord.Endpoint(app, scope.split(), "http://localhost:8000/callback")

print(endpoint.url)
code = input("code: ")

token = endpoint.get_access_token(code)
print(token.access_token)

info = endpoint.get_user(token)
print(info)
