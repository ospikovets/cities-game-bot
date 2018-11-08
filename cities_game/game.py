"""Game engine"""

import signal
import time
from collections import deque
from typing import List, Set


class GameConfigs:

    def __init__(self, cities: Set[str], thinking_time: int = 60):
        self.cities = {city.lower() for city in cities}
        self.thinkg_time = thinking_time


class Player:

    PING_INTERVAL = 0.5  # secconds

    def __init__(self, send_message: callable):
        self.send_message = send_message
        self.__named_cities = deque()

    def name_the_city(self, city: str):
        """Name the city"""

        self.__named_cities.append(city)
    
    def pop_the_city(self):
        """Get first unprocessed city"""

        return self.__named_cities.popleft()
    
    def turn(self, letter):
        """Turn function wrapper"""

        self.__named_cities = deque()
        if not letter:
            letter = 'ANY'
        return self.send_message(f"now your turn and the letter is '{letter}'")

class CitiesGame:
    """Class to describe game engine

    This class encapsulates all game logic

    Args:
        cities (set): Cities awailable for the game.
        thinking_time (:obj:`int`, optional): Time in secconds
            to think about the next word. Defaults to 60.
    Attributes:
        cities (set): Cities awailable for the game.
        thinking_time (int): Time in secconds to think about the next word.
    """

    def __init__(self, players: List[Player], configs: GameConfigs):
        self.players = players
        self.configs = configs
        self._loosers = []
        self._is_playing = False
        self._used_cities = set()

    @property
    def is_playing(self):
        return self._is_playing

    def start(self):
        """Start a new game

        Returns:
          list: Of the players, who didn't loose the game.
        """

        self._is_playing = True
        letter = ''
        players_in_game = deque(self.players)

        while self._is_playing and len(players_in_game) > 1:
            curr_player = players_in_game.popleft()
            word = self.get_next_word(curr_player, letter)
            
            if word:
                self._used_cities.add(word)
                letter = self.get_new_letter(word)
                players_in_game.append(curr_player)

        return self.finish()

    def finish(self):
        """Finish the game and name the winner(s)

        Returns:
          list: Of the players, who didn't loose the game.
        """

        self._is_playing = False
        return [p for p in self.players if p not in self._loosers]

    def get_new_letter(self, word: str) -> str:
        """Extract the letter that should be the first one in the next word
        
        Arg:
          word (str): The word to extract the letter from.
        Returns:
          srt: The first letter for the next word.
        """

        return word[-1]

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

        word = word.lower()
        starts_correctly = word.startswith(letter)
        is_valid_city = word in self.configs.cities
        mentioned = word in self._used_cities

        return starts_correctly and is_valid_city and not mentioned

    def get_next_word(self, player: Player, letter: str) -> str:
        """Get the word from the player

        Ask the player for the next word,
        while there is no valid word given
        or timeout is reached.

        Args:
          player (Player): The player who should name the next word.
          letter (str): The first lettert for the next word.
        Returns:
            str: Word gotten from the player.
        Raises:
            TimeoutError: If the word wasn't gotten during the `thinkg_time`.
        """

        player.turn(letter)
        while self._is_playing:
            try:
                word = player.pop_the_city()
            except IndexError:
                time.sleep(player.PING_INTERVAL)
            else:
                if self.is_valid(word, letter):
                    return word
                else:
                    player.send_message('it is not a valid city, name another one.')
