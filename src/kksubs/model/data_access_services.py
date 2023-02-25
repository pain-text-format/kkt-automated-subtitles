import logging
import os
from typing import List, Dict, Optional

import yaml

from kksubs.model.domain_models import MainSubtitleProfile, SubtitleGroup, SupportedImageExtensions, \
    SupportedInputTextExtensions

from kksubs.model.domain_models import get_default_font_style

from kksubs.model.converters import get_subtitle_groups_by_textpath, get_subtitle_profiles

logger = logging.getLogger(__name__)

def check_file_conflict(old_file_paths:List[str], new_file_paths:List[str]) -> bool:
    # assume the old and new file paths are equal in length.
    # if there is file conflict return True
    # else return False
    for i, new_file_path in enumerate(new_file_paths):
        if new_file_path in old_file_paths[i+1:]:
            return True

    return False

def rename_images(image_paths:List[str], input_image_directory:str, padding_length=None, start_at=None, prefix=None, suffix=None) -> List[str]:

    # ideally, come up with an algorithm that dynamically adds a suffix if there is a file naming conflict,
    # and keep adding suffixes inductively until there is no conflict.
    new_image_paths = []
    for i, image_path in enumerate(image_paths):
        extension = os.path.splitext(image_path)[1]
        image_index = str(i+start_at).rjust(padding_length, "0")
        new_basename = f"{prefix}{image_index}{suffix}{extension}"
        new_image_path = os.path.join(input_image_directory, new_basename)
        new_image_paths.append(new_image_path)

    has_conflict = check_file_conflict(image_paths, new_image_paths)
    suffix_count = 0
    while has_conflict and suffix_count <= 5:
        logger.warning("File conflict detected while performing batch renaming. Attempting to overcome conflict by appending suffix.")
        # do some stuff
        conflict_suffix = "_s" # to resolve file conflict
        for j, new_image_path in enumerate(new_image_paths):
            new_image_path_name, extension = os.path.splitext(new_image_path)
            new_image_path = f"{new_image_path_name}{conflict_suffix}{extension}"
            new_image_paths[j] = new_image_path

        has_conflict = check_file_conflict(image_paths, new_image_paths)
        suffix_count += 1

    for i, image_path in enumerate(image_paths):
        os.rename(image_path, new_image_paths[i])
    
    return new_image_paths

def update_images_in_textstring(textstring:str, image_paths:List[str], new_image_paths:List[str]=None) -> str:
    if new_image_paths is None:
        new_image_paths = image_paths

    subtitle_group_textstrings = textstring.split("image_id:")

    # get the image id
    subtitle_body_by_image_id = dict()
    for subtitle_group_text in subtitle_group_textstrings:
        if not subtitle_group_text:
            continue
        if "\n" in subtitle_group_text:
            image_id, subtitle_body = subtitle_group_text.split("\n", 1)
        else:
            image_id = subtitle_group_text.strip()
            subtitle_body = ""
        image_id = image_id.lstrip()
        subtitle_body_by_image_id[image_id] = subtitle_body.strip()

    updated_textstring = ""

    for i, image_path in enumerate(image_paths):
        image_basename = os.path.basename(image_path)
        new_image_basename = os.path.basename(new_image_paths[i])

        # this process will remove subtitles that don't point to images,
        # as well as add new images into the subtitles.
        newline_prepend = ""
        if len(updated_textstring) > 0:
            if updated_textstring[-1] != "\n":
                newline_prepend = "\n\n"
            else:
                newline_prepend = "\n"
        else:
            newline_prepend = ""
            pass

        if image_basename in subtitle_body_by_image_id.keys():
            add_line = newline_prepend + "image_id: "+new_image_basename+"\n"+subtitle_body_by_image_id[image_basename]
        else:
            add_line = f"{newline_prepend}image_id: {new_image_basename}"

        updated_textstring += add_line
    
    if len(updated_textstring) > 0 and updated_textstring[-1] != "\n":
        updated_textstring += "\n"

    return updated_textstring

def update_images_in_textpath(text_path:str, image_paths:List[str], new_image_paths:List[str]=None):
    # updates the image IDs in the draft after renaming each image.

    if not os.path.exists(text_path):
        raise FileNotFoundError(f"text path {text_path} does not exist.")
    with open(text_path, "r", encoding="utf-8") as reader:
        content = reader.read()
    updated_textstring = update_images_in_textstring(content, image_paths, new_image_paths=new_image_paths)
    with open(text_path, "w", encoding="utf-8") as writer:
        writer.write(updated_textstring)

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

    def get_subtitle_profiles(self) -> Dict[str, MainSubtitleProfile]:
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

    def generate_input_subtitle_template_for_text(self, output_path):
        # generates a simple text subtitle file in the output path.
        image_paths = self.get_image_paths()
        image_ids = list(map(lambda path:os.path.basename(path), image_paths))
        
        lines = "\n".join([f"image_id: {image_id}\n" for image_id in image_ids])
        with open(output_path, "w", encoding="utf-8") as writer:
            writer.write(lines)

    def generate_input_subtitle_template_for_yaml(self, output_path, current_yaml_input_path:str=None):
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

    def generate_input_subtitle_template(self, output_path, existing_subtitle_file:str=None):
        extension = os.path.splitext(output_path)[1]
        if extension in {".yaml", ".yml"}:
            self.generate_input_subtitle_template_for_yaml(output_path, current_yaml_input_path=existing_subtitle_file)
        if extension in {".txt"}:
            self.generate_input_subtitle_template_for_text(output_path)

    def rename_images(self, padding_length=None, start_at=None, prefix=None, suffix=None):
        # Perform image renaming so it is structured and in alphabetical order.

        image_paths = self.get_image_paths()
        image_paths.sort()
        text_paths = self.get_textpaths()

        n = len(image_paths)
        input_image_directory = self.input_image_directory

        if padding_length is None:
            padding_length = len(str(n))
        if start_at is None:
            start_at = 0

        new_image_paths = rename_images(image_paths, input_image_directory, padding_length=padding_length, start_at=start_at, prefix=prefix, suffix=suffix)
        logger.info(f"Renamed {n} images in directory {input_image_directory}.")

        for text_path in text_paths:
            text_id = os.path.basename(text_path)
            extension = os.path.splitext(text_path)[1]
            if extension != ".txt":
                logger.warning("File type not supported, skipping.")
                # raise TypeError(f"File must be text file, not {extension}.")
                continue
            
            text_path = os.path.join(self.input_text_directory, text_id)
            update_images_in_textpath(text_path, image_paths, new_image_paths=new_image_paths)

    pass