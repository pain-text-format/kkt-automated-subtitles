import logging

import os
from typing import List, Optional
from kksubs.model.domain_models import FontData, LayerData, OutlineData, Subtitle, SubtitleGroup, SubtitleProfile, TextboxData

logger = logging.getLogger(__name__)

def _validate_font_data(font_data:FontData):
    if font_data is None:
        raise KeyError
    if font_data.style is None:
        raise KeyError
    if not os.path.exists(font_data.style):
        raise FileExistsError(f"Style {font_data.style} does not exist.")
    if not isinstance(font_data.color, tuple):
        raise TypeError(f"Type of font data color is {type(font_data.color)}")
    if not isinstance(font_data.stroke_color, tuple):
        raise TypeError
    
def _validate_outline_data(outline_data:OutlineData):
    if not isinstance(outline_data.radius, int):
        raise TypeError(f"{outline_data.radius} is a {type(outline_data.radius)}")

def _validate_textbox_data(textbox_data:TextboxData):
    if not isinstance(textbox_data.alignment, str):
        raise TypeError
    if not isinstance(textbox_data.box_width, int):
        raise TypeError(f"Textbox width {textbox_data.box_width} is of type {type(textbox_data.box_width)}, not int.")

def _validate_layer_data(layer_data:LayerData):
    if layer_data.background_path is not None:
        if not os.path.exists(layer_data.background_path):
            raise FileNotFoundError(layer_data.background_path)
    if layer_data.foreground_path is not None:
        if not os.path.exists(layer_data.foreground_path):
            raise FileNotFoundError(layer_data.foreground_path)
    if layer_data.blur_strength is not None:
        if not isinstance(layer_data.blur_strength, int):
            raise TypeError(type(layer_data.blur_strength))
    if layer_data.brightness is not None:
        if not isinstance(layer_data.brightness, float) and not isinstance(layer_data.brightness, int):
            raise TypeError(type(layer_data.brightness))

def _validate_subtitle_profile(subtitle_profile:SubtitleProfile) -> None:
    if subtitle_profile.font_data is None:
        raise AttributeError
    else:
        _validate_font_data(subtitle_profile.font_data)

    if subtitle_profile.outline_data_1 is None:
        pass
    else:
        _validate_outline_data(subtitle_profile.outline_data_1)
    if subtitle_profile.outline_data_2 is None:
        pass
    else:
        _validate_outline_data(subtitle_profile.outline_data_2)
    if subtitle_profile.textbox_data is None:
        raise NotImplementedError("Subtitle profile has no textbox data.")
    else:
        _validate_textbox_data(subtitle_profile.textbox_data)
    if subtitle_profile.layer_data is None:
        pass
    else:
        _validate_layer_data(subtitle_profile.layer_data)
    pass

def _validate_subtitle_list(subtitle_list:List[Subtitle]) -> None:
    for subtitle in subtitle_list:
        if subtitle.subtitle_profile is not None:
            _validate_subtitle_profile(subtitle.subtitle_profile)
    pass

def validate_subtitle_group(subtitle_group:SubtitleGroup, image_id_set:Optional[set]=None) -> None:
    if image_id_set is not None:
        if subtitle_group.image_id not in image_id_set:
            logger.warning(f"Invalid image ID {subtitle_group.image_id}: this subtitle group will have no effect.")
    # check the data does not have issues.

    if subtitle_group.subtitle_list is not None:
        _validate_subtitle_list(subtitle_group.subtitle_list)

    pass