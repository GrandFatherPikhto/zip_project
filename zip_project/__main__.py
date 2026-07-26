# __main__.py
import sys
import logging
from pathlib import Path

from .cli import parse_args
from .config.loader import ConfigLoader
from .core.controller import Controller

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

def main():
    args = parse_args()
    setup_logging(logging.DEBUG if args.dry_run else logging.INFO)

    loader = ConfigLoader(cli_args=args)
    config = loader.load(args.config)
    config_dir = loader.config_path.parent if loader.config_path else Path.cwd()

    controller = Controller(config, config_dir)
    controller.run()

if __name__ == "__main__":
    sys.exit(main())