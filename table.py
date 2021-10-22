import typing
import colorama
from math import ceil

CLASSIC_COLOR_LAMBDA: typing.Callable[[int], str] = lambda n: colorama.Fore.WHITE
HORIZONTAL: int = 0
VERTICAL: int = 1


def int_split(number: int, split_char: str) -> str:
    if number < 1000:
        return str(number)
    full_number: str = str(number)
    return f"{full_number[0:len(full_number) % 3]}{split_char}{split_char.join(full_number[num:num + 3] for num in range(len(full_number) % 3, len(full_number), 3))}"


class TableStyle:
    def __init__(self,
                 horizontal_symbol: str = "-", vertical_symbol: str = "|",
                 corner_symbol: str = "+",
                 horizontal_color: typing.Callable[[int], str] = CLASSIC_COLOR_LAMBDA, vertical_color: typing.Callable[[int], str] = CLASSIC_COLOR_LAMBDA,
                 corner_color: typing.Callable[[int], str] = CLASSIC_COLOR_LAMBDA,
                 types_color: typing.Dict[type, typing.Callable[[int], str]] = {},
                 barrier_size: typing.Tuple[int, int] = (2, 2),
                 table_indents: typing.Tuple[int, int] = (1, 1),
                 split_char: str = ".") -> None:
        self.types_color: typing.Dict[type, typing.Callable[[int], str]] = types_color
        self.corner_color: typing.Callable[[int], str] = corner_color
        self.horizontal_color: typing.Callable[[int], str] = horizontal_color
        self.vertical_color: typing.Callable[[int], str] = vertical_color

        self._horizontal_symbol: str = horizontal_symbol
        self._vertical_symbol: str = vertical_symbol
        self._corner_symbol: str = corner_symbol
        self.split_char: str = split_char

        self.barrier_size: typing.Tuple[int, int] = barrier_size
        self.table_indents: typing.Tuple[int, int] = table_indents

    @property
    def horizontal_symbol(self) -> str:
        return self.horizontal_color(0) + self._horizontal_symbol + colorama.Style.RESET_ALL

    @property
    def vertical_symbol(self) -> str:
        return self.vertical_color(0) + self._vertical_symbol + colorama.Style.RESET_ALL

    @property
    def corner_symbol(self) -> str:
        return self.corner_color(0) + self._corner_symbol + colorama.Style.RESET_ALL

    def color_data(self, data: typing.Hashable) -> str:
        color: typing.Callable[[int], str] = lambda n: colorama.Fore.WHITE
        for k, v in self.types_color.items():
            if isinstance(data, k):
                color = v
        return color(0)


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

    def get_normal_idents(self, value: typing.Hashable, idents: int, rotation: int) -> str:
        value = self.convert_value(self.table_style.split_char, value)
        idents = idents - len(value) + self.table_style.table_indents[rotation]
        return " "*ceil(idents/2) + value + " "*(idents//2)

    def get_barrier(self, rotation: int) -> str:
        if rotation:
            return self.table_style.vertical_symbol * self.table_style.barrier_size[VERTICAL]
        else:
            return self.table_style.horizontal_symbol * self.table_style.barrier_size[HORIZONTAL]

    def get_max_raw_len(self) -> int:
        max_key_len: int = max(len(str(key)) for key in self.table_info.keys())
        return (self.table_style.table_indents[0] + max_key_len + len(self.get_barrier(VERTICAL))) * (len(list(self.table_info.values())[1]) + 1) + self.table_style.table_indents[0]

    def get_data_len(self, column_num: int) -> int:
        if column_num >= len(self.table_info.keys()):
            column_num = len(self.table_info.keys()) - 1
        return len(list(self.table_info.values())[column_num])

    def get_text_table(self) -> None:
        max_len: int = max([len(str(i)) for j in self.table_info.values() for i in j])
        max_key_len: int = max(len(str(key)) for key in self.table_info.keys())

        raw_len: int = max_key_len + self.table_style.table_indents[0]
        vertical_barriers: str = self.get_barrier(VERTICAL)
        corner: str = self.table_style.corner_symbol * self.table_style.barrier_size[0]

        empty_vertical_line: typing.Callable[[int], str] = lambda seq_len: vertical_barriers + vertical_barriers.join([" " * raw_len for i in range(seq_len + 1)]) + vertical_barriers
        empty_horizontal_line: typing.Callable[[int], str] = lambda seq_len: corner + corner.join([self.table_style.horizontal_symbol * raw_len for i in range(seq_len + 1)]) + corner

        print(empty_horizontal_line(self.get_data_len(0)))
        for key, seq in self.table_info.items():
            print(empty_vertical_line(len(seq)))
            print(vertical_barriers + self.get_normal_idents(key, max_key_len, VERTICAL), end=vertical_barriers)
            for item in seq:
                print(self.table_style.color_data(item) + self.get_normal_idents(item, max_len, VERTICAL), end=self.get_barrier(VERTICAL))
            print("\n" + empty_vertical_line(len(seq)))
            next_seq_len: int = self.get_data_len(list(self.table_info.keys()).index(key) + 1)
            if next_seq_len > len(seq):
                print(empty_horizontal_line(next_seq_len))
            else:
                print(empty_horizontal_line(len(seq)))


classic_style: TableStyle = TableStyle(table_indents=(2, 2),
                                       horizontal_symbol="=", barrier_size=(2, 2),
                                       horizontal_color=lambda n: colorama.Fore.CYAN,
                                       corner_color=lambda n: colorama.Fore.BLUE,
                                       vertical_color=lambda n: colorama.Fore.GREEN,
                                       types_color={int: lambda n: colorama.Fore.RED,
                                                    str: lambda n: colorama.Fore.LIGHTGREEN_EX}
                                       )
my_table: Table = Table({"Age": [1000, 50, 23, 43, 18], "Gender": ["Male", "Female", "Female", "Male", "Female", "Male"], "Weight": [90, 70, 60, 108, 73]},
                        classic_style)
my_table.get_text_table()
