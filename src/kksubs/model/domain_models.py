import os
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Union, List

from PIL import ImageColor

def to_integer(value) -> Optional[int]:
    if value is None or isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise TypeError(type(value))

def to_float(value) -> Optional[float]:
    if value is None or isinstance(value, (float, int)):
        return value
    if isinstance(value, str):
        return float(value)
    raise TypeError(type(value))
    
def to_rgb_color(color):
    if color is None or isinstance(color, tuple):
        return color
    if (color[0]=="(" and color[-1]==")") or (color[0]=="[" and color[-1]=="]"):
        str_data = color[1:-1]
        return tuple(map(int, str_data.split(",")))
    if isinstance(color, list):
        return (color[0], color[1], color[2])
    else:
        return ImageColor.getrgb(color)
    
def to_str_coords(value) -> Optional[tuple]:
    return tuple(map(str, value[1:-1].split(",")))

def to_xy_coords(value) -> Optional[tuple]:
    if value is None or isinstance(value, tuple):
        return value
    if isinstance(value, tuple):
        pass
    if isinstance(value, str):
        return tuple(map(int, value[1:-1].split(",")))
    if isinstance(value, list):
        return (int(value[0]), int(value[1]))
    raise TypeError(f"Coords has invalid type: {value} is of type {type(value)}.")

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
    CENTER = "center"

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
        self.color = to_rgb_color(self.color)
        self.stroke_color = to_rgb_color(self.stroke_color)
        self.size = to_integer(self.size)
        self.stroke_size = to_integer(self.stroke_size)

    @classmethod
    def get_default(cls):
        return FontData(
            style=get_default_font_style(),
            color=(255, 255, 255),
            size=50,
            stroke_color=(0, 0, 0),
            stroke_size=5
        )

    def add_default(self, profile_font_data:"FontData"=None):
        if profile_font_data is None:
            profile_font_data = FontData()

        self.style = coalesce(self.style, profile_font_data.style)
        self.color = coalesce(self.color, profile_font_data.color)
        self.size = coalesce(self.size, profile_font_data.size)
        self.stroke_color = coalesce(self.stroke_color, profile_font_data.stroke_color)
        self.stroke_size = coalesce(self.stroke_size, profile_font_data.stroke_size)
        pass

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
        self.color = to_rgb_color(self.color)
        self.radius = to_integer(self.radius)
        self.blur_strength = to_integer(self.blur_strength)
        pass

    @classmethod
    def get_default(cls):
        return OutlineData(
            color=(0, 0, 0),
            radius=5,
            blur_strength=0
        )

    def add_default(self, profile_outline_data:"OutlineData"=None):
        if profile_outline_data is None:
            profile_outline_data = OutlineData()

        self.color = coalesce(self.color, profile_outline_data.color)
        self.radius = coalesce(self.radius, profile_outline_data.radius)
        self.blur_strength = coalesce(self.blur_strength, profile_outline_data.blur_strength)
        self.correct_values()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    pass


class TextboxData(BaseData):
    def __init__(
            self, 
            alignment:str=None, anchor_point=None, grid4=None, box_width:Optional[int]=None, push:Optional[str]=None, 
            rotate=None, dynamic_rotate=None
    ):
        """
        :param alignment: left, right or center.
        :param anchor_point: [x, y] values of the anchor point. x value is left/right border of textbox if textbox is
        left/right aligned, else center line of textbox.
        """

        self.alignment = alignment
        self.anchor_point = anchor_point
        self.box_width = box_width
        self.push = push # direction from the first line of text.
        self.grid4 = grid4 # a coordinate point representing a point on a 4ths grid.
        self.rotate = rotate
        self.dynamic_rotate = dynamic_rotate # rotate the text depending on where the text is on the image (quadrant-dependent)
        self.correct_values()
        super().__init__()

    def correct_values(self):
        self.grid4 = to_xy_coords(self.grid4)
        self.anchor_point = to_xy_coords(self.anchor_point)
        self.box_width = to_integer(self.box_width)
        self.rotate = to_integer(self.rotate)
        self.dynamic_rotate = to_integer(self.dynamic_rotate)

    @classmethod
    def get_default(cls):
        return TextboxData(
            alignment="center",
            anchor_point=(0, 0),
            box_width=100,
            push="down",
        )

    def add_default(self, profile_textbox_data:"TextboxData"=None):
        if profile_textbox_data is None:
            profile_textbox_data = TextboxData()

        self.alignment = coalesce(self.alignment, profile_textbox_data.alignment)
        self.anchor_point = coalesce(self.anchor_point, profile_textbox_data.anchor_point)
        self.box_width = coalesce(self.box_width, profile_textbox_data.box_width)
        self.push = coalesce(self.push, profile_textbox_data.push)
        self.grid4 = coalesce(self.grid4, profile_textbox_data.grid4)
        self.rotate = coalesce(self.rotate, profile_textbox_data.rotate)
        self.dynamic_rotate = coalesce(self.dynamic_rotate, profile_textbox_data.dynamic_rotate)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

class LayerData(BaseData):
    def __init__(
            self, 
            brightness=None,
            gaussian_blur=None, 
            motion_blur=None, motion_rotate=None, 
            radial_blur=None, radial_coords=None,
            angular_blur=None, # no implementation.
            f_coords=None, f_radius=None, f_blur=None,
    ):
        self.brightness = brightness

        self.gaussian_blur = gaussian_blur

        self.motion_blur = motion_blur
        self.motion_rotate = motion_rotate

        self.radial_blur = radial_blur
        self.radial_coords = radial_coords

        self.f_coords = f_coords
        self.f_radius = f_radius
        self.f_blur = f_blur
        super().__init__()

    def correct_values(self):
        is_gaussian_blur = self.gaussian_blur is not None
        is_motion_blur = self.motion_blur is not None or self.motion_rotate is not None
        if is_gaussian_blur and is_motion_blur:
            raise ValueError("Cannot implement both gaussian and motion blur in one profile.")
        self.brightness = to_float(self.brightness)

        self.gaussian_blur = to_integer(self.gaussian_blur)

        self.motion_blur = to_integer(self.motion_blur)
        self.motion_rotate = to_integer(self.motion_rotate)

        self.radial_blur = to_integer(self.radial_blur)
        self.radial_coords = to_xy_coords(self.radial_coords)

        self.f_coords = to_xy_coords(self.f_coords)
        self.f_radius = to_integer(self.f_radius)
        self.f_blur = to_integer(self.f_blur)

    @classmethod
    def get_default(cls):
        return LayerData(
            f_coords=(0, 0),
            f_radius=100,
            f_blur=100
        )
    
    def add_default(self, profile_focus_data: "LayerData" = None):
        if profile_focus_data is None:
            profile_focus_data = LayerData()

        self.brightness = coalesce(self.brightness, profile_focus_data.brightness)

        self.gaussian_blur = coalesce(self.gaussian_blur, profile_focus_data.gaussian_blur)
        self.motion_blur = coalesce(self.motion_blur, profile_focus_data.motion_blur)
        self.motion_rotate = coalesce(self.motion_rotate, profile_focus_data.motion_rotate)

        self.radial_blur = coalesce(self.radial_blur, profile_focus_data.radial_blur)
        self.radial_coords = coalesce(self.radial_coords, profile_focus_data.radial_coords)

        self.f_coords = coalesce(self.f_coords, profile_focus_data.f_coords)
        self.f_radius = coalesce(self.f_radius, profile_focus_data.f_radius)
        self.f_blur = coalesce(self.f_blur, profile_focus_data.f_blur)

class AssetData(BaseData):
    # applies an asset (image) to the image. Example: focal lines, 
    def __init__(self, path:str=None, coords=None, scale=None, rotate=None):
        self.path = path # a valid path to an image.
        self.coords = coords # a set of coordinates (default (0, 0) center of image)
        self.scale = scale # a scale (0 - infinity)
        self.rotate = rotate # 0 - 360
        super().__init__()

    def correct_values(self):
        self.coords = to_xy_coords(self.coords)
        self.scale = to_float(self.scale)
        self.rotate = to_integer(self.rotate)

    def add_default(self, profile_data: "AssetData" = None):
        if profile_data is None:
            return
        self.path = coalesce(self.path, profile_data.path)
        self.coords = coalesce(self.coords, profile_data.coords)
        self.scale = coalesce(self.scale, profile_data.scale)
        self.rotate = coalesce(self.rotate, profile_data.rotate)

    @classmethod
    def get_default(cls):
        return AssetData()

class SubtitleProfile(BaseData):

    def __init__(
            self, font_data:Optional[FontData]=None, outline_data_1:Optional[OutlineData]=None, outline_data_2:Optional[OutlineData]=None,
            textbox_data:Optional[TextboxData]=None, layer_data:Optional[LayerData]=None, asset_data:Optional[AssetData]=None,
            default_text:Optional[str]=None,

            # if a subtitle profile contains an orbit.
            orbits:Optional[List["SubtitleProfile"]]=None,
            # orbiting data (orbit)
            centrix:Optional[str]=None, # coordinates. only for subtitles that orbit other subtitles.

            subtitle_profile_id:Optional[str]=None):
        
        self.font_data = font_data
        self.outline_data_1 = outline_data_1
        self.outline_data_2 = outline_data_2
        self.textbox_data = textbox_data
        self.subtitle_profile_id = subtitle_profile_id
        self.layer_data = layer_data
        self.asset_data = asset_data
        self.default_text = default_text # text prepended to the first line of a subtitle during text application.
        
        self.orbits = orbits

        self.centrix = centrix # orbit coordinates of the form UDLRC (up down left right center), reserved for orbits.
        super().__init__()

    def correct_values(self):
        if self.font_data is not None:
            self.font_data.correct_values()
        if self.outline_data_1 is not None:
            self.outline_data_1.correct_values()
        if self.outline_data_2 is not None:
            self.outline_data_2.correct_values()
        if self.textbox_data is not None:
            self.textbox_data.correct_values()
        if self.layer_data is not None:
            self.layer_data.correct_values()
        if self.asset_data is not None:
            self.asset_data.correct_values()
        if self.centrix is not None:
            self.centrix = to_str_coords(self.centrix)
        pass

    @classmethod
    def get_default(cls):
        subtitle_profile = SubtitleProfile(
            font_data=FontData.get_default(),
            textbox_data=TextboxData.get_default()
        )
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
        if self.asset_data is None:
            self.asset_data = AssetData()
        self.asset_data.add_default(profile.asset_data)

        self.default_text = coalesce(self.default_text, profile.default_text)
        self.orbits = coalesce(self.orbits, profile.orbits)
        self.centrix = coalesce(self.centrix, profile.centrix)

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
