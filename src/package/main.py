"""Main procedure for package"""
from pathlib import Path

from psiutils.icecream_init import ic_init

from package.modules import check_imports
from package.root import Root

ic_init()


def main() -> None:
    """Call the Root loop."""
    check_imports('package', Path(__file__).parent)
    Root()


if __name__ == '__main__':
    main()
