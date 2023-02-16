import logging
import os.path
import textwrap

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

from kksubs.model.data_access_services import SubtitleDataAccessService
from kksubs.model.domain_models import Subtitle, SubtitleGroup
from kksubs.model.validate import validate_subtitle_group

logger = logging.getLogger(__name__)

def _get_text_dimensions(text_string, font, default_text_width=None, default_text_height=None):
    if text_string == "":
        return default_text_width, default_text_height
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return text_width, text_height

def apply_image(image:Image.Image, background_image) -> Image.Image:
    image.paste(background_image, (0, 0), background_image)
    return image

def adjust_brightness(image:Image.Image, brightness) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    adjusted_image = enhancer.enhance(brightness)
    return adjusted_image

def apply_gaussian_blur(image:Image.Image, blur_strength) -> Image.Image:
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_strength))
    return blurred_image

# TODO
def apply_motion_blur(image:Image.Image, intensity, argument) -> Image.Image:
    # apply motion blur with assigned intensity and radial argument (0-180 degrees ccw).
    # radial argument can be either an int (degrees), or a string:
    # h (horizontal), v (vertical), d (diagonal from top left), a (anti-diagonal from bottom left).
    return image

def circular_filter_rejection(fn):
    # applies a mask that rejects a filter about a circle on the image. The rejection is smoothed on the boundary via gaussian filtering.

    def filter_fn(image, *args, mask_radius:int=None, mask_blur_strength:int=None, mask_displacement:tuple=None, **kwargs):
        if mask_radius is None:
            mask_radius = 200
        if mask_blur_strength is None:
            mask_blur_strength = 200
        if mask_displacement is None:
            mask_displacement = (0, 0)
        
        dis_x, dis_y = mask_displacement # displacement from center.
        image_width, image_height = image.size
        x, y = image_width//2+dis_x, image_height//2+dis_y # new center of focus.
        filtered_image = fn(image, *args, **kwargs)
        mask_layer = Image.new("RGB", image.size, "white")
        mask_draw = ImageDraw.Draw(mask_layer)
        mask_draw.ellipse((x-mask_radius, y-mask_radius, x+mask_radius, y+mask_radius), fill="black")
        mask_layer = mask_layer.convert("L").filter(ImageFilter.GaussianBlur(radius=mask_blur_strength))
        image.paste(filtered_image, (0, 0), mask_layer)
        return image
    
    return filter_fn

focal_blur_image = circular_filter_rejection(apply_gaussian_blur)

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
    tb_anchor_x, tb_anchor_y = textbox_data.anchor_point
    box_width = textbox_data.box_width
    push = textbox_data.push

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

    text_dimensions = [_get_text_dimensions(line, font, default_text_width=default_text_width, default_text_height=default_text_height) for line in wrapped_text]
    text_widths = list(map(lambda dim:dim[0], text_dimensions))
    max_text_width = max(text_widths)
    num_lines = len(wrapped_text)
    sum_text_height = num_lines * default_text_height

    # add text.
    for i, line in enumerate(wrapped_text):
        text_width = font.getlength(line)

        if alignment == "left":
            x = (image_width + text_width)/2 + tb_anchor_x - text_width/2
        elif alignment == "center":
            x = image_width/2 + tb_anchor_x - text_width/2
        elif alignment == "right":
            x = (image_width - text_width)/2 + tb_anchor_x - text_width/2
        else:
            raise ValueError(f"Invalid alignment value {alignment}.")
        if push == "up":
            y = image_height/2 - tb_anchor_y + (- default_text_height*(num_lines-i))
        elif push == "down":
            y = image_height/2 - tb_anchor_y + (sum_text_height - default_text_height*(num_lines-i))
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
        image.paste(text_layer, (0, 0), text_layer)

    # apply paste
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

def apply_subtitle_to_image(image:Image.Image, subtitle:Subtitle) -> Image.Image:
    # applies data from the subtitle to the image.

    # expand subtitle.
    subtitle_profile = subtitle.subtitle_profile
    content = subtitle.content

    layer_data = subtitle_profile.layer_data

    # add background image (if any)
    if layer_data is not None:
        background_path = layer_data.background_path
        image_blur_strength = layer_data.blur_strength
        image_brightness = layer_data.brightness
        if background_path is not None:
            background_image = Image.open(background_path)
            image = apply_image(image, background_image)
        if image_blur_strength is not None:
            image = apply_gaussian_blur(image, image_blur_strength)
        if image_brightness is not None:
            image = adjust_brightness(image, image_brightness)

    if content:
        image = apply_text_to_image(image, subtitle)

    # add foreground image (if any)
    if layer_data is not None:
        foreground_path = layer_data.foreground_path
        if foreground_path is not None:
            foreground_image = Image.open(foreground_path)
            image = apply_image(image, foreground_image)

    return image

class SubtitleService:
    def __init__(self, subtitle_model:SubtitleDataAccessService=None):
        self.subtitle_model = subtitle_model

    def rename_images(self, padding_length=None, start_at=None):
        # Perform image renaming so it is structured and in alphabetical order.

        image_paths = self.subtitle_model.get_image_paths()
        image_paths.sort()
        n = len(image_paths)

        if padding_length is None:
            padding_length = len(str(n))
        if start_at is None:
            start_at = 0

        for i, image_path in enumerate(image_paths):
            directory = self.subtitle_model.input_image_directory
            extension = os.path.splitext(image_path)[1]
            image_index = str(i+start_at).rjust(padding_length, "0")
            new_basename = f"{image_index}{extension}"
            new_image_path = os.path.join(directory, new_basename)
            os.rename(image_path, new_image_path)

        logger.info(f"Renamed {n} images in directory {self.subtitle_model.input_image_directory}.")

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

    def add_subtitles(self, filter_list=None):
        # add subtitles to images.

        image_paths = self.subtitle_model.get_image_paths()
        image_paths.sort()
        image_ids = list(map(os.path.basename, image_paths))
        image_id_set = set(image_ids)

        subtitle_groups = self.subtitle_model.get_subtitle_groups()
        # validation layer here.
        for text_id in subtitle_groups.keys():
            for image_id in subtitle_groups.get(text_id).keys():
                validate_subtitle_group(subtitle_groups.get(text_id).get(image_id), image_id_set=image_id_set)
        
        if filter_list is not None:
            image_paths = list(map(lambda i:image_paths[i], filter_list))

        n = len(image_paths)

        for text_id in subtitle_groups.keys():
            subtitle_group_by_text_id = subtitle_groups[text_id]

            output_directory_by_text_id = os.path.join(
                self.subtitle_model.output_directory, os.path.splitext(os.path.basename(text_id))[0]
            )
            if not os.path.exists(output_directory_by_text_id):
                os.makedirs(output_directory_by_text_id)

            for i, image_path in enumerate(image_paths):
                image_id = image_ids[i]
                output_image_path = os.path.join(output_directory_by_text_id, image_id)
                if image_id in subtitle_group_by_text_id.keys():
                    subtitle_group = subtitle_group_by_text_id[image_id]
                    processed_image = self.apply_subtitle_group(subtitle_group)
                    processed_image.save(output_image_path)
                else:
                    Image.open(image_path).save(output_image_path)
                logger.info(f"Processed and saved image {i+1}/{n} for text_id {os.path.splitext(os.path.basename(text_id))[0]}.")

        pass

    pass