from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import re  # Importa o módulo de expressões regulares

class TelegramForwardBot:
    def __init__(self, token: str):
        """
        Inicializa o bot do Telegram
        
        Args:
            token: Token do bot do Telegram
        """
        self.app = Application.builder().token(token).build()
        self.chat_ids = set()  # Armazena os chat_ids dos usuários que iniciaram uma conversa
        
        # Registra os handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Responde ao comando /start"""
        chat_id = update.message.chat_id
        self.chat_ids.add(chat_id)  # Adiciona o chat_id à lista
        await update.message.reply_text(
            "Bot iniciado! Qualquer mensagem enviada será reencaminhada para os números configurados."
        )

    def format_message(self, original_message: str) -> str:
        """
        Formata a mensagem original para incluir o link desejado.
        
        Args:
            original_message: A mensagem original recebida pelo bot.
        
        Returns:
            A mensagem formatada com o link.
        """
        # Usa regex para extrair o nome do campeonato
        match = re.search(r"🏟 (.+)$", original_message, re.MULTILINE)
        if match:
            campeonato = match.group(1).strip().lower().replace(" ", "-")
            # Constrói o link
            link = f"https://black.betinasia.com/v/sportsbook/football/XE/{campeonato}?group=in+running"
            # Retorna a mensagem original com o link adicionado
            return f"{original_message}\n\n🔗 Acompanhe aqui: {link}"
        else:
            # Se não encontrar o campeonato, retorna a mensagem original
            return original_message

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processa mensagens recebidas:
        1. Formata a mensagem
        2. Reenvia para os chat_ids armazenados
        """
        # Obtém a mensagem
        original_message = update.message.text

        # Formata a mensagem
        formatted_message = self.format_message(original_message)

        # Reenvia para cada chat_id armazenado
        for chat_id in self.chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=formatted_message
                )
            except Exception as e:
                await update.message.reply_text(
                    f"Erro ao enviar para o chat_id {chat_id}. Certifique-se que o usuário iniciou uma conversa com o bot."
                )
                print(f"Erro ao enviar para o chat_id {chat_id}: {e}")

    def run(self):
        """Inicia o bot"""
        print("Bot iniciado. Pressione Ctrl+C para parar.")
        self.app.run_polling()

# Configurações do bot
BOT_TOKEN = "7805157753:AAHELL_l95bTuZ3WQVw_Iz_guqy7Oe-CsFo"

if __name__ == "__main__":
    # Cria e inicia o bot
    bot = TelegramForwardBot(token=BOT_TOKEN)
    bot.run()