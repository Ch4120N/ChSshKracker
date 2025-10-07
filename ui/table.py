import re
from colorama import Fore, Style, init

# Initialize colorama for colored text output
init(autoreset=True)

class Theme:
    """
    Theme class defines the colors and border styles for the table.
    - parent_color: Color of the parent border
    - block_color: Default color for individual blocks
    - border_style: Style of the border ('double', 'single', 'modern')
    """
    def __init__(self, parent_color=Fore.BLUE, block_color=Fore.WHITE, border_style='double'):
        self.parent_color = parent_color
        self.block_color = block_color
        self.border_style = border_style
        self.set_style(border_style)

    def set_style(self, style):
        """
        Sets the characters for borders based on the selected style.
        Supported styles: 'double', 'single', 'modern'
        """
        if style == 'double':
            self.chars = {
                'top_left':'╔','top_right':'╗','bottom_left':'╚','bottom_right':'╝',
                'horizontal':'═','vertical':'║','sep_left':'╠','sep_right':'╣'
            }
        elif style == 'single':
            self.chars = {
                'top_left':'┌','top_right':'┐','bottom_left':'└','bottom_right':'┘',
                'horizontal':'─','vertical':'│','sep_left':'├','sep_right':'┤'
            }
        elif style == 'modern':
            self.chars = {
                'top_left':'╭','top_right':'╮','bottom_left':'╰','bottom_right':'╯',
                'horizontal':'─','vertical':'│','sep_left':'├','sep_right':'┤'
            }
        else:  # Default to double if unknown style
            self.chars = {
                'top_left':'╔','top_right':'╗','bottom_left':'╚','bottom_right':'╝',
                'horizontal':'═','vertical':'║','sep_left':'╠','sep_right':'╣'
            }

class Table:
    # Regular expression to detect ANSI escape codes for colored text
    ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')

    def __init__(self, theme=None, parent_border=True, parent_padding=2, block_padding=2):
        """
        Initializes the table.
        - theme: Theme object containing colors and border style
        - parent_border: Whether to display the main parent border
        - parent_padding: Padding between parent border and blocks
        - block_padding: Padding inside each block
        """
        self.blocks = []  # List of blocks to display
        self.theme = theme if theme else Theme()
        self.parent_border = parent_border
        self.parent_padding = parent_padding
        self.block_padding = block_padding

    def add_block(self, lines, align='center', block_color=None):
        """
        Adds a block to the table.
        - lines: List of strings for block content
        - align: Alignment of the text ('left', 'center', 'right')
        - block_color: Optional color for the block border/text if lines don't have their own color
        """
        self.blocks.append({
            'lines': lines,
            'align': align,
            'color': block_color or self.theme.block_color
        })

    def _str_len(self, text):
        """
        Returns the length of the text ignoring ANSI color codes.
        Useful for proper alignment of colored text.
        """
        return len(self.ANSI_ESCAPE.sub('', str(text)))

    def _get_block_width(self, block):
        """
        Calculates the required width of a block based on the longest line
        plus the internal block padding.
        """
        max_len = max(self._str_len(line) for line in block['lines'])
        return max_len + self.block_padding * 2

    def _align_text(self, text, width, align):
        """
        Aligns a single line of text within the given width.
        - text: The string to align
        - width: Total width available for alignment
        - align: Alignment type ('left', 'center', 'right')
        Returns the padded string according to alignment.
        """
        text_len = self._str_len(text)
        space = width - text_len
        if align == 'left':
            return ' ' * self.block_padding + text + ' ' * (space - self.block_padding)
        elif align == 'right':
            return ' ' * (space - self.block_padding) + text + ' ' * self.block_padding
        else:  # center alignment
            left = space // 2
            right = space - left
            return ' ' * left + text + ' ' * right

    def display(self):
        """
        Generates the table as a string with all blocks and borders.
        Does not print directly; returns the full string.
        Handles:
        - Parent border
        - Colored block borders
        - Alignment of text
        - Proper spacing/padding
        """
        output = []

        # Determine widths for all blocks
        block_widths = [self._get_block_width(b) for b in self.blocks]
        inner_width = max(block_widths)  # Max width of blocks
        total_width = inner_width + self.parent_padding * 2  # Total width including parent padding
        chars = self.theme.chars
        pc = self.theme.parent_color

        # Parent top border
        if self.parent_border:
            output.append(pc + chars['top_left'] + chars['horizontal']*(total_width+2) + chars['top_right'])

        for block in self.blocks:
            left_pad = ' ' * self.parent_padding if self.parent_border else ''
            bc = block['color']

            # Top border of block with block_color
            output.append((pc + '║'+left_pad if self.parent_border else '') +
                          bc + chars['top_left'] + bc + chars['horizontal']*inner_width + bc + chars['top_right'] +
                          (pc + left_pad+'║' if self.parent_border else ''))

            # Block content
            for line in block['lines']:
                # If the line already has color, do not override with block_color
                colored_line = line if self.ANSI_ESCAPE.search(line) else line
                content = self._align_text(colored_line, inner_width, block['align'])
                output.append((pc + '║'+left_pad if self.parent_border else '') +
                              bc + chars['vertical'] + content + bc + chars['vertical'] +
                              (pc + left_pad+'║' if self.parent_border else ''))

            # Bottom border of block with block_color
            output.append(('║'+left_pad if self.parent_border else '') +
                          bc + chars['bottom_left'] + bc + chars['horizontal']*inner_width + bc + chars['bottom_right'] +
                          (pc + left_pad+'║' if self.parent_border else ''))

        # Parent bottom border
        if self.parent_border:
            output.append(pc + chars['bottom_left'] + chars['horizontal']*(total_width+2) + chars['bottom_right'])

        # Return the full table string
        return '\n'.join(output)

    def build_list(self):
        """
        Generates the table as a list of strings (each string is a line).
        This is similar to display(), but returns a list instead of a single string.
        """
        output = []

        # Determine widths for all blocks
        block_widths = [self._get_block_width(b) for b in self.blocks]
        inner_width = max(block_widths)  # Max width of blocks
        total_width = inner_width + self.parent_padding * 2  # Total width including parent padding
        chars = self.theme.chars
        pc = self.theme.parent_color

        # Parent top border
        if self.parent_border:
            output.append(pc + chars['top_left'] + chars['horizontal']*(total_width+2) + chars['top_right'])

        for block in self.blocks:
            left_pad = ' ' * self.parent_padding if self.parent_border else ''
            bc = block['color']

            # Top border of block with block_color
            output.append((pc + '║'+left_pad if self.parent_border else '') +
                          bc + chars['top_left'] + bc + chars['horizontal']*inner_width + bc + chars['top_right'] +
                          (pc + left_pad+'║' if self.parent_border else ''))

            # Block content
            for line in block['lines']:
                # If the line already has color, do not override with block_color
                colored_line = line if self.ANSI_ESCAPE.search(line) else line
                content = self._align_text(colored_line, inner_width, block['align'])
                output.append((pc + '║'+left_pad if self.parent_border else '') +
                              bc + chars['vertical'] + content + bc + chars['vertical'] +
                              (pc + left_pad+'║' if self.parent_border else ''))

            # Bottom border of block with block_color
            output.append(('║'+left_pad if self.parent_border else '') +
                          bc + chars['bottom_left'] + bc + chars['horizontal']*inner_width + bc + chars['bottom_right'] +
                          (pc + left_pad+'║' if self.parent_border else ''))

        # Parent bottom border
        if self.parent_border:
            output.append(pc + chars['bottom_left'] + chars['horizontal']*(total_width+2) + chars['bottom_right'])

        return output
    
    def display_plain(self):
        """
        Generates the table as a plain string (without any ANSI escape codes or colors).
        """
        colored_output = self.display()
        # Remove ANSI Codes
        plain_output = self.ANSI_ESCAPE.sub('', colored_output)
        return plain_output