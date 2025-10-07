import argparse

class HelpFormatter(argparse.HelpFormatter):
    """Custom help formatter for consistent usage/help output aesthetics."""

    def add_usage(self, usage, actions, groups, prefix=None):
        """Render usage text with explicit prefix handling."""
        if prefix is None:
            prefix = ''
        return super(HelpFormatter, self).add_usage(
            usage, actions, groups, prefix)

