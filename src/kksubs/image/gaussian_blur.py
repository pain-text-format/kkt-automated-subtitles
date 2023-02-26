from PIL import Image, ImageFilter
from kksubs.image.utils import circular_filter_rejection

def apply_gaussian_blur(image:Image.Image, blur_strength) -> Image.Image:
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_strength))
    return blurred_image

cfr_apply_gaussian_blur = circular_filter_rejection(apply_gaussian_blur)