from kksubs.image.motion_blur import apply_horizontal_blur
from kksubs.image.utils import cv2_to_pil, in_cv2_environment, pil_to_cv2
import numpy as np
from PIL import Image
import cv2

def get_gradient_mask(image, alpha_fn=None):
    if alpha_fn is None:
        alpha_fn = lambda r, h:min(int(r/h*255*2), 255)
    width, height, _ = image.shape
    gradient_mask = np.zeros((width, height, 4))
    for r in range(height):
        # Calculate the alpha value for this column
        alpha = alpha_fn(r, height)
        # alpha = 0 if r < 500 else 255
        # Set the alpha channel of every pixel in this column to the calculated value
        gradient_mask[:, r, 3] = alpha
    return gradient_mask

def apply_gradient_mask(fn):
    # applies a mask over an image-valued function.
    def decorated_fn(image, *args, alpha_fn=None, **kwargs):
        mask = get_gradient_mask(image, alpha_fn=alpha_fn)
        image_to_paste = fn(image, *args, **kwargs)
        i2p_pil = cv2_to_pil(image_to_paste)
        mask_pil = cv2_to_pil(mask)
        image_pil = cv2_to_pil(image)
        image_pil.paste(i2p_pil, (0, 0), mask_pil)
        return pil_to_cv2(image_pil)
    return decorated_fn

def get_value(image, focal_point):
    # returns sup(dist(focal_point, x:x in image)) via programming.
    width, height = image.shape[0], image.shape[1]
    # print(width, height)
    # print(focal_point[0], focal_point[1])
    ul = np.array((0, 0))
    ur = np.array((width, 0))
    ll = np.array((0, height))
    lr = np.array((width, height))
    return np.max([np.linalg.norm(corner - np.array(focal_point)) for corner in [ul, ur, ll, lr]])

def to_polar_coordinates(fn):
    # creates a polar coordinate environment within a cartesian coordinate environment.
    # transforms image from cartesian to polar, passes to inner function, then recovers cartesian output.
    def decorated_fn(image, *args, focal_point=None, **kwargs):
        if focal_point is None:
            focal_point = (image.shape[0]/2, image.shape[1]/2)
        focal_point_reverse = (focal_point[1], focal_point[0]) # for some reason this needs to be reversed.
        image = image.astype(np.float32)
        # print(get_value(image, focal_point))
        value = get_value(image, focal_point)
        # value = np.sqrt(((image.shape[0]/2)**2.0)+((image.shape[1]/2)**2.0))
        # print(value)
        input_polar_image = cv2.linearPolar(image, focal_point_reverse, value, cv2.WARP_FILL_OUTLIERS)
        output_polar_image = fn(input_polar_image, *args, **kwargs)
        # cv2.imwrite("1.png", output_polar_image)
        linear_img =cv2.linearPolar(output_polar_image, focal_point_reverse, value, cv2.WARP_FILL_OUTLIERS+cv2.WARP_INVERSE_MAP)
        return linear_img
    return decorated_fn

def apply_radial_blur(image, focal_point=None, kernel_size=None, alpha_fn=None):
    # apply radial/perspective blur.
    # this is not the best implementation of radial blur, there are still many issues with it. However, it is fast.
    # focal point will start from center of image by default
    return in_cv2_environment(to_polar_coordinates(
        apply_gradient_mask(apply_horizontal_blur)
    ))(
        image, focal_point=focal_point, kernel_size=kernel_size, alpha_fn=alpha_fn
    )