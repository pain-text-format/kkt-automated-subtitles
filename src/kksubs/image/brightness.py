from PIL import Image, ImageEnhance
from kksubs.image.utils import circular_filter_rejection

def adjust_brightness(image:Image.Image, brightness) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    adjusted_image = enhancer.enhance(brightness)
    return adjusted_image

cfr_adjust_brightness = circular_filter_rejection(adjust_brightness)