from kksubs.kksubs import SubtitleController

# demo: add very basic subtitles from a text file.

controller = SubtitleController()
controller.load_input_image_directory("examples/sample-images")
controller.load_input_text_directory("examples/1-basic-usage/input-text-directory")
controller.load_output_directory("examples/1-basic-usage/output-directory")

controller.add_subtitles()