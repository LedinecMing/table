from dataclasses import dataclass, field
import typing
import colorama
from math import ceil

CLASSIC_COLOR_LAMBDA: typing.Callable[[int], str] = lambda n: colorama.Fore.WHITE
HORIZONTAL: int = 0
VERTICAL: int = 1


def to_dict(data: str) -> dict:
    rows: list = data.split("\n")
    result: dict = {}
    for row in rows:
        result[row.split(" ")[0]] = row.split(" ")[1:]
    return result


def int_split(number: int, split_char: str) -> str:
    if number < 1000:
        return str(number)
    full_number: str = str(number)
    return f"{full_number[0:len(full_number) % 3]}{split_char}{split_char.join(full_number[num:num + 3] for num in range(len(full_number) % 3, len(full_number), 3))}"


@dataclass
class TableStyle:
    _horizontal_symbol: str
    _vertical_symbol: str
    _corner_symbol: str

    horizontal_color: typing.Callable[[int], str]
    vertical_color: typing.Callable[[int], str]
    corner_color: typing.Callable[[int], str]

    types_color: typing.Dict[type, typing.Callable[[int], str]]
    column_color: typing.Callable[[int], str]

    barrier_size: typing.Tuple[int, int]
    table_indents: typing.Tuple[int, int]

    split_char: str

    item_requests: typing.Dict[type, int] = field(init=False)
    key_request: int = field(init=False, default_factory=lambda: 0)
    symbol_request_count: typing.Dict[str, int] = field(init=False,
                                                        default_factory=lambda: {"corner": 0, "horizontal": 0,
                                                                                 "vertical": 0})

    def __post_init__(self) -> None:
        self.item_requests: typing.Dict[type, int] = {}
        for k, v in self.types_color.items():
            self.item_requests[k] = 0

    @property
    def horizontal_symbol(self) -> str:
        self.symbol_request_count["horizontal"] += 1
        return self.horizontal_color(
            self.symbol_request_count["horizontal"]) + self._horizontal_symbol + colorama.Style.RESET_ALL

    @property
    def vertical_symbol(self) -> str:
        self.symbol_request_count["vertical"] += 1
        return self.vertical_color(
            self.symbol_request_count["vertical"]) + self._vertical_symbol + colorama.Style.RESET_ALL

    @property
    def corner_symbol(self) -> str:
        self.symbol_request_count["corner"] += 1
        return self.corner_color(self.symbol_request_count["corner"]) + self._corner_symbol + colorama.Style.RESET_ALL

    def color_data(self, data: typing.Hashable) -> str:
        color: typing.Callable[[int], str] = lambda n: colorama.Fore.WHITE
        for k, v in self.types_color.items():
            if isinstance(data, k):
                color = v
        return color(self.item_requests[type(data)])

    def clear_requests(self) -> None:
        self.symbol_request_count = {"corner": 0, "horizontal": 0, "vertical": 0}
        self.key_request = 0
        self.item_requests = {}
        for k, v in self.types_color.items():
            self.item_requests[k] = 0


class Table:
    def __init__(self,
                 table_info: typing.Dict[typing.Hashable, typing.Sequence[typing.Any]],
                 table_style: TableStyle) -> None:
        self.table_style: TableStyle = table_style
        self.table_info: typing.Dict[typing.Hashable, typing.Sequence[typing.Any]] = table_info

    def __getitem__(self, items: slice) -> typing.Sequence:
        if isinstance(items, slice):
            return list(self.table_info.values())[items]
        else:
            return self.table_info[items]

    @staticmethod
    def convert_value(split_char: str, value: typing.Any) -> str:
        if isinstance(value, int):
            return int_split(value, split_char)
        else:
            return str(value)

    def get_normal_idents(self, value: typing.Hashable, idents: int) -> str:
        self.table_style.item_requests[type(value)] += 1
        value = self.convert_value(self.table_style.split_char, value)
        idents = idents - len(value) + self.table_style.table_indents[HORIZONTAL]
        return " " * ceil(idents / 2) + value + " " * (idents // 2)

    def get_barrier(self, rotation: int) -> str:
        if rotation:
            return self.table_style.vertical_symbol * self.table_style.barrier_size[VERTICAL]
        else:
            return self.table_style.horizontal_symbol * self.table_style.barrier_size[HORIZONTAL]

    def get_max_raw_len(self, max_key_len: int, max_value_len: int) -> int:
        return max(max_key_len, max_value_len) + self.table_style.table_indents[HORIZONTAL] # * (
                #len(list(self.table_info.values())[0]) + 1) + self.table_style.table_indents[0]

    def get_data_len(self, column_num: int) -> int:
        if column_num >= len(self.table_info.keys()):
            column_num = len(self.table_info.keys()) - 1
        return len(list(self.table_info.values())[column_num])

    def get_text_table(self) -> None:
        max_value: int = max([len(str(i)) for j in self.table_info.values() for i in j])
        max_key: int = max(len(str(key)) for key in self.table_info.keys()) + self.table_style.table_indents[HORIZONTAL] * 2
        raw_len: int = self.get_max_raw_len(max_key, max_value)
        max_len: int = max(max_key, max_value)

        vertical_barriers: typing.Callable[[], str] = lambda: self.get_barrier(VERTICAL)
        corner: typing.Callable[[], str] = lambda: self.table_style.corner_symbol * self.table_style.barrier_size[1]

        empty_vertical_line: typing.Callable[[int], str] = lambda seq_len: \
            vertical_barriers() + vertical_barriers().join(
            [" " * raw_len for _ in range(seq_len + 1)]) + vertical_barriers()
        empty_horizontal_line: typing.Callable[[int], str] = lambda seq_len: corner() + corner().join(
            [self.table_style.horizontal_symbol * raw_len for _ in range(seq_len + 1)]) + corner()

        print(*[empty_horizontal_line(self.get_data_len(0)) for _ in range(self.table_style.barrier_size[VERTICAL])],
              sep="\n")
        for key, seq in self.table_info.items():
            print(*[empty_vertical_line(len(seq)) for _ in range(ceil(self.table_style.table_indents[1] / 2))],
                  sep="\n")
            self.table_style.key_request += 1
            print(vertical_barriers() + self.table_style.column_color(
                self.table_style.key_request) + self.get_normal_idents(key, max_len), end=vertical_barriers())
            for item in seq:
                print(self.table_style.color_data(item) + self.get_normal_idents(item, max_len),
                      end=self.get_barrier(VERTICAL))
            print("\n" + "\n".join(
                [empty_vertical_line(len(seq)) for _ in range(ceil(self.table_style.table_indents[1] / 2))]))
            next_seq_len: int = self.get_data_len(list(self.table_info.keys()).index(key) + 1)
            if next_seq_len > len(seq):
                print("\n".join([empty_horizontal_line(next_seq_len) for _ in range(self.table_style.barrier_size[0])]))
            else:
                print("\n".join([empty_horizontal_line(len(seq)) for _ in range(self.table_style.barrier_size[0])]))
        self.table_style.clear_requests()
