from kksubs.kksubs import SubtitleController

# demo: add very basic subtitles from a text file.

controller = SubtitleController()
controller.load_input_image_directory("sample-images")
controller.load_input_text_directory("basic-usage/input-text-directory")
controller.load_output_directory("basic-usage/output-directory")

# controller.load_subtitle_profiles("basic-usage/subtitle_profiles.yaml")
# controller.load_default_subtitle_profile_id("default")

controller.add_subtitles()