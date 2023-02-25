import logging
import os.path
import textwrap
from typing import Dict, List, Union

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from kksubs.image.gaussian_blur import apply_gaussian_blur, cfr_apply_gaussian_blur
from kksubs.image.motion_blur import apply_motion_blur, cfr_apply_motion_blur
from kksubs.image.radial_blur import apply_radial_blur
from kksubs.image.brightness import adjust_brightness, cfr_adjust_brightness
from kksubs.image.utils import apply_image

from kksubs.model.data_access_services import SubtitleDataAccessService
from kksubs.model.domain_models import LayerData, Subtitle, SubtitleGroup
from kksubs.model.validate import validate_subtitle_group

logger = logging.getLogger(__name__)

def _get_text_dimensions(text_string, font, default_text_width=None, default_text_height=None):
    if text_string == "":
        return default_text_width, default_text_height
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return text_width, text_height

def apply_text_to_image(image:Image.Image, subtitle:Subtitle) -> Image.Image:
    # expand subtitle.
    subtitle_profile = subtitle.subtitle_profile
    content = subtitle.content
    # expand details of subtitle profile.
    font_data = subtitle_profile.font_data
    outline_data_1 = subtitle_profile.outline_data_1
    outline_data_2 = subtitle_profile.outline_data_2
    textbox_data = subtitle_profile.textbox_data

    # default text application.
    default_text = subtitle_profile.default_text
    if default_text is not None:
        if content is None or len(content) == 0:
            content = [default_text]
        else:
            content[0] = default_text + content[0]

    # extract image data
    image_width, image_height = image.size
    text_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)
    outline_1_layer = Image.new("RGBa", image.size, (0, 0, 0, 0))
    outline_1_draw = ImageDraw.Draw(outline_1_layer)
    outline_2_layer = Image.new("RGBa", image.size, (0, 0, 0, 0))
    outline_2_draw = ImageDraw.Draw(outline_2_layer)

    # extract text data
    font_style = font_data.style
    font_color = font_data.color
    font_size = font_data.size
    font_stroke_size = font_data.stroke_size
    font_stroke_color = font_data.stroke_color
    alignment = textbox_data.alignment
    box_width = textbox_data.box_width
    push = textbox_data.push
    rotate = textbox_data.rotate
    dynamic_rotate = textbox_data.dynamic_rotate

    if textbox_data.grid4 is not None:
        grid4_x, grid4_y = textbox_data.grid4
        tb_anchor_x = int(image_width//4*grid4_x)
        tb_anchor_y = int(image_height//4*grid4_y)
        
        if textbox_data.anchor_point is not None: # if there is anchor point data, use it to fine-tune.
            x_adjust, y_adjust = textbox_data.anchor_point
            tb_anchor_x = tb_anchor_x + x_adjust
            tb_anchor_y = tb_anchor_y - y_adjust

    else:
        tb_anchor_x, tb_anchor_y = textbox_data.anchor_point
        tb_anchor_x = image_width/2 + tb_anchor_x
        tb_anchor_y = image_height/2 - tb_anchor_y

    font = ImageFont.truetype(font_style, font_size)
    # this is used to standardize the heights of each horizontal text line, but might be a bad idea for different languages.
    # maybe use vertical spacing in the future to avoid font-dependent height definition...
    default_text_width, default_text_height = _get_text_dimensions("l", font)

    # analyze text
    wrapped_text = []
    for line in content:
        if line != "":
            wrapped_text.extend(textwrap.wrap(line, width=box_width))
        else:
            wrapped_text.append("")
    if not wrapped_text:
        return image

    text_dimensions = [_get_text_dimensions(line, font, default_text_width=default_text_width, default_text_height=default_text_height) for line in wrapped_text]
    text_widths = list(map(lambda dim:dim[0], text_dimensions))
    max_text_width = max(text_widths)
    num_lines = len(wrapped_text)
    sum_text_height = num_lines * default_text_height

    # gather rotation arguments. (for future advanced rotation)
    left = image_width
    right = 0
    up = image_height
    down = 0
    for line in wrapped_text:
        text_width = font.getlength(line)
        if alignment == "left":
            left = min(left, tb_anchor_x)
            right = max(right, tb_anchor_x + text_width)
        elif alignment == "center":
            left = min(left, tb_anchor_x - text_width/2)
            right = max(right, tb_anchor_x + text_width/2)
        elif alignment == "right":
            left = min(left, tb_anchor_x - text_width)
            right = max(right, tb_anchor_x)
    if push == "up":
        up = min(up, tb_anchor_y)
        down = max(down, tb_anchor_y + sum_text_height)
    elif push == "down":
        up = min(up, tb_anchor_y + sum_text_height)
        down = max(down, tb_anchor_y)
    elif push == "center":
        up = tb_anchor_y
        down = tb_anchor_y
        pass

    # add text stage
    for i, line in enumerate(wrapped_text):
        text_width = font.getlength(line)

        if alignment == "left":
            x = tb_anchor_x + text_width/2 - text_width/2
        elif alignment == "center":
            x = tb_anchor_x - text_width/2
        elif alignment == "right":
            x = tb_anchor_x - text_width/2 - text_width/2
        else:
            raise ValueError(f"Invalid alignment value {alignment}.")
        if push == "up":
            y = tb_anchor_y - default_text_height*(num_lines-i)
        elif push == "down":
            y = tb_anchor_y - default_text_height*(num_lines-i) + sum_text_height
        elif push == "center":
            y = tb_anchor_y - default_text_height*(num_lines-i) + sum_text_height//2
        else:
            raise ValueError(f"Invalid push value {push}.")
        line_pos = (x, y)

        if outline_data_2 is not None:
            outline_2_draw.text(
                line_pos, line, font=font, fill=outline_data_2.color, stroke_width=outline_data_2.radius,
                stroke_fill=outline_data_2.color
            )

        if outline_data_1 is not None:
            outline_1_draw.text(
                line_pos, line, font=font, fill=outline_data_1.color, stroke_width=outline_data_1.radius,
                stroke_fill=outline_data_1.color
            )

        # add text layer
        if font_data.stroke_size is not None:
            text_draw.text(line_pos, line, font=font, fill=font_color, stroke_width=font_stroke_size, stroke_fill=font_stroke_color)
            pass
        else:
            text_draw.text(line_pos, line, font=font, fill=font_color)
        # image.paste(text_layer, (0, 0), text_layer)

    # layer rotation stage
    if rotate is not None or dynamic_rotate is not None:
        rotate_x = (right + left)/2
        rotate_y = (up + down)/2

        # check if
        if rotate is None:
            first_or_fourth_quadrant = rotate_x > image_width//2
            first_or_second_quadrant = rotate_y < image_height*2//3
            if (first_or_fourth_quadrant and first_or_second_quadrant):
                rotate = -dynamic_rotate
            elif (not first_or_fourth_quadrant and first_or_second_quadrant):
                rotate = dynamic_rotate
            if image_width*2//5 < rotate_x < image_width*3//5:
                rotate = 0

        if rotate:
            text_layer = text_layer.rotate(rotate, center=(rotate_x, rotate_y))
            if outline_1_layer is not None:
                outline_1_layer = outline_1_layer.rotate(rotate, center=(rotate_x, rotate_y))
            if outline_2_layer is not None:
                outline_2_layer = outline_2_layer.rotate(rotate, center=(rotate_x, rotate_y))

    # paste stage
    if outline_data_2 is not None:
        if outline_data_2.blur_strength is not None and outline_data_2.blur_strength:
            outline_2_over_base = image.copy()
            outline_2_over_base.paste(outline_2_layer, (0, 0), outline_2_layer)
            outline_2_over_base = outline_2_over_base.filter(ImageFilter.GaussianBlur(radius=outline_data_2.blur_strength))
            outline_2_layer = outline_2_layer.filter(ImageFilter.GaussianBlur(radius=outline_data_2.blur_strength))
            outline_2_layer = outline_2_layer.convert("RGBA")
            image.paste(outline_2_over_base, (0, 0), outline_2_layer)
        else:
            image.paste(outline_2_layer, (0, 0), outline_2_layer)
    if outline_data_1 is not None:
        if outline_data_1.blur_strength is not None and outline_data_1.blur_strength:
            outline_1_over_base = image.copy()
            outline_1_over_base.paste(outline_1_layer, (0, 0), outline_1_layer)
            outline_1_over_base = outline_1_over_base.filter(ImageFilter.GaussianBlur(radius=outline_data_1.blur_strength))
            outline_1_layer = outline_1_layer.filter(ImageFilter.GaussianBlur(radius=outline_data_1.blur_strength))
            outline_1_layer = outline_1_layer.convert("RGBA")
            image.paste(outline_1_over_base, (0, 0), outline_1_layer)
        else:
            image.paste(outline_1_layer, (0, 0), outline_1_layer)

    image.paste(text_layer, (0, 0), text_layer)
    return image

def apply_layer_data_to_image(image:Image.Image, layer_data:LayerData) -> Image.Image:
    
    brightness = layer_data.brightness

    gaussian_blur = layer_data.gaussian_blur
    
    motion_blur = layer_data.motion_blur
    motion_rotate = layer_data.motion_rotate

    radial_blur = layer_data.radial_blur
    radial_coords = layer_data.radial_coords

    rejection_mask_coords = layer_data.f_coords
    rejection_mask_radius = layer_data.f_radius
    rejection_mask_blur_strength = layer_data.f_blur

    is_gaussian_blur = gaussian_blur is not None
    is_motion_blur = motion_blur is not None or motion_rotate is not None
    is_radial_blur = radial_blur is not None or radial_coords is not None
    is_rejection_filter = rejection_mask_coords is not None or rejection_mask_radius is not None or rejection_mask_blur_strength is not None

    if brightness is not None:
        if is_rejection_filter:
            image = cfr_adjust_brightness(
                image, brightness,
                mask_radius=rejection_mask_radius,
                mask_blur_strength=rejection_mask_blur_strength,
                mask_displacement=rejection_mask_coords
            )
        else:
            image = adjust_brightness(image, brightness)

    elif is_gaussian_blur:
        if is_rejection_filter:
            image = cfr_apply_gaussian_blur(
                image, gaussian_blur,
                mask_radius=rejection_mask_radius,
                mask_blur_strength=rejection_mask_blur_strength,
                mask_displacement=rejection_mask_coords
            )
        else:
            image = apply_gaussian_blur(image, gaussian_blur)

    elif is_motion_blur:
        if is_rejection_filter:
            image = cfr_apply_motion_blur(
                image, motion_blur,
                mask_radius=rejection_mask_radius,
                mask_blur_strength=rejection_mask_blur_strength,
                mask_displacement=rejection_mask_coords
            )
        else:
            image = apply_motion_blur(image, motion_blur, angle=motion_rotate)

    elif is_radial_blur:
        image = apply_radial_blur(image, focal_point=radial_coords, kernel_size=radial_blur)
    
    return image

def apply_subtitle_to_image(image:Image.Image, subtitle:Subtitle) -> Image.Image:
    # applies data from the subtitle to the image.

    # expand subtitle.
    subtitle_profile = subtitle.subtitle_profile
    content = subtitle.content

    asset_data = subtitle_profile.asset_data

    # add background image (if any)
    layer_data = subtitle_profile.layer_data
    if layer_data is not None:
        image = apply_layer_data_to_image(image, layer_data)

    if asset_data is not None and asset_data.path is not None:
        path = asset_data.path
        coords = asset_data.coords
        scale = asset_data.scale
        rotate = asset_data.rotate
        
        asset_image = Image.open(path)
        apply_image(image, asset_image, displacement=coords, scale=scale, rotate=rotate)

    if content is not None:
        image = apply_text_to_image(image, subtitle)

    return image

class SubtitleService:
    def __init__(self, subtitle_model:SubtitleDataAccessService=None):
        self.subtitle_model = subtitle_model

    def apply_subtitle_group(self, subtitle_group:SubtitleGroup) -> Image.Image:
        image_id = subtitle_group.image_id
        subtitle_list = subtitle_group.subtitle_list
        image_path = os.path.join(self.subtitle_model.input_image_directory, image_id)
        image = Image.open(image_path).copy()
        for subtitle in subtitle_list:
            if subtitle.content is None or list(subtitle.content) == 0:
                continue
            image = apply_subtitle_to_image(image, subtitle)
        return image

    def add_subtitles(self, filter_dict:Dict[str, Union[List[int], str]]=None):
        # add subtitles to images.

        image_paths = self.subtitle_model.get_image_paths()
        image_paths.sort()
        image_ids = list(map(os.path.basename, image_paths))
        image_id_set = set(image_ids)

        subtitle_groups = self.subtitle_model.get_subtitle_groups()
        # validation layer here.
        for text_path in subtitle_groups.keys():
            for image_id in subtitle_groups.get(text_path).keys():
                validate_subtitle_group(subtitle_groups.get(text_path).get(image_id), image_id_set=image_id_set)

        for text_path in subtitle_groups.keys():
            
            text_id = os.path.basename(text_path)
            if filter_dict is not None:
                if text_id in filter_dict.keys():
                    if isinstance(filter_dict.get(text_id), list):
                        filter_list = filter_dict.get(text_id)
                        filtered_image_paths = []
                        for index in filter_list:
                            if 0 <= index <= len(image_paths)-1:
                                filtered_image_paths.append(image_paths[index])
                            else:
                                logger.warning(f"Index {index} is out of bounds for image list with {len(image_paths)} images, skipping.")
                        # filtered_image_paths = list(map(lambda i:image_paths[i]), filter_list)
                        filtered_image_ids = list(map(os.path.basename, filtered_image_paths))
                    elif isinstance(filter_dict.get(text_id), str) and filter_dict.get(text_id) == "all":
                        filtered_image_paths = image_paths
                        filtered_image_ids = image_ids
                else:
                    logger.warning(f"Draft ID {text_id} is not in input text directory, skipping.")
                    continue
            else:
                filtered_image_paths = image_paths
                filtered_image_ids = image_ids

            n = len(filtered_image_paths)
            logger.info(f"Gathered {n} images to process: {filtered_image_ids}.")

            subtitle_group_by_text_id = subtitle_groups[text_path]

            output_directory_by_text_id = os.path.join(
                self.subtitle_model.output_directory, os.path.splitext(os.path.basename(text_path))[0]
            )
            if not os.path.exists(output_directory_by_text_id):
                logger.info(f"Created output directory {output_directory_by_text_id}")
                os.makedirs(output_directory_by_text_id)

            for i, image_path in enumerate(filtered_image_paths):
                image_id = filtered_image_ids[i]
                output_image_path = os.path.join(output_directory_by_text_id, image_id)
                if image_id in subtitle_group_by_text_id.keys():
                    subtitle_group = subtitle_group_by_text_id[image_id]
                    processed_image = self.apply_subtitle_group(subtitle_group)
                    processed_image.save(output_image_path)
                else:
                    Image.open(image_path).save(output_image_path)
                logger.info(f"Processed and saved image {i+1}/{n} ({image_id}) for text_id {text_id}.")
            logger.info(f"Finished processing {n} images for text ID {text_id}")

        pass
    pass
