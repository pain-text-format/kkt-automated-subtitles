# Koikatsu Automated Subtitles
This small Python program is developed to provide some automation for the subtitling of Koikatsu stories: a sequence of KK renders that tell a story. 

It is meant to allow the user to experiment with dialogue options quickly, while providing *very* basic subtitling capabilities. It does **not** cover other use cases, such as adding text freely on the screen, adding creative effects, and so on.

The user is recommended to apply other creative tools with this as a final pre-processing step for better results. For a demonstration of features, see the `examples` folder.

## Installation
Create a virtual environment and install the requirements listed in `requirements.txt`. `pip` or `pip3` is recommended:
```
pip install -r requirements.txt
```

## Usage
Concrete examples are demonstrated in the `examples` folder.

### Basic Usage
Have images you want to add subtitles to prepared in some `input_image_directory`.
```
- input_image_directory
    - 1.png
    - 2.png
    - 3.png
```
The text you want to add to the images can be prepared in some `input_text_directory/input-text.txt`.
```
# input_text_directory/input-text.txt
image_id: 1.png
This is some text in the first image.

image_id: 2.png
This is some text in the second image.
This is the second line in the second image.

image_id: 3.png
This is some text in the third image.
```
Run the following script:
```
from controller import SubtitleController

controller = SubtitleController()
controller.load_input_text_directory(input_text_directory)
controller.load_input_image_directory(input_image_directory)
controller.load_output_directory(output_directory)

controller.add_subtitles()
```
From the `output_directory`, you will see subtitles in their corresponding image. This will be the output directory structure.
```
- output_directory
    - input-text
        - 1_caption.png
        - 2_caption.png
        - 3_caption.png
```
Note that subtitles for consecutive images are delimited by a new line before the next subtitle.

### Multiple Text Files
You can add multiple text input files.
```
- input_text_directory
    - input_text1.txt
    - input_text2.txt
    - input_text3.txt
```
When run, the program will add subtitles for each text file. This is useful for keeping and experimenting with multiple versions.
```
- output_directory
    - input_text1
        - 1_caption.png
        - 2_caption.png
        - 3_caption.png
    - input_text2
        ...
    - input_text3
        ...
```

### Subtitle Profiles
To customize a subtitle, we can use "subtitle profiles". Create a file called `subtitle_profiles.json` and add the following:
```
[
    # red font color profile
    # outlined text profile
    # text with aura profile
]
```
Then edit the `input-text.txt` like so:
```
# input_text_directory/input-text.txt
image_id: 1.png
subtitle_profile_id: red_font_color
This is some text in the first image.

image_id: 2.png
subtitle_profile_id: outlined_text
This is some text in the second image.

image_id: 3.png
subtitle_profile_id: text_with_aura
This is some text in the third image.
```

Run the following script, loading the subtitle profiles file into the controller:
```
from controller import SubtitleController

controller = SubtitleController()
controller.load_input_text_directory(input_text_directory)
controller.load_input_image_directory(input_image_directory)
controller.load_output_directory(output_directory)
controller.load_subtitle_profiles(path_to_subtitle_profiles)

controller.add_subtitles()
```
From the `output_directory`, you will see that the subtitles styled.

You can use subtitle profiles to add multiple subtitles on an image, and override subtitle properties for specific subtitles:
```
image_id: 1.png
subtitle_profile_id: speaker
This is the name of the speaker.
subtitle_profile_id: content
fontdata.color: [255, 100, 100]
fontdata.size: 12
This is the content spoken by the speaker.

image_id: 2.png
...
```

### Using Configurations
Instead of loading everything manually into the controller, you can use a `json` file to do it.
```
# config.json
{
    "input_text": input_text_directory,
    "input_image": input_image_directory,
    "output": output_directory,
    "subtitle_profiles": path_to_subtitle_profiles
}
```
Then you can just run this code.
```
from controller import SubtitleController

controller = SubtitleController()
controller.load_configs(path_to_config)

controller.add_subtitles()
```
See the examples section for concrete examples of the above.