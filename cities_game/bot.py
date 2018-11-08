"""Bot definititons

Connamds:
  invite - Invite players to the game
  play - Play the game
  finish - Finish the game and get a list of winners
"""

import os
import logging

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

from handler_callbacks.commands import (
    finish_command,
    invite_command, 
    play_command, 
    start_command, 
)
from handler_callbacks.messages import text_message_in_chat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
    finish_command_handler = CommandHandler(
        'finish', finish_command, filters=Filters.group, pass_chat_data=True
    )
    text_message_in_chat_handler = MessageHandler(
        Filters.text, text_message_in_chat, pass_chat_data=True
    )

    dp.add_handler(start_command_handler)
    dp.add_handler(invite_command_handler)
    dp.add_handler(play_command_handler)
    dp.add_handler(finish_command_handler)
    dp.add_handler(text_message_in_chat_handler)

    updater.start_polling(clean=True)
    logger.info('Booting the bot')
    updater.idle()


if __name__ == '__main__':
    main()
