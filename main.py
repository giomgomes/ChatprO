import nest_asyncio
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging
import asyncio
import json

# Aplica o patch nest_asyncio para permitir loops aninhados
nest_asyncio.apply()


# Função para carregar configurações do arquivo config.json
def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
        return config

# Carrega as configurações
config = load_config()
telegram_token = config.get('telegram_token')
api_key = config.get('api_key')
url = config.get('url')
assistant_id = config.get('assistant_id')
version = '2024-08-05'  # Versão da API

# Inicializa o Watson Assistant
authenticator = IAMAuthenticator(api_key)
assistant = AssistantV2(
    version=version,
    authenticator=authenticator
)
assistant.set_service_url(url)

# Função para criar e gerenciar sessão do Watson
def create_session():
    response = assistant.create_session(assistant_id=assistant_id).get_result()
    return response['session_id']

# Cria uma sessão global
session_id = create_session()

# Configura o logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Função para responder mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Envia a mensagem para o Watson Assistant
    response = assistant.message(
        assistant_id=assistant_id,
        session_id=session_id,
        input={
            'message_type': 'text',
            'text': user_message
        }
    ).get_result()

    # Obtém a resposta do Watson
    watson_response = response['output']['generic'][0]['text']

    # Envia a resposta de volta para o Telegram
    await update.message.reply_text(watson_response)

# Função principal para configurar e iniciar o bot
async def main():
    # Configura o bot do Telegram
    application = Application.builder().token(telegram_token).build()

    # Adiciona handlers para mensagens
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Inicia o bot
    await application.run_polling()

# Executa o bot
if __name__ == '__main__':
    asyncio.run(main())


# acho q precisa disso aqui dps eu vejo
"""
assistant.delete_session(
    assistant_id=assistant_id,
    session_id=session_id
).get_result()
"""