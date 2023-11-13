import customtkinter as ctk
from tkinter import *
from time import sleep
from PIL import Image, ImageTk, ImageDraw
from defaults import *
from tkwidgets import *
import menu
from tools.image_editor import *
from multiprocessing import Process, cpu_count
import os

image_names = []

class MainWindow(ctk.CTk):
	def __init__(self):
		super().__init__()
	
		ctk.set_appearance_mode('System')
		self.geometry('1280x800+50+50')
		self.title('Pyaint Photo Editor')
		self.DefaultImageEffects()

		# Window Layout
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=2, uniform='a')
		self.columnconfigure(1, weight=6, uniform='a')

		#Widgets
		menu.editing_mode = ctk.StringVar(value=None)
		edit_menu = menu.EditModeMenu(self)
		self.wait_img_names = ctk.BooleanVar(value=True)

		edit_menu.wait_variable(menu.editing_mode)
		if menu.editing_mode.get() == "Single Image Mode":
			edit_menu.grid_forget()
			self.image_imported = ImportImageWithDialog(self, importer=self.ImportImage)
		elif menu.editing_mode.get() == "Multi Image Mode":
			self.processes = []
			edit_menu.grid_forget()
			self.image_imported = ImportImageDirectoryWithDialog(self, importer=self.ImportImageDir)

			self.wait_variable(self.wait_img_names)
			self.images_directory = self.image_imported.filepath

			for img_name in image_names:
				self.processes.append(Multi(img_name, self.images_directory))
			for process in self.processes:
				process.DefaultImageEffects()

			self.image_imported = self.ImportImage(os.path.join(self.images_directory, image_names[0]))

		self.mainloop()

	def DefaultImageEffects(self):
		self.image_position = {
			"rotation": ctk.DoubleVar(value=ROTATION_DEFAULT),
			"zoom":       ctk.DoubleVar(value=ZOOM_DEFAULT),
			"flip":       ctk.StringVar(value=FLIP_AXIS_OPTIONS[0])
		}

		self.image_effects = {
			"blur":      ctk.DoubleVar(value=BLUR_DEFAULT),
			"contrast": ctk.IntVar(value=CONTRAST_DEFAULT),
			"hue":       ctk.IntVar(value=HUE_DEFAULT)
		}

		self.image_filters = {
			"brightness": ctk.DoubleVar(value=BRIGHTNESS_DEFAULT),
			"grayscale":  ctk.DoubleVar(value=GRAYSCALE_DEFAULT),
			"invert":     ctk.DoubleVar(value=INVERT_DEFAULT),
			"4-color":    ctk.BooleanVar(value=FOUR_COLOR_DEFAULT),
			"saturation": ctk.DoubleVar(value=SATURATION_DEFAULT)
		}

		all_effects = (
			list(self.image_position.values()) +
			list(self.image_effects.values()) +
			list(self.image_filters.values())
		)

		# apply all default values for effects to the sliders
		# and widgets for tkinter
		for attribute in all_effects:
			attribute.trace('w', self.EditImageEffects)

	def EditImageEffects(self, *args):
		self.image = self.image_og
		# Edit the image the values from the GUI sliders and buttons
		editor = ImageEditor(self.image)

		editor.rotation(self.image_position["rotation"].get())
		editor.zoom(self.image_position["zoom"].get())
		editor.flip(self.image_position["flip"].get())
		editor.brightness(self.image_filters["brightness"].get())
		editor.saturation(self.image_filters["saturation"].get())
		editor.grayscale(self.image_filters["grayscale"].get())

		try:
			editor.color_invert(self.image_filters["invert"].get())
		except:
			tkinter.messagebox.showerror("Invalid operation", "Cannot apply inversion to image filetype.")

		editor.four_color_filter(self.image_filters["4-color"].get())
		editor.blur(self.image_effects["blur"].get())
		editor.contrast(self.image_effects["contrast"].get())
		editor.hue(self.image_effects["hue"].get())

		# When edits are done, display the resulting image
		self.image = editor.get_image_output
		self.DisplayImage()

	def onExit(self):
		self.quit()

	def ImportImage(self, path, isMaster=False):
		self.image_og = Image.open(path)
		self.image = self.image_og # copy of image to revert back to original
		self.image_tk = PhotoImage(self.image)
		self.image_aspect_ratio = self.image.size[0] / self.image.size[1]

		# remove import ui and display editor
		self.image_imported.grid_forget()

		self.image_output = ShowImage(self, resizer=self.ResizeImage)
		self.close_button = CloseImageViewerButton(self, closer=self.CloseEditor)

		self.effect_menu = menu.Menu(
			self,
			self.image_position,
			self.image_filters,
			self.image_effects,
			self.image,
			self.ExportImage if menu.editing_mode.get() == "Single Image Mode" else self.ExportImages,
		)

	def ImportImageDir(self, dirpath):
		global image_names
		image_names = [img_name for img_name in os.listdir(dirpath) if img_name.endswith(('.png', '.jpeg', '.jpg'))]
		self.wait_img_names.set(False)

	def DisplayImage(self):
		self.image_output.delete('all')
		image_resized = self.image.resize(
			(self.image_width, self.image_height)
		)

		self.image_tk = ImageTk.PhotoImage(image_resized)
		self.image_output.create_image(
			0.5 * self.width,
			0.5 * self.height,
			image = self.image_tk,
			anchor = 'center',
		)

	def ResizeImage(self, event):
		self.height = event.height
		self.width = event.width
		aspect_ratio = self.width / self.height

		if aspect_ratio > self.image_aspect_ratio:   # Canvas is wider than image
			self.image_height = int(self.height)
			self.image_width = int(self.image_height * self.image_aspect_ratio)
		else:   # Canvas is taller than image
			self.image_width = int(self.width)
			self.image_height = int(self.image_width / self.image_aspect_ratio)

		self.DisplayImage()

	def CloseEditor(self):
		self.image_output.grid_forget()
		self.close_button.place_forget()
		self.effect_menu.grid_forget()
		self.effect_menu.pack_forget()
		self.image_imported = ImportImageWithDialog(parent=self, importer=self.ImportImage)

	def ExportImage(self, filename, extension, output_path):
		export_dir = "{}/{}.{}".format(output_path, filename, extension)
		IS_JPG = self.image.format and self.image.format.lower() in ('jpeg', 'jpg')
		if IS_JPG:
			quality='keep'
		else:
			quality=100

		self.image.save(export_dir, quality=quality, optimize=False)

		if menu.editing_mode.get() == "Single Image Mode":
			tkinter.messagebox.showinfo(
				title='Done', message='Successfully exported image file.'
			)

	def ExportImages(self, output_path):
		export_info = self.processes[0].image_location
		self.ExportImage(export_info[1], export_info[2], output_path)
		effects = [self.image_position, self.image_effects, self.image_filters]

		

		for process in self.processes:
			process.EditImageEffects(effects)
			process.ExportImage(output_path)

		tkinter.messagebox.showinfo(
			title='Done', message='Successfully exported {} image files.'.format(len(self.processes))
		)	


# class for editing multiple images
class Multi(MainWindow):
	def __init__(self, img_name, directory):
		self.ImportImage(os.path.join(directory, img_name))

	def ImportImage(self, path):
		self.image_location = list(os.path.split(path))
		name, extension = map(str, self.image_location[1].split('.'))
		self.image_location[1] = name
		self.image_location.append(extension)

		self.image_og = Image.open(path)
		self.image_aspect_ratio = self.image_og.size[0] / self.image_og.size[1]

	def EditImageEffects(self, effects, *args):
		self.image = self.image_og
		# Edit the image the values from the GUI sliders and buttons
		editor = ImageEditor(self.image)

		image_position, image_effects, image_filters = effects[0], effects[1], effects[2]

		editor.rotation(image_position["rotation"].get())
		editor.zoom(image_position["zoom"].get())
		editor.flip(image_position["flip"].get())
		editor.brightness(image_filters["brightness"].get())
		editor.saturation(image_filters["saturation"].get())
		editor.grayscale(image_filters["grayscale"].get())

		try:
			editor.color_invert(image_filters["invert"].get())
		except:
			tkinter.messagebox.showerror("Invalid operation", "Cannot apply inversion to image filetype.")

		editor.four_color_filter(image_filters["4-color"].get())
		editor.blur(image_effects["blur"].get())
		editor.contrast(image_effects["contrast"].get())
		editor.hue(image_effects["hue"].get())

		# When edits are done, display the resulting image
		self.image = editor.get_image_output

	def ExportImage(self, output_path):
		_, filename, extension = map(str, self.image_location)
		export_dir = "{}/{}.{}".format(output_path, filename, extension)
		IS_JPG = self.image.format and self.image.format.lower() in ('jpeg', 'jpg')
		if IS_JPG:
			quality='keep'
		else:
			quality=100

		self.image.save(export_dir, quality=quality, optimize=False)	

if __name__ == '__main__':
	MainWindow()