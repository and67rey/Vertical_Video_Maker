# main.py

from cli import parse_args
from logger_setup import setup_logging
from runner import run_vvm


def main():
    logger = setup_logging()
    args = parse_args()
    run_vvm(args)


if __name__ == "__main__":
    main()
