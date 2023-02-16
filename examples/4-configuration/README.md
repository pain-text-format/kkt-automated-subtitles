# Using Configurations

Instead of loading everything manually into the controller, you can use a `yaml` file to do it.
```
# config.yaml
input_text_directory: input_text_directory
input_image_directory: input_image_directory
output_directory: output_directory
subtitle_profile_path: path_to_subtitle_profiles
```
Then you can just run this code.
```
from kksubs.kksubs import SubtitleController

controller = SubtitleController()
controller.load_configs(path_to_config)

controller.add_subtitles()
```
See the examples section for concrete examples of the above.

*Note: the output of this module is the same as that of `3-subtitle-profiles`.