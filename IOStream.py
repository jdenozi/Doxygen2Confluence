from enum import Enum

from colorama import Fore, Style


class Color(Enum):
    """
    Enum class which represent the different color which can be used for stream output.
    """
    RED = Fore.RED
    GREEN = Fore.GREEN
    BLUE = Fore.BLUE


class StreamType(Enum):
    """
    Enum class which represent the different kind of stream output.
    """
    BASE = 0
    TITLE = 1
    SUB_TITLE = 2


class IOStream:
    """
    IOStream class can write sequences of characters and represent other kinds of data.
    The standard function are: cout and cerr
    """

    def __init__(self, color: bool = False):
        """
        Constructor of IOStream object.
        :param color: Indicate if we want color in stream character.
        """
        self.color = color

    def stdout(self, message: str, stream_type: StreamType = StreamType.BASE):
        """
        Redirect message to text console.
        :param message: The message to be printed on the console.
        :param stream_type: The type of stream to be printed on the console based on StreamType class.
        """
        if stream_type == StreamType.BASE:
            if self.color:
                print(Style.RESET_ALL + "     {}".format(message))
            else:
                print("     {}".format(message))

        if stream_type == StreamType.TITLE:
            if self.color:
                print(Style.RESET_ALL + "     - {}".format(message + "  ->"), end='')
            else:
                print(Style.RESET_ALL + "     - {}".format(message + "  ->"), end='')

        if stream_type == StreamType.SUB_TITLE:
            if self.color:
                print(Style.RESET_ALL + "     -- {}".format(message))
            else:
                print("     {}".format(message))

    def stderr(self, message: str):
        """
        Redirect error message to text console.
        :param message: The error message to be printed on text console.
        """
        if self.color:
            print(Fore.RED + "     [ERROR] " + Style.RESET_ALL + "{}".format(message))
            exit()
        else:
            print("     [ERROR] " + Style.RESET_ALL + "{}".format(message))
            exit()

    def stdlog(self, message: str):
        """
        Redirect log message to text console.
        :param message: The log message to be printed on text console.
        """
        if self.color:
            print(Fore.GREEN + "     [LOG] " + Style.RESET_ALL + "{}".format(message))
        else:
            print("     [LOG] " + Style.RESET_ALL + "{}".format(message))
