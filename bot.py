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
        Formata a mensagem original para incluir o link desejado.
        
        Args:
            original_message: A mensagem original recebida pelo bot.
        
        Returns:
            A mensagem formatada com os links.
        """
        # Regular expression para encontrar os nomes dos times
        teams_pattern = re.compile(r"⚽️\s*(.*?)\s*\(H\)\s*x\s*(.*?)\s*\(A\)\s*\(ao vivo\)")
        matches = teams_pattern.findall(original_message)
        
        if matches:
            formatted_message = original_message
            for home_team, away_team in matches:
                # Codificar os nomes dos times para formar os links
                home_team_link = f"https://www.pinnacle.com/en/search/{home_team.replace(' ', '%20')}/"
                away_team_link = f"https://www.pinnacle.com/en/search/{away_team.replace(' ', '%20')}/"
                
                # Substituir os nomes dos times pelos links
                formatted_message = formatted_message.replace(f"{home_team} (H)", f"<a href='{home_team_link}'>{home_team} (H)</a>")
                formatted_message = formatted_message.replace(f"{away_team} (A)", f"<a href='{away_team_link}'>{away_team} (A)</a>")
            
            return formatted_message
        else:
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
                    text=formatted_message,
                    parse_mode='HTML'  # Habilitar formatação HTML para os links
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
