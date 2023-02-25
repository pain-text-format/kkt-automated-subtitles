import argparse
import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Optional

from kksubs.kksubs import SubtitleController

clear_screen_command = 'cls' if os.name == 'nt' else 'clear'

logger = logging.getLogger(__name__)

def print_header(msg):
    print(f"---------- {msg} ----------")

class Command:
    def __init__(self, name, alias, description):
        self.name = name
        self.alias = alias
        self.description = description

    def __eq__(self, other:"Command") -> bool:
        if other is not None:
            return self.name == other.name
        return False

class Window(ABC):

    def __init__(self, name, parent=None) -> None:
        self.parent = parent
        self.name = name

    def get_name(self):
        return self.name

    def show(self):
        os.system(clear_screen_command)
        print_header(self.get_name())
        pass

    def get_input(self, msg=None):
        if msg is None:
            msg = ""
        else:
            msg = ": " + msg
        return input(f"kksubs{msg} >>> ")
    
    def handle_input_exception(self, user_input:str):
        return self.handle_input(self.get_input(msg=f"Invalid command \"{user_input}\", please try again"))
    
    def show_common_help(self):
        print("- (h)elp: show help")
        print("- (r)efresh: refresh window")
        print("- (b)ack: go back")
        print("- (q)uit: quit application")
        pass

    def show_window_help(self):
        pass

    def show_help(self):
        print("")
        print_header("WINDOW COMMANDS")
        print("")
        self.show_window_help()
        print("")
        print("")
        print_header("COMMON COMMANDS")
        print("")
        self.show_common_help()
        print("")
        pass

    @abstractmethod
    def _handle_input(self, user_input) -> Optional["Window"]:
        ...
    
    def handle_input(self, user_input=None) -> Optional["Window"]:
        if user_input is None:
            user_input = self.get_input()
        if user_input.startswith("!mkdir "):
            try:
                os.makedirs(user_input.split(" ", 1)[1])
                return self
            except:
                return self.handle_input_exception(user_input)
        if user_input.startswith("!cd "):
            try:
                os.chdir(user_input.split(" ", 1)[1])
                return self
            except:
                return self.handle_input_exception(user_input)
        if user_input.startswith("!ls"):
            if user_input == "!ls":
                items = os.listdir(".")
            else:
                try:
                    items = os.listdir(os.path.join(".", user_input.split(" ", 1)[1]))
                except:
                    return self.handle_input(self.get_input(f"Failed to list directory from command \"{user_input}\""))
            print("")
            for item in items:
                print(f"- {item}")
            print("")
            return self.handle_input()
        if user_input in {"refresh", "r", "clear", "cls"}:
            return self
        if user_input in {"quit", "q", "exit"}:
            return None
        if user_input in {"back", "b"}:
            if self.parent is not None:
                return self.parent
            else:
                return self.handle_input(self.get_input("Already at main window"))
        if user_input in {"help", "h"}:
            self.show_help()
            return self.handle_input()
        return self._handle_input(user_input)

class MainWindow(Window):
    def __init__(self):
        self.setup = True
        self.projects_by_directory:Dict[str, ProjectWindow] = dict()
        super().__init__(f"Main ({os.getcwd()})")

    def get_name(self):
        return f"Main ({os.getcwd()})"

    def show(self):
        super().show() # this will show the top border.
        if self.setup:
            print("Welcome to the terminal application for kksubs!")
            print("To get started, select an option from below:")
            print("- list: list opened projects")
            print("- open [path/to/project/directory]")
            print("")
            self.setup = False
        self.show_project_list()

    def show_window_help(self):
        print("- list: list opened projects")
        print("- open [path/to/project/directory]")

    def add_project(self, directory, go_to_project=True) -> Optional[Window]:
        if not os.path.exists(directory):
            return self.handle_input(self.get_input(msg=f"Directory \"{directory}\" does not exist"))
        
        directory = os.path.realpath(directory)
        if directory not in self.projects_by_directory.keys():
            try:
                self.projects_by_directory[directory] = ProjectWindow(self, directory)
            except:
                return self.handle_input(self.get_input(f"An error occurred adding {directory} to Projects."))
        
        print(f"Successfully added project: {directory}")
        if go_to_project:
            return self.projects_by_directory[directory]
        else:
            return self.handle_input()
        
    def show_project_list(self):
        print("")
        print("Project List")
        print("")
        projects_by_directory = self.projects_by_directory
        if projects_by_directory:
            for directory in projects_by_directory.keys():
                print(f"- {directory}")
        else:
            print("- No projects opened.")
        print("")

    def _handle_input(self, user_input:str) -> Optional["Window"]:
        if user_input.startswith("add "):
            directory = user_input.split(" ", 1)[1]
            return self.add_project(directory, go_to_project=False)

        if user_input.startswith("open "):
            # perform checks.
            directory = user_input.split(" ", 1)[1]
            return self.add_project(directory)
            
        if user_input in {"list", "ls"}:
            self.show_project_list()
            return self.handle_input()
        
        return self.handle_input_exception(user_input)

class ProjectWindow(Window):
    def __init__(self, parent:MainWindow, directory:str=None, controller:SubtitleController=None):
        super().__init__(f"Project ({directory})", parent=parent)
        if controller is None:
            controller = SubtitleController()
            
        self.setup = True
        self.directory = directory
        self.controller = controller
        self.model = controller.subtitle_model
        self.parent = parent

        # load information from controller.
        logger.info(f"Attempting to load project from directory {directory}.")
        controller.load_project(directory=directory)
    
    def show_window_help(self):
        print("- list: list drafts")
        print("- open [draft_ID]")

    def show(self):
        super().show()

        input_image_directory = self.model.input_image_directory
        input_text_directory = self.model.input_text_directory
        output_directory = self.model.output_directory
        subtitle_profile_path = self.model.subtitle_profile_path

        if self.setup:
            print("SUCCESS: You've opened a kksubs project.")
            self.setup = False
        print("Project Details:\n")
        print(f"- Project name: ")
        print(f"- Input image directory: {input_image_directory}")
        print(f"- Input text directory: {input_text_directory}")
        print(f"- Output directory: {output_directory}")
        print(f"- Subtitle profile path: {subtitle_profile_path}")
        print("")

    def _handle_input(self, user_input:str) -> Optional["Window"]:
        if user_input in {"list", "ls"}:
            text_paths = self.model.get_textpaths()
            print("")
            print_header(f"List of Drafts ({self.directory})")
            for text_path in text_paths:
                print(f"- {os.path.basename(text_path)}: {text_path}")
            print("")
            return self.handle_input(self.get_input("To open a draft, enter the command \"open [draft]\"."))
        if user_input.startswith("open "):
            text_paths = self.model.get_textpaths()
            draft_id = user_input.split(" ", 1)[1].strip()
            for text_path in text_paths:
                _draft_id = os.path.basename(text_path)
                if draft_id == _draft_id:
                    return DraftWindow(self, draft_id)
            return self.handle_input(self.get_input(f"Draft ID \"{draft_id}\" does not exist"))
        return self.handle_input_exception(user_input)

# include the following commands:
# apply: applies subtitles to 
class DraftWindow(Window):
    def __init__(self, parent:ProjectWindow, draft_id:str) -> None:
        super().__init__(f"Draft ({draft_id})", parent)
        self.draft_id = draft_id
        self.parent = parent
    
    def show_window_help(self):
        print("- apply: apply subtitles")
        print("  -- index: apply subtitle to the [index]-th image.")
        print("  -- ten: apply subtitle to the 10 images after and equal to the [ten]-th image.")
        print("- out: open output directory")
    
    def show(self):
        super().show()

    def _handle_input(self, user_input:str) -> Optional["Window"]:
        if user_input in {"apply"}:
            print("Applying subtitles...")
            self.parent.controller.add_subtitles_by_text_id(self.draft_id)
            print("Subtitles applied, enter \"out\" to show in output.")
            return self.handle_input()
        if user_input.startswith("apply "):
            parser = argparse.ArgumentParser()
            parser.add_argument("-i", "--index", type=int, help="index of image to open.", default=None)
            parser.add_argument("--ten", type=int, help="apply subtitles to the 10 images after the given image index.", default=None)
            
            try:
                args = parser.parse_args(user_input.split()[1:])
            except:
                return self.handle_input_exception(user_input)

            log_level = logger.getEffectiveLevel()
            logger.setLevel(logging.INFO)
            if args.index is not None:
                self.parent.controller.add_subtitles_by_text_id(self.draft_id, filter_list=[args.index])
            elif args.ten is not None:
                self.parent.controller.add_subtitles_by_text_id(self.draft_id, filter_list=list(range(args.ten, args.ten+10)))
                pass
            
            logger.setLevel(log_level)
            return self.handle_input()

        if user_input in {"out"}:
            draft_output_directory = os.path.join(self.parent.model.output_directory, os.path.splitext(self.draft_id)[0])
            os.startfile(draft_output_directory)
            return self.handle_input()
        return self.handle_input_exception(user_input)
