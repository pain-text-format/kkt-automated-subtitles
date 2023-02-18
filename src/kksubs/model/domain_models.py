import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union, List

from PIL import ImageColor

def get_default_font_style():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../resource/font/Roboto/Roboto-Regular.ttf")

def coalesce(*args):
    for arg in args:
        if arg is not None:
            return arg
    return None

class SupportedExtensions(Enum):
    @classmethod
    def get_is_supported(cls, filepath, boolean=True):
        for format_class in cls:
            if os.path.splitext(filepath)[1].lower() in format_class.value:
                return format_class if not boolean else True
        return None if not boolean else False


class SupportedValues(Enum):
    @classmethod
    def get_is_supported(cls, value):
        if not isinstance(value, str):
            return False
        for value_class in cls:
            if value_class.value == value.lower():
                return True
        return False


class SupportedImageExtensions(SupportedExtensions):
    PNG = {".png"}
    JPG = {".jpg", ".jpeg"}


class SupportedInputTextExtensions(SupportedExtensions):
    YAML = {".yaml", ".yml"}
    TEXT = {".txt"}
    JSON = {".json"}


class SupportedAlignments(SupportedValues):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class SupportedPushValues(SupportedValues):
    UP = "up"
    DOWN = "down"

class BaseData(ABC):

    def __init__(self):
        self.correct_values()

    @abstractmethod
    def correct_values(self):
        ...

    @abstractmethod
    def add_default(self, profile_data:"BaseData"=None):
        ...

    @classmethod
    @abstractmethod
    def get_default(cls):
        ...

def convert_color_str_to_tuple(color):
    if (color[0]=="(" and color[-1]==")") or (color[0]=="[" and color[-1]=="]"):
        str_data = color[1:-1]
        return tuple(map(int, str_data.split(",")))
    else:
        return ImageColor.getrgb(color)

class FontData(BaseData):
    def __init__(
            self, style: Optional[str] = None, color: Optional[Union[List, str]] = None, size: Optional[int] = None,
            stroke_color = None, stroke_size:Optional[int] = None,
    ):
        self.style = style
        self.color = color
        self.size = size
        self.stroke_color = stroke_color
        self.stroke_size = stroke_size
        super().__init__()

    def correct_values(self):
        if isinstance(self.color, list):
            self.color = (self.color[0], self.color[1], self.color[2])
        elif isinstance(self.color, str):
            # use regex to check for the following formats: (a, b, c) or [a, b, c].
            self.color = convert_color_str_to_tuple(self.color)

        if isinstance(self.stroke_color, list):
            self.stroke_color = (
                self.stroke_color[0],
                self.stroke_color[1],
                self.stroke_color[2]
            )
        elif isinstance(self.stroke_color, str):
            self.stroke_color = convert_color_str_to_tuple(self.stroke_color)

        if self.size is not None:
            if not isinstance(self.size, int):
                if isinstance(self.size, str):
                    self.size = int(self.size)
                else:
                    raise TypeError(f"Font size {self.size} is type {type(self.size)}.")
        if self.stroke_size is not None:
            if not isinstance(self.stroke_size, int):
                if isinstance(self.stroke_size, str):
                    self.stroke_size = int(self.stroke_size)
                else:
                    raise TypeError(f"Font size {self.stroke_size} is type {type(self.stroke_size)}.")

    @classmethod
    def get_default(cls):
        font_data = FontData()
        font_data.add_default()
        return font_data

    def add_default(self, profile_font_data:"FontData"=None):
        if profile_font_data is None:
            profile_font_data = FontData()

        self.style = coalesce(self.style, profile_font_data.style, get_default_font_style())
        self.color = coalesce(self.color, profile_font_data.color, (255, 255, 255))
        self.size = coalesce(self.size, profile_font_data.size, 50)

        default_global_stroke_color = (0, 0, 0)
        default_global_stroke_size = 5

        self.stroke_color = coalesce(self.stroke_color, profile_font_data.stroke_color, default_global_stroke_color)
        self.stroke_size = coalesce(self.stroke_size, profile_font_data.stroke_size, default_global_stroke_size)

        # # If stroke color and stroke size is none, assume that user does not want outline. (not used.)
        # if self.stroke_color is None and self.stroke_size is None:
        #     if profile_font_data.stroke_color is None and profile_font_data.stroke_size is None:
        #         pass
        #     else:
        #         self.stroke_color = asc_override(None, profile_font_data.stroke_color, default_global_stroke_color)
        #         self.stroke_size = asc_override(None, profile_font_data.stroke_size, default_global_stroke_size)
        # elif self.stroke_color is None:
        #     self.stroke_color = asc_override(None, profile_font_data.stroke_color, default_global_stroke_color)
        # elif self.stroke_size is None:
        #     self.stroke_size = asc_override(None, profile_font_data.stroke_size, default_global_stroke_size)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    pass


class OutlineData(BaseData):
    def __init__(self, color:Union[List, str]=None, radius:int=None, blur_strength:int=None):
        self.color = color
        self.radius = radius
        self.blur_strength = blur_strength
        super().__init__()

    def correct_values(self):
        if isinstance(self.color, list):
            self.color = (self.color[0], self.color[1], self.color[2])
        elif isinstance(self.color, str):
            self.color = convert_color_str_to_tuple(self.color)
        if isinstance(self.radius, str):
            self.radius = int(self.radius)
        if isinstance(self.blur_strength, str):
            self.blur_strength = int(self.blur_strength)
        pass

    @classmethod
    def get_default(cls):
        outline_data = OutlineData()
        outline_data.add_default()
        return outline_data

    def add_default(self, profile_outline_data:"OutlineData"=None):
        if profile_outline_data is None:
            profile_outline_data = OutlineData()

        self.color = coalesce(self.color, profile_outline_data.color, (0, 0, 0))
        self.radius = coalesce(self.radius, profile_outline_data.radius, 5)
        self.blur_strength = coalesce(self.blur_strength, profile_outline_data.blur_strength, 0)
        self.correct_values()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    pass


class TextboxData(BaseData):
    def __init__(self, alignment:str=None, anchor_point=None, box_width:Optional[int]=None, push:Optional[str]=None):
        """
        :param alignment: left, right or center.
        :param anchor_point: [x, y] values of the anchor point. x value is left/right border of textbox if textbox is
        left/right aligned, else center line of textbox.
        """

        self.alignment = alignment
        self.anchor_point = anchor_point
        self.box_width = box_width
        self.push = push # direction from the first line of text.
        self.correct_values()
        super().__init__()

    def correct_values(self):
        if self.anchor_point is not None:
            if isinstance(self.anchor_point, tuple):
                pass
            elif isinstance(self.anchor_point, str):
                self.anchor_point = tuple(map(int, self.anchor_point[1:-1].split(",")))
            elif isinstance(self.anchor_point, list):
                self.anchor_point = (int(self.anchor_point[0]), int(self.anchor_point[1]))
            else:
                raise TypeError(f"Anchor point has invalid type: {self.anchor_point} is of type {type(self.anchor_point)}.")
        if self.box_width is not None:
            if isinstance(self.box_width, int):
                pass
            elif isinstance(self.box_width, str):
                self.box_width = int(self.box_width)
            else:
                raise TypeError(f"Box width has invalid type: {self.box_width} is of type {type(self.box_width)}")


    @classmethod
    def get_default(cls):
        text_box_data = TextboxData()
        text_box_data.add_default()
        return text_box_data

    def add_default(self, profile_textbox_data:"TextboxData"=None):
        if profile_textbox_data is None:
            profile_textbox_data = TextboxData()

        self.alignment = coalesce(self.alignment, profile_textbox_data.alignment, "center")
        self.anchor_point = coalesce(self.anchor_point, profile_textbox_data.anchor_point, (0, 0))
        self.box_width = coalesce(self.box_width, profile_textbox_data.box_width, 100)
        self.push = coalesce(self.push, profile_textbox_data.push, "down")

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class LayerData(BaseData):
    # data concerning the image layer, rather than the subtitle.
    # examples:
    # text background, text foreground,
    # image effects like image gaussian blur, image brightness.
    def __init__(
            self, 
            background_path:Optional[str]=None, foreground_path:Optional[str]=None,
            blur_strength:Optional[int]=None, brightness=None,
    ):
        self.background_path = background_path
        self.foreground_path = foreground_path
        self.blur_strength = blur_strength
        self.brightness = brightness
        super().__init__()

    def correct_values(self):
        if self.blur_strength is not None:
            if isinstance(self.blur_strength, int):
                pass
            elif isinstance(self.blur_strength, str):
                self.blur_strength = int(self.blur_strength)
            else:
                raise TypeError(f"Blur strength {self.blur_strength} is of type {type(self.blur_strength)}, not int.")
            
        if self.brightness is not None:
            if isinstance(self.brightness, int):
                pass
            elif isinstance(self.brightness, str):
                self.brightness = int(self.brightness)
            else:
                raise TypeError(f"Brightness {self.brightness} is of type {type(self.brightness)}, not int")
            
    def add_default(self, profile_data: "LayerData" = None):
        if profile_data is None:
            return
        self.background_path = coalesce(self.background_path, profile_data.background_path)
        self.foreground_path = coalesce(self.foreground_path, profile_data.foreground_path)
        self.blur_strength = coalesce(self.blur_strength, profile_data.blur_strength)
        self.brightness = coalesce(self.brightness, profile_data.brightness)

    @classmethod
    def get_default(cls):
        return LayerData()


class SubtitleProfile(BaseData):

    def __init__(self, font_data:Optional[FontData]=None, outline_data_1:Optional[OutlineData]=None, outline_data_2:OutlineData=None,
                 textbox_data:Optional[TextboxData]=None, layer_data:Optional[LayerData]=None, default_text:Optional[str]=None,
                 subtitle_profile_id:Optional[str]=None):
        self.font_data = font_data
        self.outline_data_1 = outline_data_1
        self.outline_data_2 = outline_data_2
        self.textbox_data = textbox_data
        self.subtitle_profile_id = subtitle_profile_id
        self.layer_data = layer_data
        self.default_text = default_text # text prepended to the first line of a subtitle during text application.
        super().__init__()

    def correct_values(self):
        pass

    @classmethod
    def get_default(cls):
        subtitle_profile = SubtitleProfile()
        subtitle_profile.add_default()
        return subtitle_profile

    def add_default(self, profile:"SubtitleProfile"=None):

        # pass global data to profile data.
        if profile is None:
            profile = SubtitleProfile()

        if profile.font_data is None:
            profile.font_data = FontData()
        profile.font_data.add_default()

        if self.font_data is None:
            self.font_data = coalesce(self.font_data, profile.font_data, FontData.get_default())
        self.font_data.add_default(profile.font_data)

        # if no local outline data and no profile outline data, do not fill with global data.
        # if profile data, no local, create local, fill profile with global data, then local with profile.
        # if local data, no profile, fill local with global.
        # if local and profile, fill profile with global, then fill local with profile.
        # TODO: simplify this code.
        if self.outline_data_1 is None and profile.outline_data_1 is None:
            pass
        elif self.outline_data_1 is None:
            self.outline_data_1 = OutlineData()
            profile.outline_data_1.add_default(OutlineData.get_default())
            self.outline_data_1.add_default(profile.outline_data_1)
        elif profile.outline_data_1 is None:
            assert self.outline_data_1 is not None
            self.outline_data_1.add_default(OutlineData.get_default())
        if self.outline_data_1 is not None:
            if profile.outline_data_1 is None:
                profile.outline_data_1 = OutlineData()
            profile.outline_data_1.add_default(OutlineData.get_default())
            self.outline_data_1.add_default(profile.outline_data_1)
        if self.outline_data_2 is None and profile.outline_data_2 is None:
            pass
        elif self.outline_data_2 is None:
            self.outline_data_2 = OutlineData()
            profile.outline_data_2.add_default(OutlineData.get_default())
            self.outline_data_2.add_default(profile.outline_data_2)
        elif profile.outline_data_2 is None:
            self.outline_data_2.add_default(OutlineData.get_default())
        if self.outline_data_2 is not None:
            if profile.outline_data_2 is None:
                profile.outline_data_2 = OutlineData()
            profile.outline_data_2.add_default(OutlineData.get_default())
            self.outline_data_2.add_default(profile.outline_data_2)

        if self.textbox_data is None:
            self.textbox_data = TextboxData()
        self.textbox_data.add_default(profile.textbox_data)

        if self.layer_data is None:
            self.layer_data = LayerData()
        self.layer_data.add_default(profile.layer_data)

        self.default_text = coalesce(self.default_text, profile.default_text)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    pass


class Subtitle:

    def __init__(
            self, subtitle_profile_id: Optional[str] = None, subtitle_profile: Optional[SubtitleProfile] = None,
            content: List[str] = None
    ):
        """
        Encapsulates a single subtitle.
        :param subtitle_profile_id: if None, applies default subtitle profile.
        :param content: content to be displayed on image.
        """

        self.subtitle_profile_id = subtitle_profile_id
        self.subtitle_profile = subtitle_profile
        self.content = content

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    pass


class SubtitleGroup:

    def __init__(self, image_id:str=None, subtitle_list:List[Subtitle]=None):
        """
        Encapsulates a list of subtitles that are added to an image, uniquely identified by the image ID.
        :param image_id:
        :param subtitle_list:
        """
        self.image_id = image_id
        self.subtitle_list = subtitle_list

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
