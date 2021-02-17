from __future__ import annotations

class ChatRoom:
    def display_message(self, user: User, message: str) -> None:
        print(f"[{user} says]: {message}")

class User:
    def __init__(self, name: str) -> None:
        self.name = name
        self.chat_root = ChatRoom()

    def say(self, message: str) -> None:
        self.chat_root.display_message(self, message)

    def __str__(self) -> str:
        return self.name

def main():
    """
    >>> molly = User('Molly')
    >>> mark = User('Mark')
    >>> ethan = User('Ethan')

    >>> molly.say("Hi Team! Meeting at 3 PM today.")
    [Molly says]: Hi Team! Meeting at 3 PM today.
    >>> mark.say("Roger that!")
    [Mark says]: Roger that!
    >>> ethan.say("Alright.")
    [Ethan says]: Alright.
    """

if __name__ == "__main__":
    import doctest

    doctest.testmod()

