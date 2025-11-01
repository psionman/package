list:
    just --list

run:
    uv run src/package/main.py

test arg1="":
    uv run -m pytest {{arg1}}
