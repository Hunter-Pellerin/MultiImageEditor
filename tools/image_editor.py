"""
Module responsible for providing image manipulation functionalities.
"""

from defaults import *
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np

class ImageEditor:
    """
    Class containing all image-manipulation methods used in the app.
    """
    def __init__(self, image_file: Image.Image) -> None:
        self.used_image = image_file
        if self.used_image.mode == 'P':
            self.used_image = self.used_image.convert('RGB')


    def rotation(self, rotation_angle: float) -> None:
        """
        Apply a rotation by a given angle to the image.

        Args:
            rotation_angle (float): rotation angle.
        """
        if rotation_angle != ROTATION_DEFAULT:
            self.used_image = self.used_image.rotate(angle=rotation_angle)

    def zoom(self, zoom_amount: float) -> None:
        """
        Zoom the image by a given amount.

        Args:
            zoom_amount (float): The given zoom amount.
        """
        if zoom_amount != ZOOM_DEFAULT:
            self.used_image = ImageOps.crop(self.used_image, border=zoom_amount)

    def flip(self, flip_option: str) -> None:
        """
        Flip the image horizontally, vertically, or both ways.

        Args:
            flip_option (str): The flip type, can be 'X' for horizontal,
            'Y' for vertical, and 'Both' for both directions.
        """
        if flip_option != 'None':
            mirror = flip_option in ('X', 'Both')
            flip = flip_option in ('Y', 'Both')
            if mirror:
                self.used_image = ImageOps.mirror(self.used_image)
            if flip:
                self.used_image = ImageOps.flip(self.used_image)

    def brightness(self, brightness_value: float) -> None:
        """
        Change the image brightness by a given amount.

        Args:
            brightness_value (float): New brightness value. When set to 0,
            the image becomes completely black.
        """
        if brightness_value != BRIGHTNESS_DEFAULT:
            brightness_enhancer = ImageEnhance.Brightness(self.used_image)
            self.used_image =  brightness_enhancer.enhance(brightness_value)

    def saturation(self, saturation_value: float) -> None:
        """
        Change the image vibrance by a given amount.

        Args:
            vibrance_value (float): New vibrance value. When set to 0,
            the image becomes grayscale.
        """
        if saturation_value != SATURATION_DEFAULT:
            brightness_enhancer = ImageEnhance.Color(self.used_image)
            self.used_image =  brightness_enhancer.enhance(saturation_value)

    def grayscale(self, grayscale_flag: bool) -> None:
        """
        Convert the image to grayscale (Black and White).

        Args:
            grayscale_flag (bool): Set to True, if the filter is chosen.
        """
        if grayscale_flag:
             self.used_image = ImageOps.grayscale(self.used_image)

    def color_invert(self, invert_flag: bool) -> None:
        """
        Invert the image colors (Negative filter).

        Args:
            invert_flag (bool): Set to True, if the filter is chosen.
        """
        if invert_flag:
            try:
                self.used_image = ImageOps.invert(self.used_image)
            except:
                raise OSError

    def four_color_filter(self, four_col_flag: bool) -> None:
        """
        Apply a 4-color filter to the image i.e. display the image using only 4 colors,
        extracted from the image by an algorithm implemented in Pillow.

        Args:
            four_col_flag (bool): Set to True, if the filter is chosen.
        """
        if four_col_flag:
            self.used_image = self.used_image.convert("P", palette=Image.ADAPTIVE, colors=4)

    def blur(self, blur_value: float) -> None:
        """
        Blur the image by a given amount.

        Args:
            blur_value (float): Blur intensity.
        """
        if blur_value != BLUR_DEFAULT:
            blur_filter = ImageFilter.GaussianBlur(blur_value)
            self.used_image = self.used_image.filter(blur_filter)

    def contrast(self, contrast_value: float) -> None:
        """
        Change the image contrast by a given amount.

        Args:
            contrast_value (float): Used contrast value.
        """
        if contrast_value != CONTRAST_DEFAULT:
            contrast_filter = ImageFilter.UnsharpMask(contrast_value)
            self.used_image = self.used_image.filter(contrast_filter)

    def hue(self, hue_value: int) -> None:
        """
        Change the image hue (color) by a given amount.

        Args:
            hue_value (int): Ranges from -100 to 100.
        """
        if hue_value != HUE_DEFAULT:
            used_operation = np.add if hue_value > 0 else np.subtract
            hue_value = abs(hue_value)
            hsv_im = self.used_image.convert("HSV")
            h_chan, s_chan, v_chan = hsv_im.split()

            h_chan_np = np.array(h_chan)
            h_chan_np = used_operation(h_chan_np, hue_value)
            h_chan = Image.fromarray(h_chan_np)

            result = Image.merge("HSV", (h_chan, s_chan, v_chan))
            self.used_image = result.convert("RGB")

    @property
    def get_image_output(self) -> Image.Image:
        """
        Get the resulting image after applying all effects and filters.

        Returns:
            Image.Image: The resulting image.
        """
        return self.used_image