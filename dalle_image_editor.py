import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw
import requests
import io
import easygui
from openai import OpenAI

client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.openai.com/v1/"
)

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Image Generator and Editor")

        self.image_frame = tk.Frame(root)
        self.image_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.image_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.image_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')

        self.images = []
        self.selected_image = None
        self.row = 0
        self.col = 0

        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.create_button = tk.Button(button_frame, text="Generate New Image", command=self.create_image)
        self.create_button.pack(side=tk.LEFT)

        self.edit_button = tk.Button(button_frame, text="Edit Selected Image", command=self.edit_image)
        self.edit_button.pack(side=tk.LEFT)

        self.variation_button = tk.Button(button_frame, text="Create Variation of Selected", command=self.create_variation)
        self.variation_button.pack(side=tk.LEFT)

        self.open_button = tk.Button(button_frame, text="Open Image File", command=self.open_image)
        self.open_button.pack(side=tk.LEFT)

        self.save_button = tk.Button(button_frame, text="Save Selected Image", command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        self.remove_button = tk.Button(button_frame, text="Remove Selected Image", command=self.remove_image)
        self.remove_button.pack(side=tk.LEFT)

        self.clear_button = tk.Button(button_frame, text="Clear All Images", command=self.clear_images)
        self.clear_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(root, text="")
        self.status_label.pack(side=tk.BOTTOM)

    def update_status(self, message):
        self.status_label.config(text=message)

    def show_image(self, image_path):
        img = Image.open(image_path)
        img.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(img)
        
        frame = tk.Frame(self.inner_frame, bd=2, relief=tk.RAISED)
        frame.grid(row=self.row, column=self.col, padx=5, pady=5)
        
        label = tk.Label(frame, image=photo)
        label.image = photo
        label.pack()
        
        self.images.append((frame, image_path))
        
        label.bind("<Button-1>", lambda e, f=frame: self.select_image(f))
        
        self.col += 1
        if self.col >= 3:
            self.col = 0
            self.row += 1
        
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def select_image(self, frame):
        if self.selected_image:
            self.selected_image.config(bg='SystemButtonFace')
        frame.config(bg='lightblue')
        self.selected_image = frame

    def download_image(self, url):
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        img_path = f"generated_image_{len(self.images)}.png"
        img.save(img_path)
        return img_path

    def prompt_for_input(self, prompt_message):
        return simpledialog.askstring("Input Required", prompt_message)

    def get_integer(self, title, label, minv, maxv):
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.geometry("300x150")
        
        label = tk.Label(dialog, text=label)
        label.pack(pady=10)
        
        scale = tk.Scale(dialog, from_=minv, to=maxv, orient=tk.HORIZONTAL, length=200)
        scale.set(minv)
        scale.pack()
        
        result = {"value": None}
        
        def on_ok():
            result["value"] = scale.get()
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ok_button = tk.Button(dialog, text="OK", command=on_ok)
        ok_button.pack(side=tk.LEFT, padx=10, pady=10)
        
        cancel_button = tk.Button(dialog, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=10, pady=10)
        
        dialog.transient(dialog.master)
        dialog.grab_set()
        dialog.wait_window()
        
        return result["value"]

    def create_image(self):
        prompt = self.prompt_for_input("Please enter a description for the image you want to create:")
        if not prompt:
            return

        self.update_status("Generating image, please wait...")
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            for data in response.data:
                image_path = self.download_image(data.url)
                self.show_image(image_path)
        except Exception as e:
            self.update_status("Failed to generate image.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(e)
            return

        self.update_status("Image created successfully")

    def edit_image(self):
        if not self.selected_image:
            messagebox.showinfo("No Image Selected", "Please select an image to edit.")
            return

        image_path = [img[1] for img in self.images if img[0] == self.selected_image][0]
        original_image = Image.open(image_path)
        original_size = original_image.size
        marked_image = self.draw_mask(image_path)
        buffer = io.BytesIO()
        marked_image.save(buffer, format="PNG")
        buffer.seek(0)
        marked_image = buffer

        prompt = self.prompt_for_input("Enter a description of the changes you want to make to the image:")
        if not prompt:
            return

        n = self.get_integer("Number of Edits", "How many edits would you like to generate?", 1, 10)
        if not n:
            return

        self.update_status("Editing image, please wait...")
        try:
            response = client.images.edit(
                model="dall-e-2",
                image=marked_image,
                prompt=prompt,
                n=n,
                size="1024x1024"
            )
            for data in response.data:
                edited_image_path = self.download_image(data.url)

                edited_image = Image.open(edited_image_path)
                edited_image = edited_image.resize(original_size, Image.LANCZOS)
                edited_image.save(edited_image_path)
                self.show_image(edited_image_path)
        except Exception as e:
            self.update_status("Failed to edit image.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(e)
            return

        self.update_status("Image edited successfully")

    def create_variation(self):
        if not self.selected_image:
            messagebox.showinfo("No Image Selected", "Please select an image to create variations.")
            return

        image_path = [img[1] for img in self.images if img[0] == self.selected_image][0]
        original_image = Image.open(image_path)
        original_size = original_image.size

        n = self.get_integer("Number of Variations", "How many variations would you like to generate?", 1, 10)
        if not n:
            return

        self.update_status("Creating variations, please wait...")
        try:
            response = client.images.create_variation(
                model="dall-e-2",
                image=open(image_path, "rb"),
                n=n,
                size="1024x1024"
            )
            for data in response.data:
                variation_image_path = self.download_image(data.url)

                variation_image = Image.open(variation_image_path)
                variation_image = variation_image.resize(original_size, Image.LANCZOS)
                variation_image.save(variation_image_path)
                self.show_image(variation_image_path)
        except Exception as e:
            self.update_status("Failed to create variations.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            print(e)
            return

        self.update_status("Variations created successfully")

    def draw_mask(self, image_path):
        self.update_status("Mark areas that should be modified")

        base_img = Image.open(image_path)
        original_size = base_img.size
        base_img = base_img.resize((512, 512))
        
        checker = Image.new('RGBA', (320, 320), (255, 255, 255, 255))
        d = ImageDraw.Draw(checker)
        for i in range(0, 320, 20):
            for j in range(0, 320, 20):
                if (i // 20 + j // 20) % 2 == 0:
                    d.rectangle([i, j, i+19, j+19], fill=(200, 200, 200, 255))
        checker = checker.resize((512, 512), Image.NEAREST)

        if base_img.mode != 'RGBA':
            base_img = base_img.convert('RGBA')

        mask_canvas = tk.Toplevel(self.root)
        mask_canvas.title("Mark areas that should be modified")
        
        canvas = tk.Canvas(mask_canvas, width=512, height=512)
        canvas.pack(expand=True, fill=tk.BOTH)

        tk_img = ImageTk.PhotoImage(base_img)
        canvas_img = canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

        def update_display():
            nonlocal tk_img
            display = Image.alpha_composite(checker, base_img)
            tk_img = ImageTk.PhotoImage(display)
            canvas.itemconfig(canvas_img, image=tk_img)

        brush_size = tk.IntVar(value=20)
        brush_mode = tk.StringVar(value="erase")
        brush_shape = tk.StringVar(value="circle")

        def start_draw(event):
            canvas.old_x = event.x
            canvas.old_y = event.y

        def draw(event):
            x, y = event.x, event.y
            size = brush_size.get()
            
            img_data = base_img.load()
            
            def modify_alpha(x, y):
                r, g, b, a = img_data[x, y]
                if brush_mode.get() == "erase":
                    img_data[x, y] = (r, g, b, 0)
                else:
                    img_data[x, y] = (r, g, b, 255)

            if brush_shape.get() == "line":
                for i in range(size):
                    x1 = int(canvas.old_x + (x - canvas.old_x) * i / size)
                    y1 = int(canvas.old_y + (y - canvas.old_y) * i / size)
                    for dx in range(-size//2, size//2):
                        for dy in range(-size//2, size//2):
                            if 0 <= x1+dx < 512 and 0 <= y1+dy < 512:
                                modify_alpha(x1+dx, y1+dy)
            elif brush_shape.get() == "circle":
                for dx in range(-size, size):
                    for dy in range(-size, size):
                        if dx*dx + dy*dy <= size*size/4:
                            if 0 <= x+dx < 512 and 0 <= y+dy < 512:
                                modify_alpha(x+dx, y+dy)
            elif brush_shape.get() == "square":
                for dx in range(-size//2, size//2):
                    for dy in range(-size//2, size//2):
                        if 0 <= x+dx < 512 and 0 <= y+dy < 512:
                            modify_alpha(x+dx, y+dy)
            
            canvas.old_x = x
            canvas.old_y = y
            update_display()

        canvas.bind("<Button-1>", start_draw)
        canvas.bind("<B1-Motion>", draw)

        controls_frame = tk.Frame(mask_canvas)
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(controls_frame, text="Brush Size:").pack(side=tk.LEFT)
        tk.Scale(controls_frame, from_=1, to=100, orient=tk.HORIZONTAL, variable=brush_size).pack(side=tk.LEFT)

        tk.Radiobutton(controls_frame, text="Erase (Make area transparent)", variable=brush_mode, value="erase").pack(side=tk.LEFT)
        tk.Radiobutton(controls_frame, text="Restore (Make area opaque)", variable=brush_mode, value="restore").pack(side=tk.LEFT)

        tk.Radiobutton(controls_frame, text="Circle Brush", variable=brush_shape, value="circle").pack(side=tk.LEFT)
        tk.Radiobutton(controls_frame, text="Square Brush", variable=brush_shape, value="square").pack(side=tk.LEFT)
        tk.Radiobutton(controls_frame, text="Line Brush", variable=brush_shape, value="line").pack(side=tk.LEFT)

        def set_full_transparent():
            img_data = base_img.load()
            for x in range(512):
                for y in range(512):
                    r, g, b, _ = img_data[x, y]
                    img_data[x, y] = (r, g, b, 0)
            update_display()

        def set_full_opaque():
            img_data = base_img.load()
            for x in range(512):
                for y in range(512):
                    r, g, b, _ = img_data[x, y]
                    img_data[x, y] = (r, g, b, 255)
            update_display()

        tk.Button(controls_frame, text="Make All Transparent", command=set_full_transparent).pack(side=tk.LEFT)
        tk.Button(controls_frame, text="Make All Opaque", command=set_full_opaque).pack(side=tk.LEFT)

        tk.Button(controls_frame, text="Finish Marking", command=mask_canvas.destroy).pack(side=tk.RIGHT)

        mask_canvas.wait_window(mask_canvas)

        marked_image = base_img.resize(original_size, Image.LANCZOS)
        self.update_status("Image marking completed")
        return marked_image

    def open_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if file_path:
            self.show_image(file_path)

    def save_image(self):
        if not self.selected_image:
            messagebox.showinfo("No Image Selected", "Please select an image to save.")
            return

        image_path = [img[1] for img in self.images if img[0] == self.selected_image][0]
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if save_path:
            Image.open(image_path).save(save_path)
            self.update_status(f"Image saved as {save_path}")

    def remove_image(self):
        if not self.selected_image:
            messagebox.showinfo("No Image Selected", "Please select an image to remove.")
            return

        for frame, path in self.images:
            if frame == self.selected_image:
                frame.grid_forget()
                self.images.remove((frame, path))
                break

        self.selected_image = None
        self.rearrange_images()

    def clear_images(self):
        for frame, _ in self.images:
            frame.grid_forget()
        self.images.clear()
        self.selected_image = None
        self.row = 0
        self.col = 0
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def rearrange_images(self):
        self.row = 0
        self.col = 0
        for frame, _ in self.images:
            frame.grid(row=self.row, column=self.col, padx=5, pady=5)
            self.col += 1
            if self.col >= 3:
                self.col = 0
                self.row += 1
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()
