from kksubs.kksubs import SubtitleController

# demo: add very basic subtitles from a text file.

controller = SubtitleController()
controller.load_configs("examples/4-configuration/config.yaml")

controller.add_subtitles()