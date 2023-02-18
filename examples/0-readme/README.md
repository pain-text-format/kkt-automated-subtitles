# Basic Usage
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
content: This is some text in the first image.

image_id: 2.png
content: This is some text in the second image.
This is the second line in the second image.

image_id: 3.png
content: This is some text in the third image.
```
Run the following script:
```
from kksubs.kksubs import SubtitleController

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

## Multiple Text Files

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