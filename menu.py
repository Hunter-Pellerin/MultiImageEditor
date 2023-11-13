import customtkinter as ctk
from PIL.Image import Image
from typing import Any, Callable
from panel import *
from defaults import *

editing_mode = None

class Menu(ctk.CTkTabview):
    def __init__(self, parent: ctk.CTk, pos_vars: dict[Any], color_vars: dict[Any],
        effect_vars: dict[Any], image: Image, export_func: Callable[[str, str, str],None]
    ):
        super().__init__(master=parent)
        self.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Tabs
        self.add('Position')
        self.add('Color')
        self.add('Effect')
        self.add('Export')

        # Widgets
        PositionFrame(self.tab('Position'), pos_vars)
        ColorFrame(self.tab('Color'), image, color_vars)
        EffectFrame(self.tab('Effect'), effect_vars)
        ExportFrame(self.tab('Export'), export_func)

class PositionFrame(ctk.CTkFrame):
    # CTkFrame to control image positioning, such as rotation, zoom and flipping.

    def __init__(self, parent: ctk.CTkFrame, pos_vars: dict[Any]) -> None:
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(
            self,
            panel_name='Rotation',
            data_var=pos_vars['rotation'],
            min_value=0,
            max_value=360,
        )
        SliderPanel(
            self,
            panel_name='Zoom',
            data_var=pos_vars['zoom'],
            min_value=0,
            max_value=400,
        )
        SegmentedPanel(
            self,
            panel_name='Invert',
            data_var=pos_vars['flip'],
            options=FLIP_AXIS_OPTIONS,
        )
        RevertButton(
            self,
            (pos_vars['rotation'], ROTATION_DEFAULT),
            (pos_vars['zoom'], ZOOM_DEFAULT),
            (pos_vars['flip'], FLIP_AXIS_OPTIONS[0]),
        )

def get_image(image: str | Image) -> Image:
    return Image.open(image) if isinstance(image, str) else image

class ColorFrame(ctk.CTkFrame):
    """
    CTkFrame to apply image color filters and effects (grayscale, 4-color, inversion),
    with functionality to extract colors from the image.
    """
    def __init__(self, parent: ctk.CTkFrame, image: Image, color_vars: dict[Any]) -> None:
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')
        self.image_file = get_image(image)

        SwitchPanel(
            self,
            (color_vars['grayscale'], 'B/W'),
            (color_vars['invert'], 'Negative'),
            (color_vars['4-color'], '4-Color'),
        )
        SliderPanel(
            self,
            panel_name='Brightness',
            data_var=color_vars['brightness'],
            min_value=0,
            max_value=5,
        )
        SliderPanel(
            self,
            panel_name='Saturation',
            data_var=color_vars['saturation'],
            min_value=0,
            max_value=5,
        )

        ColorsPanel(self, self.image_file)

        RevertButton(
            self,
            (color_vars['grayscale'],  GRAYSCALE_DEFAULT),
            (color_vars['invert'],     INVERT_DEFAULT),
            (color_vars['4-color'],    FOUR_COLOR_DEFAULT),
            (color_vars['brightness'], BRIGHTNESS_DEFAULT),
            (color_vars['saturation'], SATURATION_DEFAULT),
        )


class EffectFrame(ctk.CTkFrame):
    """
    CTkFrame to apply different effects to the open image,
    such as blurring, changing contrast, hue.
    """
    def __init__(self, parent: ctk.CTkFrame, effect_vars: dict[Any]) -> None:
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        SliderPanel(
            self,
            panel_name='Blur',
            data_var=effect_vars['blur'],
            min_value=0,
            max_value=30,
        )
        SliderPanel(
            self,
            panel_name='Contrast',
            data_var=effect_vars['contrast'],
            min_value=0,
            max_value=10,
        )
        SliderPanel(
            self,
            panel_name='Hue',
            data_var=effect_vars['hue'],
            min_value=-100,
            max_value=100,
        )

        RevertButton(
            self,
            (effect_vars['blur'], BLUR_DEFAULT),
            (effect_vars['contrast'], CONTRAST_DEFAULT),
            (effect_vars['hue'], HUE_DEFAULT),
        )


class ExportFrame(ctk.CTkFrame):
    # CTkFrame to export the open image in different output formats.

    def __init__(self, parent: ctk.CTkFrame, export_func: Callable):
        super().__init__(master=parent, fg_color='transparent')
        self.pack(expand=True, fill='both')

        self.file_name = ctk.StringVar()
        self.file_extension = ctk.StringVar(value='jpg')
        self.path = ctk.StringVar()
        self.quality = ctk.DoubleVar(value=100)

        if editing_mode.get() == "Single Image Mode":
            FileNamePanel(self, self.file_name, self.file_extension, self.quality)
        FilePathPanel(self, self.path)

        ExportButton(
            self, export_func, self.file_name, self.file_extension, self.path,
        )

# Switch between multi and single image editing modes
def ChangeEditingMode(new_mode: str):
    global editing_mode
    editing_mode.set(new_mode)

# Initialize the menu for image editing modes
class EditModeMenu(ctk.CTkOptionMenu):
    def __init__(self, parent: ctk.CTk):
        super().__init__(master=parent, values=["Single Image Mode", "Multi Image Mode"], command=ChangeEditingMode)
        self.grid(column=0, columnspan=2, row=0, sticky='nsew', padx=(parent.winfo_width()/3), pady=(parent.winfo_height()/3))
        self.set("Editing Mode")