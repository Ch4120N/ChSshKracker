# -*- UTF-8 -*-
# ui/summary_render.py

import shutil


class SummaryRenderer:
    def __init__(self, title: str = 'Configuration Summary', space: int = 5, margin_left_spaces: int = 2, max_width: int = 80) -> None:
        self.title = title
        self.space = space
        self.margin_left = ' ' * margin_left_spaces
        self.max_pref_width = max_width

    def render(self, summary: dict) -> None:
        terminal_width = shutil.get_terminal_size((80, 20)).columns
        max_line_width = min(terminal_width, self.max_pref_width)
        spaces = ' ' * self.space
        max_key_length = max((len(str(k))
                             for k in summary if summary[k]), default=0)

        
        padding = (max_line_width - len(self.title) - 4) // 2
        padding = max(padding, 5)
        print(self.margin_left + '═' * padding + f' {self.title} ' + '═' * padding)

        for key, value in summary.items():
            if value is None or value == '' or value == 0:
                continue
            key_str = str(key)
            value_str = str(value)
            line = f"{self.margin_left}{key_str:<{max_key_length}}{spaces}: {value_str}"
            if len(line) > max_line_width:
                wrap_width = max_line_width - max_key_length - len(spaces) - 6
                wrapped_value = [value_str[i:i+wrap_width]
                                 for i in range(0, len(value_str), wrap_width)]
                print(
                    f"{self.margin_left}{key_str:<{max_key_length}}{spaces}: {wrapped_value[0]}")
                for part in wrapped_value[1:]:
                    print(
                        f"{self.margin_left}{' ' * (max_key_length + len(spaces) + 2)}{part}")
            else:
                print(line)

        print(self.margin_left + '═' * (max_line_width - 3))
