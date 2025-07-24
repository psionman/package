"""Main procedure for package"""

from root import Root
from psiutils.icecream_init import ic_init
ic_init()


def main() -> None:
    """Call the Root loop."""
    Root()


if __name__ == '__main__':
    main()
