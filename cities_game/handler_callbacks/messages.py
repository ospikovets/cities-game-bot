import logging

from telegram.ext.dispatcher import run_async
from telegram.messageentity import MessageEntity

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@run_async
def text_message_in_chat(bot, update, chat_data):
    logger.info(f'Recieved a message: "{update.message.text}"')

    game = chat_data.get('game')

    if chat_data.get('inviting'):
        process_invite(bot, update, chat_data)
    elif game and game.is_playing:
        process_game_message(bot, update, chat_data)


def process_invite(bot, update, chat_data):

    logger.info('Processing invite message')

    entities = update.message.entities
    mentions = [e for e in entities if e.type == MessageEntity.TEXT_MENTION]
    logger.info(f'Mentions: {mentions}')
    
    users_to_add = [m.user for m in mentions]
    invited_users = chat_data['invited_users']
    invited_users.extend(users_to_add)
    
    players_name = [p.full_name for p in invited_users]
    update.message.reply_text(f'Players list: {players_name}')


def process_game_message(bot, update, chat_data):

    logger.info('Processing game message')

    sender_id = update.message.from_user.id
    player = chat_data['players'].get(sender_id)
    if player:
        player.name_the_city(update.message.text)
