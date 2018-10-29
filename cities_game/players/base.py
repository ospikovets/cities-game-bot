from abc import ABC, abstractmethod


class AbstractPlayer(ABC):
    """Class to define player interface
    
    Args:
        name (str): Player name
    Attributes:
        name (str): Player name
    """

    @abstractmethod
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def recieve_message(self, message: str =''):
        """Recieve message from the player
        
        Args:
            message (str): Message to send to the player before receiving one.
                Defaults to empty string.
        Returns:
            str: Recieved message
        """

    @abstractmethod
    def send_message(self, message: str):
        """Send message to the player
        
        Args:
            message (str): Message to send.
        """
