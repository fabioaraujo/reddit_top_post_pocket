import praw
import os
import dotenv
import requests

dotenv.load_dotenv()
# Configurações da API do Reddit
client_id = os.getenv("client_id")

client_secret = os.getenv("client_secret")
user_agent = 'python-script-top-posts'

# Configurações da API do Pocket
pocket_consumer_key = os.getenv("pocket_consumer_key")
redirect_uri = 'https://getpocket.com/a/queue/'  # Pode ser qualquer URL de callback do Pocket


# Passo 1: Obter um request_token para autenticação
def get_request_token():
    response = requests.post(
        "https://getpocket.com/v3/oauth/request",
        headers={"X-Accept": "application/json"},
        data={"consumer_key": pocket_consumer_key, "redirect_uri": redirect_uri}
    )
    return response.json()["code"]


# Passo 2: Autenticar o request_token (é necessário fazer uma vez)
def authenticate_pocket(request_token):
    print("Acesse a URL abaixo para autenticar sua aplicação no Pocket:")
    print(f"https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={redirect_uri}")
    input("Após a autenticação, pressione Enter para continuar...")


# Passo 3: Obter o access_token
def get_access_token(request_token):
    response = requests.post(
        "https://getpocket.com/v3/oauth/authorize",
        headers={"X-Accept": "application/json"},
        data={"consumer_key": pocket_consumer_key, "code": request_token}
    )

    return response.json()["access_token"]


# Função para salvar uma URL no Pocket
def save_to_pocket(url, access_token):
    requests.post(
        "https://getpocket.com/v3/add",
        headers={"X-Accept": "application/json"},
        data={
            "url": url,
            "consumer_key": pocket_consumer_key,
            "access_token": access_token
        }
    )


access_token = os.getenv("access_token")
if not access_token:
    # Autenticação inicial
    request_token = get_request_token()
    authenticate_pocket(request_token)
    access_token = get_access_token(request_token)
    dotenv.set_key(key_to_set="access_token", value_to_set=access_token)

# Inicialize a instância do Reddit
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

# Acessa o subreddit e busca posts populares
subreddit = reddit.subreddit('todayilearned')
post = next(subreddit.top(limit=1, time_filter="day"))  # Busca o post mais popular

print(f"Título: {post.title}")
print(f"Pontuação: {post.score}")
print(f"URL: {post.url}")
print(f"Post URL: https://www.reddit.com{post.permalink}")
print("-" * 40)

# Envia a URL do post ao Pocket
save_to_pocket(post.url, access_token)
print("URL enviada ao Pocket com sucesso!")

