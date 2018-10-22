"""Game engine"""

import signal
from collections import deque
from typing import List, Set


class CitiesGameEngine:
    """Class to describe game engine

    This class encapsulates all game logic

    Args:
        players (list): List of players, who plays the game.
        cities (set): Cities awailable for the game.
        thinking_time (:obj:`int`, optional): Time in secconds
            to think about the next word. Defaults to 60.
    Attributes:
        players (list): List of players, who plays the game.
        cities (set): Cities awailable for the game.
        thinking_time (int): Time in secconds to think about the next word.
    """

    def __init__(self, players: List, cities: Set, thinking_time: int = 60):
        self.players = players
        self.cities = cities
        self.thinking_time = thinking_time

        self._is_playing = False
        self._used_cities = set()
        self._lost_players = []

    def start(self):
        """Start new game

        Returns:
            list: Of the players, who didn't loose the game.
        """

        self._is_playing = True
        letter = ''
        players_in_game = deque(self.players)

        while self._is_playing and len(players_in_game) > 1:
            curr_player = players_in_game.popleft()
            try:
                word = self.get_next_word(curr_player, letter)
            except TimeoutError:
                self._lost_players.append(curr_player)
                curr_player.message('You lost!')
            else:
                self._used_cities.add(word)
                letter = word[-1]
                players_in_game.append(curr_player)

        return self.finish()

    def finish(self):
        """Finish the game and name the winner(s)

        Returns:
            list: Of the players, who didn't loose the game.
        """

        self._is_playing = False
        return self.players - self._lost_players

    def restart(self):
        """Restart the game"""

        if self._is_playing:
            self.finish()

        self._used_cities = set()
        self._lost_players = []
        self.start()

    def is_valid(self, word: str, letter: str) -> bool:
        """Validate the word

        Check if the word starts from the correct letter
        and is a valid city from the list,
        and if it wasn't already mentioned by other players.

        Args:
            word (str): The word to validate.
            letter (str): The expected letter to start the word from.

        Returns:
            bool: True if valid, False otherwise.
        """

        starts_correctly = word.startswith(letter)
        is_valid_city = word in self.cities
        mentioned = word in self._used_cities

        return starts_correctly and is_valid_city and not mentioned

    def get_next_word(self, player, letter: str) -> str:
        """Get the word from the player

        Ask the player for the next word,
        while there is no valid word given
        or timeout is reached.

        Returns:
            str: Word gotten from the player.
        Raises:
            TimeoutError: If the word wasn't gotten during the `thinkg_time`
        """

        signal.signal(signal.SIGALRM, lambda *args: raise_(TimeoutError))
        signal.alarm(self.thinking_time)

        word = player.get_input(f'Your turn and the letter is "{letter}"')
        while not self.is_valid(word, letter):
            word = player.get_input('This word is not valid! '
                                    'Please give another one!')

        signal.signal(signal.SIGALRM, signal.SIG_IGN)

        return word


def raise_(ex):
    """Raise an Exception

    Wrapper to raise an exception in lambda function
    """
    raise ex
