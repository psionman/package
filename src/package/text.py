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


class Text():
    """Combines package level and psiutils strings."""
    def __init__(self, display_duplicates: bool = False) -> None:
        """
        Initialize the object with attributes based on the key-value pairs
        in the `strings` dictionary.

        Args:
            self: The instance of the class.

        Returns:
            None
        """

        for key, string in psi_strings.items():
            setattr(self, key, string)

        for key, string in strings.items():
            setattr(self, key, string)

        if display_duplicates:
            for item in sorted(list(strings)):
                if item in psi_strings:
                    output = f'{item}, {psi_strings[item]}, {strings[item]}'
                    if psi_strings[item] != strings[item]:
                        output += ' ***'
                    print(output)
