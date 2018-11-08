"""Bot definititons

Connamds:
  invite - Invite players to the game
  play - Play the game
  finish - Finish the game and get a list of winners
"""

import os
import logging

from telegram.bot import Bot
from telegram.chat import Chat
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
from telegram.messageentity import MessageEntity
from telegram.user import User

from game import CitiesGame, GameConfigs, Player


CITIES = {'Kyiv', 'Vinnytsa', 'Artemivsk'}
DEFAULT_GAME_CONFIGS = GameConfigs(CITIES)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def start_command(bot, update):
    """Usage: /start"""

    wellcome_msg = "Wellcome! Add me to the group and let's play Cities Game"
    update.message.reply_text(wellcome_msg)

@run_async
def text_message_in_chat(bot, update, chat_data):
    logger.info(f'Recieved a message: "{update.message.text}"')

    game = chat_data.get('game')

    if chat_data.get('inviting'):
        entities = update.message.entities
        mentions = [e for e in entities if e.type == MessageEntity.TEXT_MENTION]
        logger.info(f'Mentions: {mentions}')
        users_to_add = [m.user for m in mentions]
        invited_users = chat_data['invited_users']
        invited_users.extend(users_to_add)
        players_name = [p.full_name for p in invited_users]
        update.message.reply_text(f'Players list: {players_name}')
    elif game and game.is_playing:
        sender_id = update.message.from_user.id
        player = chat_data['players'].get(sender_id)
        if player:
            player.name_the_city(update.message.text)
    else:
        user = update.effective_chat
        user.send_message('Hello')
        user.send_message('Hi')

def invite_command(bot, update, chat_data):
    """Usage: /invite"""

    chat_data['inviting'] = True
    chat_data['invited_users'] = [update.message.from_user]
    update.message.reply_text(
        "Let`s invite friends to the game. "
        "Just mention them in this chat "
        "and send '/play' when you are ready to go")

@run_async
def play_command(bot, update, chat_data):
    """Usage: /play"""

    chat_data['inviting'] = False
    game = chat_data.get('game')

    if game and game.is_playing():
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

def stop_command(bot, update, chat_data):
    """Usage: /stop"""

    chat_data['inviting'] = False
    game = chat_data.get('game')
    if game and game.is_playing:
        game.finish()

def telegram_player(user: User, chat: Chat):
    """Create game player from the telegram user in chat"""

    def send_message(message: str):
        mention = user.mention_markdown()
        text = f'{mention} {message}'
        chat.send_message(text)

    return Player(send_message)


def main():
    token = os.environ['TELEGRAM_BOT_TOKEN']
    updater = Updater(token=token)
    dp = updater.dispatcher

    start_command_handler = CommandHandler('start', start_command)
    invite_command_handler = CommandHandler(
        'invite', invite_command, filters=Filters.group, pass_chat_data=True
    )
    play_command_handler = CommandHandler(
        'play', play_command, filters=Filters.group, pass_chat_data=True
    )
    text_message_in_chat_handler = MessageHandler(
        Filters.text, text_message_in_chat, pass_chat_data=True
    )

    dp.add_handler(start_command_handler)
    dp.add_handler(invite_command_handler)
    dp.add_handler(play_command_handler)
    dp.add_handler(text_message_in_chat_handler)

    updater.start_polling(clean=True)
    logger.info('Booting the bot')
    updater.idle()

if __name__ == '__main__':
    main()
