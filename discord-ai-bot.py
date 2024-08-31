import discord
from discord.ext import commands
import google.generativeai as genai
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Configure sua chave de API
genai.configure(api_key=os.getenv("API KEY GEMINI"))

# Inicializar o modelo
model = genai.GenerativeModel('gemini-1.5-flash')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Inicializa a memória como uma lista vazia
memory = []

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.command()
async def eva(ctx, *, message):
    if ctx.message.attachments:
        # Baixa a imagem da URL
        image_url = ctx.message.attachments[0].url
        image_data = requests.get(image_url).content
        response = get_gemini_response(message, image_data)
    else:
        response = get_gemini_response(message)
    for msg in response:
        # Adiciona quebras de linha entre as partes da resposta
        msg = msg.replace('\n\n', '\n')
        # Usa marcadores de formatação do Discord
        msg = msg.replace('*', '**')
        # Divide a mensagem em partes menores de 2000 caracteres
        for i in range(0, len(msg), 2000):
            await ctx.send(msg[i:i+2000])
        # Adiciona a mensagem e a resposta à memória
        memory.append((message, msg))
        # Gera uma imagem com base na resposta do Google Gemini
        image_url = generate_image(msg) # type: ignore
        await ctx.send(image_url)

def get_gemini_response(message, image_data=None):
    try:
        # Usa as últimas 10 tuplas da memória para fornecer o contexto à IA
        context = "\n".join([f"Usuário: {m}\nEva: {r}" for m, r in memory[-10:]])
        prompt = f"{context}\nUsuário: {message}\nEva:"
        if image_data:
            # Envia a imagem e a mensagem para a API do Google Gemini
            response = model.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_data}])
        else:
            # Envia apenas a mensagem para a API do Google Gemini
            response = model.generate_content(prompt)
        if response.candidates and response.candidates[0].content.parts:
            text = response.candidates[0].content.parts[0].text
            if len(text) > 2000:
                # Divide a resposta em mensagens menores de 2000 caracteres
                messages = [text[i:i+2000] for i in range(0, len(text), 2000)]
                return messages
            else:
                return [text]
        else:
            return ["A resposta da API do Google Gemini não contém um texto válido."]
    except Exception as e:
        return [f"Ocorreu um erro: {e}"]

#gemini-pro

import requests

url = "https://gemini-pro-ai.p.rapidapi.com/"

payload = { "contents": [
		{
			"role": "user",
			"parts": [{ "text": "Hello" }]
		}
	] }
headers = {
	"x-rapidapi-key": "ca6822c83bmshc823671da34f264p1d38dcjsn9d0d18fe21e3",
	"x-rapidapi-host": "gemini-pro-ai.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

def get_newsletters():
    # Use uma API de notícias para obter as notícias mais recentes sobre marketing digital e IA
    # Por exemplo, você pode usar a API do NewsAPI (https://newsapi.org/)
    # Certifique-se de obter uma chave de API e substituir "YOUR_API_KEY" abaixo
    url = f"https://newsapi.org/v2/everything?q=marketing+digital+OR+IA&apiKey=f2fc497bcb294c06b7e50f49d8034b45"
    response = requests.get(url)
    newsletters = response.json()["articles"]
    channel = bot.get_channel(1279246977690763316)

    # Use a API da Gemini para resumir as notícias em um formato mais conciso e fácil de ler
    summaries = []
    for newsletter in newsletters:
        title = newsletter["title"]
        description = newsletter["description"]
        prompt = f"Por favor, resuma o seguinte artigo de notícias em uma frase concisa e fácil de ler:\n\nTítulo: {title}\nDescrição: {description}"
        response = model.generate_content(prompt)
        summary = response.candidates[0].content.parts[0].text
        summaries.append(summary)

    return summaries

@bot.command()
async def news(ctx):
    summaries = get_newsletters()
    for summary in summaries:
        await ctx.send(summary)

print(response.json())

bot.run(os.getenv('TOKEN'))
