from kksubs.kksubs import SubtitleController

# demo: add very basic subtitles from a text file.

controller = SubtitleController()
controller.load_input_image_directory("input_image_directory")
controller.load_input_text_directory("input_text_directory")
controller.load_output_directory("output_directory")

controller.add_subtitles()