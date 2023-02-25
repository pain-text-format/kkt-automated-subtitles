from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import cv2
import numpy as np

def cv2_to_pil(cv2_image):
    return Image.fromarray(cv2.cvtColor(cv2.convertScaleAbs(cv2_image), cv2.COLOR_BGRA2RGBA))
    # return Image.fromarray(cv2.cvtColor(cv2.convertScaleAbs(cv2_image), cv2.COLOR_BGRA2RGBA))
def pil_to_cv2(pil_image):
    # return cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGRA2RGBA)
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGRA2RGB)

def in_cv2_environment(fn):
    # creates a cv2 environment for a cv2-valued function.
    def decorated_fn(image, *args, **kwargs):
        return cv2_to_pil(fn(pil_to_cv2(image), *args, **kwargs))
    return decorated_fn

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

def apply_image(image:Image.Image, applying_image:Image.Image, displacement:tuple=None, scale:float=None, rotate:int=None) -> Image.Image:

    if displacement is None:
        displacement = (0, 0)
    if scale is not None:
        size = applying_image.size
        new_image_size = (int(size[0]*scale), int(size[1]*scale))
        applying_image = applying_image.resize(new_image_size)
    if rotate is not None:
        applying_image = applying_image.rotate(rotate)

    image_width, image_height = image.size
    new_image_width, new_image_height = new_image_size
    
    x = image_width//2-new_image_width//2+displacement[0]
    y = image_height//2-new_image_height//2-displacement[1]

    image.paste(applying_image, (x, y), applying_image)
    return image