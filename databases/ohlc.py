import datetime as dt


class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class OHLC:
    __slots__ = ('timestamp', 'open', 'high', 'low', 'close', 'print_color')

    def __init__(self, timestamp: str, open: float, high: float,
                 low: float, close: float, print_color=Color.GREEN):
        self.timestamp = timestamp
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.print_color = print_color

    @classmethod
    def from_prices_list(cls, prices_list: list, print_color: str):
        shifted_time = dt.datetime.now() - dt.timedelta(minutes=1)
        return cls(timestamp=shifted_time.strftime('%Y-%m-%d %H:%M:%S'),
                   open=prices_list[0],
                   high=max(prices_list),
                   low=min(prices_list),
                   close=prices_list[-1],
                   print_color=print_color)

    def __str__(self):
        return f'{Color.BOLD}Timestamp - {Color.END}' \
               f'{self.print_color}{self.timestamp}{Color.END}, ' \
               f'{Color.BOLD}Open - {Color.END}' \
               f'{self.print_color}{self.open}{Color.END}, ' \
               f'{Color.BOLD}High - {Color.END}' \
               f'{self.print_color}{self.high}{Color.END}, ' \
               f'{Color.BOLD}Low - {Color.END}' \
               f'{self.print_color}{self.low}{Color.END}, ' \
               f'{Color.BOLD}Close - {Color.END}' \
               f'{self.print_color}{self.close}{Color.END}'
