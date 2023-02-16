from kksubs.kksubs import SubtitleController

# demo: add very basic subtitles from a text file.

controller = SubtitleController()
controller.load_input_image_directory("examples/sample-images")
controller.load_input_text_directory("examples/3-subtitle-profiles/input-text-directory")
controller.load_output_directory("examples/3-subtitle-profiles/output-directory")
controller.load_subtitle_profiles("examples/3-subtitle-profiles/subtitle_profiles.yaml")
controller.load_default_subtitle_profile_id("default")

controller.add_subtitles()