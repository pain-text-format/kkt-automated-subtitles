

import os
from typing import Dict, List
from kksubs.model.domain_models import FontData, Subtitle, SubtitleGroup, SubtitleProfile

def _validate_font_data(font_data:FontData):
    if font_data is None:
        raise KeyError
    if font_data.style is None:
        raise KeyError
    if not os.path.exists(font_data.style):
        raise FileExistsError

def _validate_subtitle_profile(subtitle_profile:SubtitleProfile) -> None:
    if subtitle_profile.font_data is None:
        raise AttributeError
    else:
        _validate_font_data(subtitle_profile.font_data)
    pass

def _validate_subtitle_list(subtitle_list:List[Subtitle]) -> None:
    for subtitle in subtitle_list:
        if subtitle.subtitle_profile is not None:
            _validate_subtitle_profile(subtitle.subtitle_profile)
    pass

def validate_subtitle_groups(subtitle_groups_by_textpath:Dict[str, SubtitleGroup]) -> None:
    # check the data does not have issues.

    for image_id in subtitle_groups_by_textpath.keys():
        subtitle_group = subtitle_groups_by_textpath.get(image_id)
        subtitle_list = subtitle_group.subtitle_list
        _validate_subtitle_list(subtitle_list)

    pass