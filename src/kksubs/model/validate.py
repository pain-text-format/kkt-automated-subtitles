import logging

import os
from typing import List, Optional
from kksubs.model.domain_models import AssetData, LayerData, FontData, OutlineData, Subtitle, SubtitleGroup, SubtitleProfile, TextboxData

logger = logging.getLogger(__name__)

def _validate_coordinates(coords):
    # check if coords is a pair of ints.
    if not isinstance(coords, tuple):
        raise TypeError(type(coords))
    if not (isinstance(coords[0], int) and isinstance(coords[1], int)):
        raise TypeError(f"Coords are not pair of ints: {(coords[0], type(coords[0]))}, {(coords[1], type(coords[1]))}")


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
    if textbox_data.grid4 is not None:
        if not isinstance(textbox_data.grid4, tuple):
            raise TypeError(type(textbox_data.grid4))
        if not (isinstance(textbox_data.grid4[0], int) and isinstance(textbox_data.grid4[1], int)):
            raise TypeError(f"Textbox data does not contain ints: {(textbox_data.grid4[0], type(textbox_data.grid4[0]))}, {(textbox_data.grid4[1], type(textbox_data.grid4[1]))}")
        if not ((0 <= textbox_data.grid4[0] <= 4) and (0 <= textbox_data.grid4[0] <= 4)):
            raise ValueError(f"Values not between 0 and 4: {textbox_data.grid4}")
    if textbox_data.rotate is not None:
        if not isinstance(textbox_data.rotate, int):
            raise TypeError(type(textbox_data.rotate))
    if textbox_data.dynamic_rotate is not None:
        logger.warning("Dynamic rotation feature is not stable, use with caution.")
        if not isinstance(textbox_data.dynamic_rotate, int):
            raise TypeError(type(textbox_data.dynamic_rotate))

def _validate_layer_data(layer_data:LayerData):
    if layer_data.gaussian_blur is not None:
        if not isinstance(layer_data.gaussian_blur, int):
            raise TypeError(layer_data.gaussian_blur, type(layer_data.gaussian_blur))
    pass

def _validate_asset_data(asset_data:AssetData):
    if asset_data.path is not None:
        if not os.path.exists(asset_data.path):
            raise FileNotFoundError(asset_data.path)
    if asset_data.coords is not None:
        _validate_coordinates(asset_data.coords)
    if asset_data.scale is not None:
        if not isinstance(asset_data.scale, (float, int)):
            raise TypeError(type(asset_data.scale))
    if asset_data.rotate is not None:
        if not isinstance(asset_data.rotate, int):
            raise TypeError(type(asset_data.rotate))

def _validate_subtitle_profile(subtitle_profile:SubtitleProfile) -> None:
    if subtitle_profile.font_data is None:
        raise AttributeError
    else:
        subtitle_profile.font_data.add_default(FontData.get_default())
        _validate_font_data(subtitle_profile.font_data)
        
    if subtitle_profile.default_text is not None:
        if not isinstance(subtitle_profile.default_text, str):
            raise TypeError(type(subtitle_profile.default_text))

    if subtitle_profile.outline_data_1 is not None:
        subtitle_profile.outline_data_1.add_default(OutlineData.get_default())
        _validate_outline_data(subtitle_profile.outline_data_1)

    if subtitle_profile.outline_data_2 is not None:
        subtitle_profile.outline_data_2.add_default(OutlineData.get_default())
        _validate_outline_data(subtitle_profile.outline_data_2)

    if subtitle_profile.textbox_data is None:
        raise NotImplementedError("Subtitle profile has no textbox data.")
    else:
        subtitle_profile.textbox_data.add_default(TextboxData.get_default())
        _validate_textbox_data(subtitle_profile.textbox_data)

    if subtitle_profile.layer_data is not None:
        _validate_layer_data(subtitle_profile.layer_data)

    if subtitle_profile.asset_data is not None:
        _validate_asset_data(subtitle_profile.asset_data)
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