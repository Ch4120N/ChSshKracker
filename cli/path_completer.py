# -*- UTF-8 -*-
# cli/path_completer.py

import os
from prompt_toolkit.completion import Completer, Completion


class PathCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if not any(sep in text for sep in (os.sep, '/', '\\')) and not text.startswith('~'):
            text = os.path.join('.', text)

        if text.startswith("~"):
            text = os.path.expanduser(text)

        dirname = os.path.dirname(text) or '.'
        basename = os.path.basename(text)

        try:
            entries = os.listdir(dirname)
        except Exception:
            return

        matches = []
        for entry in entries:
            if entry.startswith(basename):
                full_path = os.path.join(dirname, entry)
                completion = entry
                if os.path.isdir(full_path):
                    completion += os.sep
                matches.append(completion)

        matches.sort()
        for match in matches:
            yield Completion(match, start_position=-len(basename))
