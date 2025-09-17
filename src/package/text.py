"""
Text module that merges psiutils.text.strings with project-level strings.

Usage:
    from text_module import Text

    txt = Text()
    print(txt.SELECT)   # Access as attribute
    print(txt.DELETE_PROMPT)
"""

from dataclasses import dataclass, field
from psiutils.text import strings as psi_strings

strings = {
    'SELECT': 'Select',
    'ACCEPT': 'Accept',
    'DELETE_PROMPT': 'Are you sure you wish to delete this record?',
    'CONFIG': 'Preferences',
    'NOT_IN_PROJECT_DIR': 'Not working in project\'s directory',
    'EDIT_SCRIPT': 'Edit script',
    'RUN_SCRIPT': 'Run script',
}


@dataclass
class Text:
    """Combines package-level (psiutils) and project-level strings.

    Attributes from `psiutils.text.strings` are loaded first, then overridden
    or extended by the local `strings` dictionary.
    """

    display: bool = field(default=False, repr=False)

    def __post_init__(self) -> None:
        """Populate the dataclass instance with string attributes."""
        # Load psiutils strings
        for key, string in psi_strings.items():
            setattr(self, key, string)

        # Override or add project-level strings
        for key, string in strings.items():
            setattr(self, key, string)

        # Optionally display contents of `text`
        if self.display:
            for item in sorted(list(psi_strings)):
                output = f'{item}, {psi_strings[item]}'
                if item in strings:
                    if psi_strings[item] != strings[item]:
                        output = f'{output}, {strings[item]} ***'
                    else:
                        output = f'{output} <{"="*10} //duplicate//'
                print(output)
