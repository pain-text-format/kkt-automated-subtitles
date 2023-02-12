import logging
import os
from typing import List, Dict

import yaml

from kksubs.model.converters import get_subtitle_groups_by_textpath, get_subtitle_profiles
from kksubs.model.domain_models import SubtitleProfile, SubtitleGroup, SupportedImageExtensions, \
    SupportedInputTextExtensions

from kksubs.model.domain_models import get_default_font_style

logger = logging.getLogger(__name__)

class SubtitleDataAccessService:

    def __init__(
            self, input_text_directory=None, input_image_directory=None, output_directory=None,
            subtitle_profile_path=None, default_subtitle_profile_id=None, default_subtitle_style=None
    ):
        self.input_text_directory = input_text_directory
        self.input_image_directory = input_image_directory
        self.output_directory = output_directory
        self.subtitle_profile_path = subtitle_profile_path
        self.default_subtitle_profile_id = default_subtitle_profile_id
        self.default_subtitle_style = default_subtitle_style

    def set_input_image_directory(self, input_image_directory):
        if not os.path.exists(input_image_directory):
            raise FileNotFoundError(f"Image input directory {input_image_directory} does not exist.")
        self.input_image_directory = input_image_directory

    def set_input_text_directory(self, input_text_directory):
        if not os.path.exists(input_text_directory):
            raise FileNotFoundError(f"Text input directory {input_text_directory} does not exist.")
        self.input_text_directory = input_text_directory

    def set_output_directory(self, output_directory):
        if not os.path.exists(output_directory):
            raise FileNotFoundError(f"Output directory {output_directory} does not exist.")
        self.output_directory = output_directory

    def set_subtitle_profile_path(self, subtitle_profile_path):
        if not os.path.exists(subtitle_profile_path):
            raise FileNotFoundError(f"Subtitle profile path {subtitle_profile_path} does not exist.")
        self.subtitle_profile_path = subtitle_profile_path

    def get_textpaths(self) -> List[str]:
        if not os.path.exists(self.input_text_directory):
            raise FileNotFoundError(f"Input text directory {self.input_text_directory} does not exist.")
        input_text_paths = os.listdir(self.input_text_directory)
        filtered_paths = list(filter(lambda path: SupportedInputTextExtensions.get_is_supported(path), input_text_paths))
        correct_paths = list(map(lambda filtered_path:os.path.join(self.input_text_directory, filtered_path), filtered_paths))
        return correct_paths

    def get_subtitle_groups_by_textpath(self, textpath, subtitle_profiles=None, default_profile_id=None) -> Dict[str, SubtitleGroup]:
        if subtitle_profiles is None:
            subtitle_profiles = self.get_subtitle_profiles()
        if default_profile_id is None:
            default_profile_id = self.default_subtitle_profile_id
        return get_subtitle_groups_by_textpath(textpath, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)

    def get_subtitle_groups(self) -> Dict[str, Dict[str, SubtitleGroup]]:
        if self.default_subtitle_style is None:
            logger.warning(f"A default subtitle style/font has not been specified, using the sample font {get_default_font_style()} instead.")
        result = {
            textpath: self.get_subtitle_groups_by_textpath(textpath) for textpath in self.get_textpaths()
        }
        return result

    def get_image_paths(self) -> List[str]:
        if not os.path.exists(self.input_image_directory):
            raise FileNotFoundError(f"Input image directory {self.input_image_directory} does not exist.")

        regular_file_paths = os.listdir(self.input_image_directory)
        image_ids = list(filter(lambda path:SupportedImageExtensions.get_is_supported(path), regular_file_paths))
        image_paths = list(map(lambda image_id:os.path.join(self.input_image_directory, image_id), image_ids))
        return image_paths

    def get_subtitle_profiles(self) -> Dict[str, SubtitleProfile]:
        if self.subtitle_profile_path is not None:
            if not os.path.exists(self.subtitle_profile_path):
                raise FileExistsError(f"Subtitle profile path {self.subtitle_profile_path} does not exist.")
            return get_subtitle_profiles(self.subtitle_profile_path)
        return None

    def set_default_subtitle_profile_id(self, profile_id):
        if self.get_subtitle_profiles() is None:
            raise KeyError("Currently there are no subtitle profiles associated with this application.")
        if profile_id not in self.get_subtitle_profiles().keys():
            raise KeyError(f"profile ID {profile_id} not in subtitle profiles located in {self.subtitle_profile_path}")
        self.default_subtitle_profile_id = profile_id

    def set_default_subtitle_style(self, subtitle_style):
        if not os.path.exists(subtitle_style):
            raise FileExistsError(f"The subtitle style {subtitle_style} does not exist.")
        self.default_subtitle_style = subtitle_style

    def generate_yaml_subtitle_template(self, output_path, current_yaml_input_path:str=None):
        # generates a YAML subtitle template to the output path.
        # if a path to existing YAML input file is found, will generate a YAML based on the current input data.

        image_paths = self.get_image_paths()
        image_ids = list(map(lambda path:os.path.basename(path), image_paths))
        image_ids.sort()

        index_by_image_ids = {
            image_id:i for i, image_id in enumerate(image_ids)
        }
        subtitle_group_list = [
            {
                "image_id": image_id,
                "subtitle_list": [{"content": [""]}]
            } for image_id in image_ids
        ]

        # overwrite template with current YAML data.
        if current_yaml_input_path is not None:
            if not os.path.exists(current_yaml_input_path):
                logger.warning(f"Cannot find existing YAML input path {current_yaml_input_path}.")
            else:
                with open(current_yaml_input_path, "r", encoding="utf-8") as yaml_writer:
                    current_yaml_input:List[Dict] = yaml.safe_load(yaml_writer)
                for subtitle_group_dict in current_yaml_input:
                    image_id = subtitle_group_dict.get("image_id")
                    if not image_id in index_by_image_ids.keys():
                        continue
                    index_by_image_id = index_by_image_ids[image_id]
                    subtitle_group_list[index_by_image_id] = subtitle_group_dict

        with open(output_path, "w", encoding="utf-8") as yaml_writer:
            yaml.dump(subtitle_group_list, yaml_writer, default_flow_style=False)

    pass