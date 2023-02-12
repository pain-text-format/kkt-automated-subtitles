

import os
from typing import List
from .domain_models import FontData, OutlineData, Subtitle, SubtitleGroup, SubtitleProfile

def _validate_font_data(font_data:FontData):
    if font_data is None:
        raise KeyError
    if font_data.style is None:
        raise KeyError
    if not os.path.exists(font_data.style):
        raise FileExistsError(f"Style {font_data.style} does not exist.")
    
def _validate_outline_data(outline_data:OutlineData):
    if not isinstance(outline_data.radius, int):
        raise TypeError(f"{outline_data.radius} is a {type(outline_data.radius)}")

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
    pass

def _validate_subtitle_list(subtitle_list:List[Subtitle]) -> None:
    for subtitle in subtitle_list:
        if subtitle.subtitle_profile is not None:
            _validate_subtitle_profile(subtitle.subtitle_profile)
    pass

def validate_subtitle_group(subtitle_group:SubtitleGroup) -> None:
    # check the data does not have issues.

    if subtitle_group.subtitle_list is not None:
        _validate_subtitle_list(subtitle_group.subtitle_list)

    pass