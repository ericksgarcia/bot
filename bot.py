from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import re  # Para usar expressões regulares
import os  # Para acessar variáveis de ambiente

class TelegramForwardBot:
    def __init__(self, token: str):
        """
        Inicializa o bot do Telegram.
        
        Args:
            token: Token do bot do Telegram.
        """
        self.app = Application.builder().token(token).build()
        self.chat_ids = set()  # Armazena os chat_ids dos usuários que iniciaram uma conversa
        
        # Registra os handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Responde ao comando /start."""
        chat_id = update.message.chat_id
        self.chat_ids.add(chat_id)  # Adiciona o chat_id à lista
        await update.message.reply_text(
            "Bot iniciado! Qualquer mensagem enviada será reencaminhada para os números configurados."
        )

    def format_message(self, original_message: str) -> str:
    """
    Formata a mensagem original para incluir os links dos times.
    
    Args:
        original_message: A mensagem original recebida pelo bot.
    
    Returns:
        A mensagem formatada com os links dos times.
    """
    # Usa regex para extrair os nomes dos times
    matches = re.findall(r"⚽️ (.+?) \(H\) x (.+?) \(A\) \(ao vivo\)", original_message)
    
    if matches:
        formatted_message = original_message + "\n\n"
        for home_team, away_team in matches:
            # Constrói os links para cada time
            home_link = f"https://betwinner.com/br/search-events?searchtext={home_team.replace(' ', '+')}"
            away_link = f"https://betwinner.com/br/search-events?searchtext={away_team.replace(' ', '+')}"
            
            # Adiciona os links à mensagem formatada
            formatted_message += f"🔗 {home_team}: {home_link}\n"
            formatted_message += f"🔗 {away_team}: {away_link}\n\n"
        
        return formatted_message.strip()
    else:
        # Se não encontrar os times, retorna a mensagem original
        return original_message

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Processa mensagens recebidas:
        1. Formata a mensagem.
        2. Reenvia para os chat_ids armazenados.
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
        """Inicia o bot."""
        print("Bot iniciado. Pressione Ctrl+C para parar.")
        self.app.run_polling()

if __name__ == "__main__":
    # Obtém o token do bot a partir de uma variável de ambiente
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("Por favor, defina a variável de ambiente BOT_TOKEN.")
    
    # Cria e inicia o bot
    bot = TelegramForwardBot(token=BOT_TOKEN)
    bot.run()
