import json
import logging

from kksubs.model.data_access_services import SubtitleDataAccessService
from kksubs.model.subtitle_services import SubtitleService

logger = logging.getLogger(__name__)

class SubtitleController:

    def __init__(self, subtitle_model:SubtitleDataAccessService=None, subtitle_service:SubtitleService=None):
        if subtitle_model is None and subtitle_service is None:
            subtitle_model = SubtitleDataAccessService()
        if subtitle_service is None:
            subtitle_service = SubtitleService(subtitle_model=subtitle_model)

        self.subtitle_model = subtitle_model
        self.subtitle_service = subtitle_service

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
        with open(filepath, "r") as json_file:
            configs = json.load(json_file)

        input_text_directory = configs["input_text_directory"]
        input_image_directory = configs["input_image_directory"]
        output_directory = configs["output_directory"]

        self.load_input_text_directory(input_text_directory)
        self.load_input_image_directory(input_image_directory)
        self.load_output_directory(output_directory)

        if "subtitle_profile_path" in configs.keys():
            subtitle_profile_path = configs["subtitle_profile_path"]  # may not exist
            self.load_subtitle_profiles(subtitle_profile_path)

            if "default_subtitle_profile_id" in configs.keys():
                self.load_default_subtitle_profile_id(configs["default_subtitle_profile_id"])

    def create_yaml_template(self, filename, existing_filename:str=None):
        # Creates an appropriately formatted text file in the input text directory for the user to work on.
        self.subtitle_model.generate_yaml_subtitle_template(filename, current_yaml_input_path=existing_filename)
        pass

    def add_subtitles(self):
        self.subtitle_service.add_subtitles()

    pass
