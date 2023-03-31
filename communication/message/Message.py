#!/usr/bin/env python3
from .MessagePerformative import MessagePerformative


class Message:
    """Message class.
    Class implementing the message object which is exchanged between agents through a message service
    during communication.

    attr:
        from_agent: the sender of the message (id)
        to_agent: the receiver of the message (id)
        message_performative: the performative of the message
        content: the content of the message
    """

    def __init__(self, from_agent, to_agent, message_performative, content):
        """Create a new message."""
        self.__from_agent: int = from_agent
        self.__to_agent: int = to_agent
        self.__message_performative: MessagePerformative = message_performative
        self.__content: str = content

    def __str__(self) -> str:
        """Return Message as a String."""
        return (
            "From "
            + str(self.__from_agent)
            + " to "
            + str(self.__to_agent)
            + " ("
            + str(self.__message_performative)
            + ") "
            + str(self.__content)
        )

    def get_exp(self) -> int:
        """Return the sender of the message."""
        return self.__from_agent

    def get_dest(self) -> int:
        """Return the receiver of the message."""
        return self.__to_agent

    def get_performative(self) -> MessagePerformative:
        """Return the performative of the message."""
        return self.__message_performative

    def get_content(self):
        """Return the content of the message."""
        return self.__content
