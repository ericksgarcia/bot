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
    Formata a mensagem original para incluir links para cada time.
    
    Args:
        original_message: A mensagem original recebida pelo bot.
    
    Returns:
        A mensagem formatada com os links para cada time.
    """
    # Lista para armazenar todas as linhas da mensagem formatada
    formatted_lines = []
    
    # Processa cada linha da mensagem original
    for line in original_message.split('\n'):
        # Procura por linhas que começam com ⚽️ e contêm times
        if '⚽️' in line and '(H)' in line and '(A)' in line:
            # Extrai os nomes dos times usando regex
            match = re.search(r'⚽️\s+(.+?)\s*\(H\)\s*x\s*(.+?)\s*\(A\)', line)
            if match:
                home_team = match.group(1).strip()
                away_team = match.group(2).strip()
                
                # Formata os nomes dos times para a URL (substitui espaços por +)
                home_team_url = home_team.replace(' ', '+')
                away_team_url = away_team.replace(' ', '+')
                
                # Adiciona a linha original
                formatted_lines.append(line)
                
                # Adiciona os links para os times
                formatted_lines.append(f"https://betwinner.com/br/search-events?searchtext={home_team_url}")
                formatted_lines.append(f"https://betwinner.com/br/search-events?searchtext={away_team_url}")
                formatted_lines.append("")  # Linha em branco para separar os jogos
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    # Junta todas as linhas em uma única string
    return '\n'.join(formatted_lines)

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
