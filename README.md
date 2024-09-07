# DALL-E Image Editor
This repository contains a Python application named `dalle_image_editor` which acts as an AI Image Generator and Editor using OpenAI's DALL-E models. The application is built using the `Tkinter` library for the GUI and uses various other libraries for handling images and API requests.

> **Note**: The README file is completely AI-generated, while the Python script is written with the help of AI tools.

## Features
- **Generate New Image**: Create a new image based on a textual description using OpenAI's DALL-E model.
- **Edit Selected Image**: Edit an existing image by marking areas that should be modified and providing a new description.
- **Create Variation of Selected Image**: Generate variations of an existing image.
- **Open Image File**: Open and display an image file from your local system.
- **Save Selected Image**: Save the currently selected image to your local system.
- **Remove Selected Image**: Remove the currently selected image from the display.
- **Clear All Images**: Clear all displayed images.

## Requirements
- Python 3.x
- `tkinter`
- `PIL`
- `requests`
- `easygui`
- `openai`

To install the required packages, run:
```bash
pip install tk pillow requests easygui openai
```

## Usage
1. **Run the Application**:
   ```bash
   python dalle_image_editor.py
   ```

2. **Generate New Image**:
   - Click on the `Generate New Image` button.
   - Enter a description for the image in the prompt dialog.
   - Wait for the image to be generated and displayed.

3. **Edit Selected Image**:
   - Click on any image to select it.
   - Click on the `Edit Selected Image` button.
   - A new window will open to mark the areas to be modified.
     - Use the brush tools to mark the areas.
     - Choose between `Erase`, `Restore`, `Circle Brush`, `Square Brush`, and `Line Brush`.
     - Click `Finish Marking` when done.
   - Enter a description of the changes you want to make in the prompt dialog.
   - Wait for the edited image to be generated and displayed.

4. **Create Variation of Selected Image**:
   - Click on any image to select it.
   - Click on the `Create Variation of Selected` button.
   - Enter the number of variations to generate in the dialog.
   - Wait for the variations to be generated and displayed.

5. **Open Image File**:
   - Click on the `Open Image File` button.
   - Select an image file from your local system.
   - The image will be displayed in the application.

6. **Save Selected Image**:
   - Click on any image to select it.
   - Click on the `Save Selected Image` button.
   - Select the location to save the image in the file save dialog.
   - The selected image will be saved to the specified location.

7. **Remove Selected Image**:
   - Click on any image to select it.
   - Click on the `Remove Selected Image` button.
   - The selected image will be removed from the display.

8. **Clear All Images**:
   - Click on the `Clear All Images` button.
   - All images will be removed from the display.

## Notes
- Ensure that you have a functional OpenAI API key and replace `"sk-xxx"` with your actual API key in the script.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgments
This project was created with the help of AI tools like OpenAI's GPT-4. Special thanks to the developers of `tkinter`, `PIL`, `requests`, `easygui`, and `openai` for their amazing libraries.

## Disclaimer
Please note that the generation and editing of images are done using OpenAI’s models, and their usage is subject to OpenAI’s terms and conditions.

---

Enjoy creating and editing your images with `dalle_image_editor`! If you encounter any issues or have any suggestions, feel free to open an issue on the GitHub repository.
