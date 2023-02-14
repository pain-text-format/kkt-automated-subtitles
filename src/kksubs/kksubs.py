import json
import logging
import os

import yaml

from kksubs.model.data_access_services import SubtitleDataAccessService
from kksubs.model.subtitle_services import SubtitleService

logger = logging.getLogger(__name__)

def _get_config_file_dict(filepath):
    extension = os.path.splitext(filepath)[1]
    if extension in {".json"}:
        with open(filepath, "r", encoding="utf-8") as json_reader:
            content = json.load(json_reader)
    elif extension in {".yml", ".yaml"}:
        with open(filepath, "r", encoding="utf-8") as yaml_reader:
            content = yaml.safe_load(yaml_reader)
    else:
        raise TypeError(f"Invalid file type for config: {filepath}")
    return content

class SubtitleController:

    def __init__(self, subtitle_model:SubtitleDataAccessService=None, subtitle_service:SubtitleService=None):
        logger.info("Starting session with new controller.")
        if subtitle_model is None and subtitle_service is None:
            subtitle_model = SubtitleDataAccessService()
        if subtitle_service is None:
            subtitle_service = SubtitleService(subtitle_model=subtitle_model)

        self.subtitle_model = subtitle_model
        self.subtitle_service = subtitle_service
        logger.info("Session started.")

    # load methods save the inputs or metadata into the current session for future use.
    def load_input_text_directory(self, directory):
        logger.info(f"Loaded input text directory: {directory}.")
        self.subtitle_model.set_input_text_directory(directory)

    def load_input_image_directory(self, directory):
        logger.info(f"Loaded input image directory: {directory}.")
        self.subtitle_model.set_input_image_directory(directory)

    def load_output_directory(self, directory):
        logger.info(f"Loaded output directory: {directory}.")
        self.subtitle_model.set_output_directory(directory)

    def load_subtitle_profiles(self, filepath):
        logger.info(f"Loaded subtitle profile: {filepath}.")
        self.subtitle_model.set_subtitle_profile_path(filepath)

    def load_default_subtitle_profile_id(self, default_subtitle_profile_id):
        logger.info(f"Loaded default subtitle profile ID: {default_subtitle_profile_id}.")
        self.subtitle_model.set_default_subtitle_profile_id(default_subtitle_profile_id)

    def load_configs(self, filepath):
        configs_dict = _get_config_file_dict(filepath)

        input_text_directory = configs_dict["input_text_directory"]
        input_image_directory = configs_dict["input_image_directory"]
        output_directory = configs_dict["output_directory"]

        self.load_input_text_directory(input_text_directory)
        self.load_input_image_directory(input_image_directory)
        self.load_output_directory(output_directory)

        if "subtitle_profile_path" in configs_dict.keys() and configs_dict["subtitle_profile_path"] is not None:
            subtitle_profile_path = configs_dict["subtitle_profile_path"]  # may not exist
            self.load_subtitle_profiles(subtitle_profile_path)

            if "default_subtitle_profile_id" in configs_dict.keys() and configs_dict["default_subtitle_profile_id"] is not None:
                self.load_default_subtitle_profile_id(configs_dict["default_subtitle_profile_id"])

    def create_config_template(self, filepath=None):
        # creates a config template.
        if filepath is None:
            logger.warning(f"Filename for config template was not specified; creating a config.yaml in the current directory.")
            filepath = "config.yaml"

        config_dict = {
            "input_text_directory": None,
            "input_image_directory": None,
            "output_directory": None,
            "subtitle_profile_path": None,
            "default_subtitle_profile_id": None,
        }
        with open(filepath, "w", encoding="utf-8") as yamlwriter:
            yaml.dump(config_dict, yamlwriter, default_flow_style=False, sort_keys=False)

    def create_subtitle_profile_template(self, filepath=None):
        if filepath is None:
            logger.warning(f"Filename for subtitle profile was not specified; creating subtitle_profile.yaml in the current directory.")
            filepath = "subtitle_profiles.yaml"
            
        subtitle_profile_array = [
            {
                "subtitle_profile_id": None,
                "font_data": None,
                "outline_data_1": None,
                "outline_data_2": None,
                "textbox_data": None,
            }
        ]
        with open(filepath, "w", encoding="utf-8") as yamlwriter:
            yaml.dump(subtitle_profile_array, yamlwriter, default_flow_style=False, sort_keys=False)

    def generate_input_subtitle_template(self, filename, existing_filename:str=None):
        # Creates an appropriately formatted text file in the input text directory for the user to work on.
        self.subtitle_model.generate_input_subtitle_template(filename, existing_subtitle_file=existing_filename)
        pass

    def rename_images(self, padding_length:int=None, start_at:int=None):
        # Perform image refactoring, such as renaming image names, in the input image directory.
        # Defaults to 1.png, 2.png, and so on...
        self.subtitle_service.rename_images(padding_length=padding_length, start_at=start_at)

    def add_subtitles(self, filter_list=None):
        self.subtitle_service.add_subtitles(filter_list=filter_list)

    pass
