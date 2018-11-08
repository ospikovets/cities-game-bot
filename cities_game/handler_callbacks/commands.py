import logging

from telegram.chat import Chat
from telegram.ext.dispatcher import run_async
from telegram.user import User

from game import CitiesGame, GameConfigs, Player

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CITIES = {'Kyiv', 'Vinnytsa', 'Artemivsk'}
DEFAULT_GAME_CONFIGS = GameConfigs(CITIES)


def start_command(bot, update):
    """Usage: /start"""

    logger.info('Recieved command /start')

    wellcome_msg = "Wellcome! Add me to the group and let's play Cities Game"
    update.message.reply_text(wellcome_msg)


def invite_command(bot, update, chat_data):
    """Usage: /invite"""

    logger.info('Recieved command /invite')

    chat_data['inviting'] = True
    chat_data['invited_users'] = [update.message.from_user]
    update.message.reply_text(
        "Let`s invite friends to the game. "
        "Just mention them in this chat "
        "and send '/play' when you are ready to go")

@run_async
def play_command(bot, update, chat_data):
    """Usage: /play"""

    logger.info('Recieved command /play')

    chat_data['inviting'] = False
    game = chat_data.get('game')

    if game and game.is_playing:
        update.message.reply_text("We already playing!")
    elif len(chat_data.get('invited_users', [])) < 2:
        update.message.reply_text(
            "At least 2 players are required to play the game. "
            "You can invite them with '/invite' command."
        )
    else:
        chat = update.effective_chat
        chat_data['players'] = {u.id: telegram_player(u, chat) for u in chat_data['invited_users']}
        players = [p for p in chat_data['players'].values()]
        game = CitiesGame(players, DEFAULT_GAME_CONFIGS)
        chat_data['game'] = game
        
        update.message.reply_text("Let`s the game begins!")
        game.start()

@run_async
def finish_command(bot, update, chat_data):
    """Usage: /stop"""

    logger.info('Recieved command /stop')

    chat_data['inviting'] = False
    game = chat_data.get('game')
    if game and game.is_playing:
        game.finish()
        update.message.reply_text('The game was finished! Thank you for playing.')


def telegram_player(user: User, chat: Chat):
    """Create game player from the telegram user in chat"""

    def send_message(message: str):
        mention = user.full_name
        text = f'{mention} {message}'
        chat.send_message(text)

    return Player(send_message)
