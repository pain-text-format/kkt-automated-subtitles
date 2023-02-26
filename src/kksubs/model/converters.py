import json
import os
from typing import Dict, List, Optional
import logging
import re

import yaml

logger = logging.getLogger(__name__)

# convert and delegate

from kksubs.model.domain_models import AssetData, LayerData, SubtitleProfile, FontData, OutlineData, TextboxData, Subtitle, SubtitleGroup


def _get_subtitle_profile_from_dict(subtitle_profile_dict:Dict, subtitle_profiles:Dict[str, SubtitleProfile]=None, is_orbit=None) -> SubtitleProfile:
    if is_orbit is None:
        is_orbit = False
    
    keys = subtitle_profile_dict.keys()
    subtitle_profile = SubtitleProfile()

    # keys
    font_data_key = "font_data"
    outline_data_1_key = "outline_data_1"
    outline_data_2_key = "outline_data_2"
    textbox_data_key = "textbox_data"
    subtitle_id_key = "subtitle_profile_id"
    layer_data_key = "layer_data"
    asset_data_key = "asset_data"
    default_text_key = "default_text"

    if font_data_key in keys:
        font_data = FontData()
        font_data_dict = subtitle_profile_dict[font_data_key]
        font_data.style = font_data_dict.get("style")
        font_data.color = font_data_dict.get("color")
        font_data.size = font_data_dict.get("size")
        font_data.stroke_color = font_data_dict.get("stroke_color")
        font_data.stroke_size = font_data_dict.get("stroke_size")
        font_data.correct_values()
        subtitle_profile.font_data = font_data
        pass
    if outline_data_1_key in keys:
        outline_data_1 = OutlineData()
        outline_data_dict = subtitle_profile_dict[outline_data_1_key]
        outline_data_1.color = outline_data_dict.get("color")
        outline_data_1.radius = outline_data_dict.get("radius")
        outline_data_1.blur_strength = outline_data_dict.get("blur_strength")
        outline_data_1.correct_values()
        subtitle_profile.outline_data_1 = outline_data_1
        pass
    if outline_data_2_key in keys:
        outline_data_2 = OutlineData()
        outline_data_dict = subtitle_profile_dict[outline_data_2_key]
        outline_data_2.color = outline_data_dict.get("color")
        outline_data_2.radius = outline_data_dict.get("radius")
        outline_data_2.blur_strength = outline_data_dict.get("blur_strength")
        outline_data_2.correct_values()
        subtitle_profile.outline_data_2 = outline_data_2
        pass
    if textbox_data_key in keys:
        textbox_data = TextboxData()
        textbox_data_dict = subtitle_profile_dict[textbox_data_key]
        textbox_data.alignment = textbox_data_dict.get("alignment")
        textbox_data.anchor_point = textbox_data_dict.get("anchor_point")
        textbox_data.box_width = textbox_data_dict.get("box_width")
        textbox_data.push = textbox_data_dict.get("push")
        textbox_data.grid4 = textbox_data_dict.get("grid4")
        textbox_data.rotate = textbox_data_dict.get("rotate")
        textbox_data.dynamic_rotate = textbox_data_dict.get("dynamic_rotate")
        textbox_data.correct_values()
        subtitle_profile.textbox_data = textbox_data
        pass
    if layer_data_key in keys:
        layer_data = LayerData()
        bdd = subtitle_profile_dict[layer_data_key]
        layer_data.brightness = bdd.get("brightness")
        layer_data.gaussian_blur = bdd.get("gaussian_blur")
        layer_data.motion_blur = bdd.get("motion_blur")
        layer_data.motion_rotate = bdd.get("motion_rotate")
        layer_data.radial_blur = bdd.get("radial_blur")
        layer_data.radial_coords = bdd.get("radial_coords")
        layer_data.f_blur = bdd.get("f_blur")
        layer_data.f_coords = bdd.get("f_coords")
        layer_data.f_radius = bdd.get("f_radius")
        layer_data.correct_values()
        subtitle_profile.layer_data = layer_data
        pass
    if asset_data_key in keys:
        asset_data = AssetData()
        asset_data_dict:Dict = subtitle_profile_dict[asset_data_key]
        asset_data.path = asset_data_dict.get("path")
        asset_data.coords = asset_data_dict.get("coords")
        asset_data.scale = asset_data_dict.get("scale")
        asset_data.rotate = asset_data_dict.get("rotate")
        subtitle_profile.asset_data = asset_data

    if default_text_key in keys:
        subtitle_profile.default_text = subtitle_profile_dict.get(default_text_key)
        pass
    if subtitle_id_key in keys:
        subtitle_profile.subtitle_profile_id = subtitle_profile_dict.get(subtitle_id_key)
        pass

    # check if the profile ID represents that of a child.
    # if the profile represents a child, then it should inherit from the parent.
    subtitle_profile_id = subtitle_profile.subtitle_profile_id
    parent_profile_id_list = _get_parent_profile_id_list(subtitle_profile_id)

    for parent_profile_id in parent_profile_id_list:
        parent_profile_id = parent_profile_id.strip()
        if parent_profile_id:
            if parent_profile_id not in subtitle_profiles.keys():
                raise KeyError(f"Subtitle profile with ID {parent_profile_id} does not exist as parent for child {subtitle_profile_id}.")
            parent_subtitle_profile = subtitle_profiles.get(parent_profile_id)
            subtitle_profile.add_default(parent_subtitle_profile)
            subtitle_profile.subtitle_profile_id = subtitle_profile_id.split("(")[0]

    # check for orbits.
    if not is_orbit:
        orbits = subtitle_profile_dict.get("orbits")
        if orbits is not None and len(orbits) > 0:
            subtitle_profile.orbits = list()
            for orbit in orbits:
                orbit_subtitle_profile = _get_subtitle_profile_from_dict(orbit, subtitle_profiles=subtitle_profiles, is_orbit=True)
                subtitle_profile.orbits.append(orbit_subtitle_profile)
    else: # if is orbit
        subtitle_profile.centrix = subtitle_profile_dict.get("centrix")

    return subtitle_profile


def _inject_subtitle_profile_data(subtitle:Subtitle, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:Optional[str]=None):
    # assume subtitle has local profile information.
    if subtitle.subtitle_profile is None:
        subtitle.subtitle_profile = SubtitleProfile()

    # check if default profile ID exists --> get default profile.
    # else, use global subtitle profile.

    if subtitle_profiles is not None and default_profile_id is not None:
        if default_profile_id in subtitle_profiles.keys():
            default_profile = SubtitleProfile()
            default_profile.add_default(subtitle_profiles[default_profile_id])
        else:
            logger.warning(f"The default subtitle with ID {default_profile_id} is not found: Using global default.")
            default_profile = SubtitleProfile()
    else:
        default_profile = SubtitleProfile()
    default_profile.add_default()

    # check if subtitle profile ID exists, if exist --> get from subtitle profiles.
    # else, use default profile.
    if subtitle_profiles is not None and subtitle.subtitle_profile_id is not None:
        if subtitle.subtitle_profile_id in subtitle_profiles.keys():
            subtitle_profile = subtitle_profiles[subtitle.subtitle_profile_id]
        else:
            logger.warning(f"The subtitle profile with ID {subtitle.subtitle_profile_id} is not found: Using global default.")
            subtitle_profile = SubtitleProfile()
    else:
        subtitle_profile = SubtitleProfile()
    subtitle_profile.add_default(default_profile)

    # orbit data.
    orbits = subtitle_profile.orbits
    if orbits is not None and len(orbits) > 0:
        for orbit in orbits:
            orbit.add_default(default_profile)

    subtitle.subtitle_profile.add_default(subtitle_profile)


def _get_subtitle_from_dict(subtitle_json:Dict, subtitle_profiles:Dict[str, SubtitleProfile]=None, default_profile_id:str=None) -> Subtitle:
    """
    Extract Subtitle data from a JSON dict representing a Subtitle.
    Profile priority: local profile data overrides local profile ID data overrides default profile data overrides global profile data.
    :param subtitle_json:
    :param subtitle_profiles:
    :param default_profile_id:
    :return: Subtitle
    """

    subtitle_profile_id_key = "subtitle_profile_id"
    subtitle_profile_key = "subtitle_profile"
    content_key = "content"
    subtitle = Subtitle()

    if subtitle_profile_id_key in subtitle_json.keys():
        subtitle.subtitle_profile_id = subtitle_json[subtitle_profile_id_key]
    subtitle.subtitle_profile = SubtitleProfile()


    if subtitle_profile_key in subtitle_json.keys():
        local_profile = _get_subtitle_profile_from_dict(subtitle_json[subtitle_profile_key])
        subtitle.subtitle_profile = local_profile

    _inject_subtitle_profile_data(subtitle, subtitle_profiles, default_profile_id)
    if content_key in subtitle_json.keys():
        subtitle.content = subtitle_json[content_key]

    return subtitle

def _get_subtitle_groups_from_dict(subtitle_groups_list:Dict, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    # keys
    image_id_key = "image_id"
    subtitle_list_key = "subtitle_list"

    subtitle_groups_by_path = dict()

    for subtitle_group_json in subtitle_groups_list:
        if image_id_key not in subtitle_group_json.keys():
            raise KeyError
        image_id = subtitle_group_json[image_id_key]
        if subtitle_list_key not in subtitle_group_json.keys():
            raise KeyError
        subtitle_group = SubtitleGroup(image_id=image_id)
        if subtitle_list_key not in subtitle_group_json.keys():
            continue
        subtitle_group.subtitle_list = []
        for subtitle_json in subtitle_group_json[subtitle_list_key]:
            subtitle_group.subtitle_list.append(_get_subtitle_from_dict(
                subtitle_json, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id
            ))
        # subtitle_group.subtitle_list = [
        #     _get_subtitle_from_dict(subtitle_json, subtitle_profiles=subtitle_profiles,
        #                             default_profile_id=default_profile_id) for subtitle_json in
        #     subtitle_group_json[subtitle_list_key]
        # ]
        subtitle_groups_by_path[image_id] = subtitle_group

    return subtitle_groups_by_path

def _get_subtitle_groups_from_json(textpath, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    with open(textpath, "r", encoding="utf-8") as reader:
        subtitle_groups_json = json.load(reader)
    return _get_subtitle_groups_from_dict(subtitle_groups_json, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)

def _get_subtitle_groups_from_yaml(textpath, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    with open(textpath, "r", encoding="utf-8") as reader:
        subtitle_groups_json = yaml.safe_load(reader)
    return _get_subtitle_groups_from_dict(subtitle_groups_json, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)


text_profile_features_by_keys = {
    "font_data": ["style", "color", "size", "stroke_color", "stroke_size"],
    "outline_data_1": ["color", "radius", "blur_strength"],
    "outline_data_2": ["color", "radius", "blur_strength"],
    "textbox_data": ["alignment", "anchor_point", "box_width", "grid4", "push", "rotate", "dynamic_rotate"],
    "layer_data": [
        "brightness", 
        "gaussian_blur", 
        "motion_blur", "motion_rotate", 
        "radial_blur", "radial_coords",
        "f_blur", "f_radius", "f_coords",
    ],
    "asset_data": ["path", "coords", "scale", "rotate"]
}


def _get_profile_data_type_feature_and_value(line:str):
    # examples:
    # font_data.style: abc --> font_data, style, abc
    # outline_data_1.color: red --> outline_data_1, color, red

    if line.startswith("subtitle_profile_id:"):
        return "subtitle_profile_id", "subtitle_profile_id", line.split(":", 1)[1].lstrip()

    for data_type in text_profile_features_by_keys.keys():
        for feature in text_profile_features_by_keys[data_type]:
            formatted_feature = f"{data_type}.{feature}"
            if line.lower().startswith(formatted_feature):
                value = line.split(":", 1)[1].lstrip()
                return data_type, feature, value

    return None, None, None


def _add_text_data_to_subtitle(subtitle: Subtitle, line:str) -> Subtitle:
    # extracts profile-related data from a line of text, and adds it to the subtitle appropriately.
    # first check if it is a profile ID field.
    data_type, attribute, value = _get_profile_data_type_feature_and_value(line)
    if attribute is None:
        return subtitle

    if subtitle.subtitle_profile is None:
        subtitle.subtitle_profile = SubtitleProfile()
    if data_type == "subtitle_profile_id":
        subtitle.subtitle_profile_id = value
        return subtitle

    elif data_type == "font_data":
        if subtitle.subtitle_profile.font_data is None:
            subtitle.subtitle_profile.font_data = FontData()
        setattr(subtitle.subtitle_profile.font_data, attribute, value)
        subtitle.subtitle_profile.font_data.correct_values()
        return subtitle
    elif data_type == "outline_data_1":
        if subtitle.subtitle_profile.outline_data_1 is None:
            subtitle.subtitle_profile.outline_data_1 = OutlineData()
        setattr(subtitle.subtitle_profile.outline_data_1, attribute, value)
        subtitle.subtitle_profile.outline_data_1.correct_values()
        return subtitle
    elif data_type == "outline_data_2":
        if subtitle.subtitle_profile.outline_data_2 is None:
            subtitle.subtitle_profile.outline_data_2 = OutlineData()
        setattr(subtitle.subtitle_profile.outline_data_2, attribute, value)
        subtitle.subtitle_profile.outline_data_2.correct_values()
        return subtitle
    elif data_type == "textbox_data":
        if subtitle.subtitle_profile.textbox_data is None:
            subtitle.subtitle_profile.textbox_data = TextboxData()
        setattr(subtitle.subtitle_profile.textbox_data, attribute, value)
        subtitle.subtitle_profile.textbox_data.correct_values()
        return subtitle
    elif data_type == "layer_data":
        if subtitle.subtitle_profile.layer_data is None:
            subtitle.subtitle_profile.layer_data = LayerData()
        setattr(subtitle.subtitle_profile.layer_data, attribute, value)
        subtitle.subtitle_profile.layer_data.correct_values()
        return subtitle
    elif data_type == "asset_data":
        if subtitle.subtitle_profile.asset_data is None:
            subtitle.subtitle_profile.asset_data = AssetData()
        setattr(subtitle.subtitle_profile.asset_data, attribute, value)
        subtitle.subtitle_profile.asset_data.correct_values()
        return subtitle
    raise

def get_profile_alias(line:str, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None):
    if subtitle_profiles is None:
        return None
    for profile_id in subtitle_profiles.keys():
        if line.startswith(f"{subtitle_profiles[profile_id].subtitle_profile_id}:"):
            return profile_id
    return None

def get_default_subtitle_profile(subtitle_profiles:Dict[str, SubtitleProfile], default_profile_id:str=None):
    if subtitle_profiles is not None and default_profile_id in subtitle_profiles.keys():
        default_profile = subtitle_profiles[default_profile_id]
    else:
        default_profile = SubtitleProfile()
    default_profile.add_default()
    return default_profile

def _get_subtitle_groups_from_textstring(textstring:str, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    # to prevent repetition and overriding existing subtitles, send the user warnings when there are dupe image IDs.
    image_id_to_line_number = dict()
    
    lines = textstring.split("\n")
    subtitle_groups_by_path = dict()

    subtitle_group = SubtitleGroup(subtitle_list=[])
    subtitle = Subtitle(content=[])
    default_profile = get_default_subtitle_profile(subtitle_profiles, default_profile_id=default_profile_id)
    default_profile.add_default(SubtitleProfile.get_default())

    is_profile_environment = False
    is_content_environment = False
    is_empty = False
    empty_strings = []

    for i, line in enumerate(lines):
        profile_alias = get_profile_alias(line, subtitle_profiles=subtitle_profiles)
        if line.lower().startswith("image_id:"):
            image_id = line.split(":")[1].lstrip()

            # duplicate handling.
            if image_id in image_id_to_line_number.keys():
                logger.warning(f"Found duplicate subtitle data for image ID {image_id}. Duplicate line numbers: {i+1}, {image_id_to_line_number[image_id]+1}")
            image_id_to_line_number[image_id] = i

            subtitle_group.image_id = image_id
            is_content_environment = False
            is_profile_environment = True
        elif line.lower().startswith("content:") or profile_alias is not None:
            is_content_environment = True
            is_profile_environment = False
            line = line.split(":", 1)[1].lstrip()

        # local profile properties start from after image_id and end before content environment.
        if profile_alias is not None:
            subtitle.subtitle_profile_id = profile_alias
            subtitle = _add_text_data_to_subtitle(subtitle, line)
        if is_profile_environment:
            subtitle = _add_text_data_to_subtitle(subtitle, line)

        # adding from a content environment
        if is_content_environment:
            if line == "":
                is_empty = True
                empty_strings.append("")
                if i+1<len(lines):
                    data_type, feature, value = _get_profile_data_type_feature_and_value(lines[i+1])
                    if data_type is not None or lines[i+1].lower().startswith("content:") or lines[i+1].lower().startswith("image_id:"):
                        empty_strings = []
            else:
                if is_empty:
                    subtitle.content.extend(empty_strings)
                    empty_strings = []
                    is_empty = False
                subtitle.content.append(line)

        # conditions for adding subtitle/subtitle_group
        # last part.
        if i+1==len(lines) and subtitle_group.image_id is not None:
            _inject_subtitle_profile_data(subtitle, subtitle_profiles, default_profile_id)
            if subtitle.subtitle_profile.font_data is None:
                raise TypeError(f"Subtitle profile error: {subtitle.subtitle_profile.__dict__}")
            subtitle.subtitle_profile.add_default()
            subtitle_group.subtitle_list.append(subtitle)
            empty_strings = []
            subtitle_groups_by_path[subtitle_group.image_id] = subtitle_group

        if i+1<len(lines):
            # subtitle: the current subtitle environment ends when the next line is content or a file for subtitle profile.
            next_profile_alias = get_profile_alias(lines[i+1], subtitle_profiles=subtitle_profiles)
            if is_content_environment and i+1<len(lines) and (lines[i+1].lower().startswith("content:") or next_profile_alias is not None):
                _inject_subtitle_profile_data(subtitle, subtitle_profiles, default_profile_id)
                if subtitle.subtitle_profile.font_data is None:
                    raise TypeError(f"Subtitle profile error: {subtitle.subtitle_profile.__dict__}")
                subtitle.subtitle_profile.add_default()
                subtitle_group.subtitle_list.append(subtitle)
                empty_strings = []
                subtitle = Subtitle(content=[], subtitle_profile=SubtitleProfile())

            data_type, feature, value = _get_profile_data_type_feature_and_value(lines[i+1])
            if is_content_environment and i+1<len(lines) and data_type is not None:
                is_content_environment = False
                is_profile_environment = True
                _inject_subtitle_profile_data(subtitle, subtitle_profiles, default_profile_id)
                if subtitle.subtitle_profile.font_data is None:
                    raise TypeError(f"Subtitle profile error: {subtitle.subtitle_profile.__dict__}")
                subtitle.subtitle_profile.add_default()
                subtitle_group.subtitle_list.append(subtitle)
                empty_strings = []
                subtitle = Subtitle(content=[], subtitle_profile=SubtitleProfile())

            # subtitle group
            elif i+1<len(lines) and lines[i+1].lower().startswith("image_id:") and subtitle_group.image_id is not None:
                _inject_subtitle_profile_data(subtitle, subtitle_profiles, default_profile_id)
                subtitle.subtitle_profile.add_default()
                subtitle_group.subtitle_list.append(subtitle)
                empty_strings = []
                subtitle_groups_by_path[subtitle_group.image_id] = subtitle_group
                subtitle_group = SubtitleGroup(subtitle_list=[])
                subtitle = Subtitle(content=[], subtitle_profile=SubtitleProfile())

        pass

    return subtitle_groups_by_path

def _get_subtitle_groups_from_text(textpath, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    # limited functionality for text files. possibly more buggy.
    with open(textpath, "r", encoding="utf-8") as reader:
        textstring = reader.read()
    return _get_subtitle_groups_from_textstring(textstring, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)


def get_subtitle_groups_by_textpath(textpath, subtitle_profiles:Optional[Dict[str, SubtitleProfile]]=None, default_profile_id:str=None) -> Dict[str, SubtitleGroup]:
    extension = os.path.splitext(textpath)[1]
    if extension == ".json":
        result = _get_subtitle_groups_from_json(textpath, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)
    if extension in {".yml", ".yaml"}:
        result = _get_subtitle_groups_from_yaml(textpath, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)
    if extension == ".txt":
        result = _get_subtitle_groups_from_text(textpath, subtitle_profiles=subtitle_profiles, default_profile_id=default_profile_id)
    # validate_subtitle_groups(result)
    return result

def _get_parent_profile_id_list(child_profile_id) -> List[str]:
    # returns parent profile ID or None.
    match = re.search(r'\((.*?)\)', child_profile_id)
    if match:
        return match.group(1).split(",")
    return []

def get_subtitle_profiles(subtitle_profile_path) -> Dict[str, SubtitleProfile]:
    # deserialize a list of subtitle profile paths.
    extension = os.path.splitext(subtitle_profile_path)[1]
    if extension == ".json":
        with open(subtitle_profile_path, "r", encoding="utf-8") as reader:
            subtitle_profile_list_dict = json.load(reader)
    if extension in {".yml", ".yaml"}:
        with open(subtitle_profile_path, "r", encoding="utf-8") as reader:
            subtitle_profile_list_dict = yaml.safe_load(reader)

    subtitle_profiles = dict()
    for subtitle_profile_json in subtitle_profile_list_dict:
        subtitle_profile = _get_subtitle_profile_from_dict(subtitle_profile_json, subtitle_profiles=subtitle_profiles)
        subtitle_profiles[subtitle_profile.subtitle_profile_id] = subtitle_profile
    
    return subtitle_profiles
