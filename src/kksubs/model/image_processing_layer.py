from PIL import Image, ImageEnhance, ImageFilter, ImageDraw
import cv2
import numpy as np

def cv2_to_pil(cv2_image):
    return Image.fromarray(cv2.cvtColor(cv2.convertScaleAbs(cv2_image), cv2.COLOR_BGR2RGBA))
def pil_to_cv2(pil_image):
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_BGRA2RGBA)

def in_cv2_environment(fn):
    # creates a cv2 environment for a cv2-valued function.
    def decorated_fn(image, *args, **kwargs):
        return cv2_to_pil(fn(pil_to_cv2(image), *args, **kwargs))
    return decorated_fn

def id(image):
    # identity function.
    return image

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

def apply_horizontal_blur(image, kernel_size=None):
    if kernel_size is None:
        kernel_size = 50
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[int((kernel_size - 1)/2), :] = np.ones(kernel_size)
    kernel /= kernel_size
    horizontally_blurred_image = cv2.filter2D(image, -1, kernel)
    return horizontally_blurred_image

def apply_vertical_blur(image, kernel_size=None):
    if kernel_size is None:
        kernel_size = 50
    kernel = np.zeros((kernel_size, kernel_size))
    kernel[:,int((kernel_size - 1)/2)] = np.ones(kernel_size)
    kernel /= kernel_size
    vertically_blurred_image = cv2.filter2D(image, -1, kernel)
    return vertically_blurred_image

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

def adjust_brightness(image:Image.Image, brightness) -> Image.Image:
    enhancer = ImageEnhance.Brightness(image)
    adjusted_image = enhancer.enhance(brightness)
    return adjusted_image

def apply_gaussian_blur(image:Image.Image, blur_strength) -> Image.Image:
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=blur_strength))
    return blurred_image

def get_sup_kernel_size(kernel_size):
    parity = kernel_size%2
    # must be odd.
    result = int(np.ceil(np.sqrt(2)*kernel_size))
    if result%2==parity:
        return result
    return result+1

# get the nxn submatrix from an NxN matrix (starting from the center).
# assume n, N are odd, and N-n > 0.
# (N-n)/2 is the diff.
def get_center_submatrix(super_matrix, n, N=None):
    if N is None:
        N = len(super_matrix)
    difference = int((N-n)/2)
    return super_matrix[difference:difference+n, difference:difference+n]

def apply_motion_blur(image:Image.Image, kernel_size=None, angle=None) -> Image.Image:
    if kernel_size is None or kernel_size == 0:
        return image
    if angle is None:
        angle = 0
    if angle%180==0:
        return apply_horizontal_blur(image, kernel_size=kernel_size)
    if angle%180==90:
        return apply_vertical_blur(image, kernel_size=kernel_size)

    if kernel_size%2==0:
        # warn that kernel size is even, will be incremented so it is odd.
        kernel_size += 1
    # convert image to cv2
    cv2_image = np.array(image.convert("RGB"))[:,:,::-1].copy()

    sup_kernel_size = get_sup_kernel_size(kernel_size)
    # print(sup_kernel_size)
    sup_kernel = np.zeros((sup_kernel_size, sup_kernel_size))
    sup_kernel[int((sup_kernel_size-1)/2), :] = np.ones(sup_kernel_size)
    sup_kernel = sup_kernel * 255
    sup_kernel_as_image = Image.fromarray(sup_kernel)
    rotated_sup_kernel = sup_kernel_as_image.rotate(angle)
    rotated_sup_kernel = np.asarray(rotated_sup_kernel)
    rotated_kernel = get_center_submatrix(rotated_sup_kernel, kernel_size, sup_kernel_size)/255/kernel_size
    rotated_mb = cv2.filter2D(cv2_image, -1, rotated_kernel)
    blurred_image = Image.fromarray(cv2.cvtColor(rotated_mb, cv2.COLOR_BGR2RGB))
    # convert cv2 to image.
    return blurred_image

def apply_radial_blur(image, focal_point=None, kernel_size=None, alpha_fn=None):
    # apply radial/perspective blur.
    # this is not the best implementation of radial blur, there are still many issues with it. However, it is fast.
    # focal point will start from center of image by default
    return in_cv2_environment(to_polar_coordinates(
        apply_gradient_mask(apply_horizontal_blur)
    ))(
        image, focal_point=focal_point, kernel_size=kernel_size, alpha_fn=alpha_fn
    )

cfr_adjust_brightness = circular_filter_rejection(adjust_brightness)
cfr_apply_gaussian_blur = circular_filter_rejection(apply_gaussian_blur)
cfr_apply_motion_blur = circular_filter_rejection(apply_motion_blur)