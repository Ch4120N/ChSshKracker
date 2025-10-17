# -*- UTF-8 -*-
# ui/sharp_box.py

import shutil
import textwrap

from colorama import Fore, init

from core.config import ANSI_ESCAPE

init(autoreset=True)


class SharpBox:
    """
    SharpBox renders a boxed help banner
    Features:
    - Customizable title, version, usage and options
    - Responsive to terminal width (will shrink content to fit)
    - Optional colored title using colorama
    - Export as plain text (no ANSI escapes) or save to file
    """

    def __init__(self, title: str, version: str = '', description: str = '', usage: str = '', options: list = [], examples: list = [],
                 width: int = 94, color: bool = True, margin_left: int = 2):
        """
        - title: main title string (e.g. 'ChSSHKracker - Ch4120N SSH Kracker')
        - version: version suffix to append to title (e.g. 'v1.3.0')
        - usage: usage string (one-liner)
        - options: list of (opt, desc) tuples or strings. If string, it is printed raw.
        - width: preferred full banner width (including border). The class will adapt to terminal size.
        - color: whether to color the title line; uses colorama Fore cyan by default.
        """
        self.title = title.strip()
        self.version = version.strip()
        self.description = description.strip()
        self.usage = usage.strip()
        self.options = options if options is not None else []
        self.examples = examples if examples is not None else []
        self.preferred_width = max(40, int(width))
        self.color = bool(color)
        self.margin_left = margin_left if margin_left is not None else 0
        # internal computed width after consulting terminal size
        self.width = self._compute_width()
        # inner content width (space between the two '#' and spaces)
        self.inner_width = self.width - 4  # '# ' + content + ' #'

    def _compute_width(self):
        cols = shutil.get_terminal_size(
            fallback=(self.preferred_width, 24)).columns
        # ensure there's a minimal comfortable width
        return min(max(40, cols), max(40, self.preferred_width))

    def _make_border(self):
        return ' ' * self.margin_left + '#' * self.width

    def _make_empty_line(self):
        return ' ' * self.margin_left + '#'+(' ' * (self.width-2))+'#'

    def _pad_line(self, text: str, align: str = 'left') -> str:
        """Pad a plain text (no ANSI) to fit inner width with alignment and framing hashes."""
        plain = ANSI_ESCAPE.sub('', text)
        if len(plain) > self.inner_width:
            # shouldn't happen here; caller should wrap
            plain = plain[:self.inner_width]
        space = self.inner_width - len(plain)
        if align == 'center':
            left = space // 2
            right = space - left
            body = ' ' * left + text + ' ' * right
        elif align == 'right':
            body = ' ' * space + text
        else:
            # left
            body = text + ' ' * space
        return ' ' * self.margin_left + f"# {body} #"

    def _pad_line_options(self, text: str, align: str = 'left') -> str:
        """Pad a plain text (no ANSI) to fit inner width with alignment and framing hashes."""
        plain = ANSI_ESCAPE.sub('', text)
        if len(plain) > self.inner_width:
            # shouldn't happen here; caller should wrap
            plain = plain[:self.inner_width]
        space = self.inner_width - len(plain)
        if align == 'center':
            left = space // 2
            right = space - left
            body = ' ' * left + text + ' ' * right
        elif align == 'right':
            body = ' ' * space + text + ' ' * 2
        else:
            # left
            body = ' ' * 2 + text + ' ' * (space-2)
        return ' ' * self.margin_left + f"# {body} #"

    def _pad_line_examples(self, text: str, align: str = 'left') -> str:
        """Pad a plain text (no ANSI) to fit inner width with alignment and framing hashes."""
        plain = ANSI_ESCAPE.sub('', text)
        if len(plain) > self.inner_width:
            # shouldn't happen here; caller should wrap
            plain = plain[:self.inner_width]
        space = self.inner_width - len(plain)
        if align == 'center':
            left = space // 2
            right = space - left
            body = ' ' * left + text + ' ' * right
        elif align == 'right':
            body = ' ' * (space-4) + text + ' -' + ' ' * 2
        else:
            # left
            body = ' ' * 2 + '- ' + text + ' ' * (space-4)
        return ' ' * self.margin_left + f"# {body} #"

    def _wrap_text(self, text: str, width: int):
        # wrap without breaking words; returns list of strings
        return textwrap.wrap(text, width=width) or ['']

    def render(self, color: bool = False) -> str:
        """Return the banner as a single string. If color is None, use instance setting."""
        do_color = self.color if color is None else bool(color)
        # recompute width in case terminal changed
        self.width = self._compute_width()
        self.inner_width = self.width - 4

        lines = []
        lines.append(self._make_border())

        # Title line (include version if provided)
        full_title = self.title + (f' v{self.version}' if self.version else '')
        # color the title if requested
        if do_color:
            title_text = Fore.CYAN + full_title + Fore.RESET
        else:
            title_text = full_title
        lines.append(self._pad_line(title_text, align='center'))

        # empty line
        lines.append(self._make_empty_line())

        # Description
        if self.description:
            desc_lines = self._wrap_text(self.description, self.inner_width)
            for d in desc_lines:
                lines.append(self._pad_line(d, align='center'))
            lines.append(self._make_empty_line())

        # Usage
        if self.usage:
            usage_lines = self._wrap_text(self.usage, self.inner_width)
            for u in usage_lines:
                lines.append(self._pad_line(u, align='center'))
            lines.append(self._make_empty_line())

        # Options header
        if self.options:
            lines.append(self._pad_line('OPTIONS:', align='left'))
            # For each option, format as '  -I, --ip-list    description'
            for opt in self.options:
                if isinstance(opt, str):
                    opt_line = opt
                    wrapped = self._wrap_text(opt_line, self.inner_width)
                    for w in wrapped:
                        lines.append(self._pad_line_options(w, align='left'))
                else:
                    # tuple/list
                    opt_name, opt_desc = opt[0], opt[1]
                    # pad opt_name to align descriptions at column 24 (configurable)
                    opt_field_width = 24
                    opt_name_plain = ANSI_ESCAPE.sub('', str(opt_name))
                    if len(opt_name_plain) >= opt_field_width - 2:
                        # too long, put name on its own line
                        lines.append(self._pad_line_options(
                            opt_name, align='left'))
                        wrapped = self._wrap_text(
                            str(opt_desc), self.inner_width - 2)
                        for w in wrapped:
                            lines.append(self._pad_line_options(
                                '  ' + w, align='left'))
                    else:
                        # place name and description on same line if fits
                        space_for_desc = self.inner_width - opt_field_width
                        desc_wrapped = self._wrap_text(
                            str(opt_desc), width=space_for_desc)
                        first = opt_name.ljust(
                            opt_field_width) + (desc_wrapped[0] if desc_wrapped else '')
                        lines.append(self._pad_line_options(
                            first.rstrip(), align='left'))
                        for cont in desc_wrapped[1:]:
                            lines.append(self._pad_line_options(
                                ' ' * opt_field_width + cont, align='left'))
        # empty line after options
        lines.append(self._make_empty_line())
        if self.examples:
            lines.append(self._pad_line('EXAMPLES:', align='left'))
            # For each option, format as '  -I, --ip-list    description'
            for opt in self.examples:
                if isinstance(opt, str):
                    opt_line = opt
                    wrapped = self._wrap_text(opt_line, self.inner_width)
                    for w in wrapped:
                        lines.append(self._pad_line_examples(w, align='left'))
                else:
                    # tuple/list
                    opt_name, opt_desc = opt[0], opt[1]
                    # pad opt_name to align descriptions at column 24 (configurable)
                    opt_field_width = 24
                    opt_name_plain = ANSI_ESCAPE.sub('', str(opt_name))
                    if len(opt_name_plain) >= opt_field_width - 2:
                        # too long, put name on its own line
                        lines.append(self._pad_line_examples(
                            opt_name, align='left'))
                        wrapped = self._wrap_text(
                            str(opt_desc), self.inner_width - 2)
                        for w in wrapped:
                            lines.append(self._pad_line_examples(
                                '  ' + w, align='left'))
                    else:
                        # place name and description on same line if fits
                        space_for_desc = self.inner_width - opt_field_width
                        desc_wrapped = self._wrap_text(
                            str(opt_desc), width=space_for_desc)
                        first = opt_name.ljust(
                            opt_field_width) + (desc_wrapped[0] if desc_wrapped else '')
                        lines.append(self._pad_line_examples(
                            first.rstrip(), align='left'))
                        for cont in desc_wrapped[1:]:
                            lines.append(self._pad_line_examples(
                                ' ' * opt_field_width + cont, align='left'))
        # empty line after examples
        lines.append(self._make_empty_line())

        # bottom border
        lines.append(self._make_border())

        return '\n'.join(lines)

    def render_plain(self) -> str:
        return ANSI_ESCAPE.sub('', self.render(color=False))

    def save_to_file(self, path: str, plain: bool = True):
        data = self.render_plain() if plain else self.render()
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(data)
