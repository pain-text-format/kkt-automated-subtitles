import argparse
import logging
from sys import platform

from kksubs.cmds.windows import MainWindow

logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        logger.info("Starting session.")
        self.current_window = MainWindow()
    
    def run(self):
        while self.current_window is not None:
            self.current_window.show()
            user_input = self.current_window.get_input()
            self.current_window = self.current_window.handle_input(user_input)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--info', type=bool, default=False)
    args = parser.parse_args()
    if args.info:
        logging.basicConfig(level=logging.INFO)

    app = Application()
    app.run()

if __name__ == "__main__":
    main()

