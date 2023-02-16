# Subtitle Profiles
To customize subtitles more globally, we can use "subtitle profiles". Then, instead of adding details in your subtitle input file, like
```
image_id: 1.png
(subtitle details)
content: stuff to write
```
you can use subtitle profile IDs to represent the details, by putting the details in a file like `subtitle_profiles.yaml`,
```
# subtitle_profiles.yaml
- subtitle_profile_id: special profile
    (subtitle details)
```
and write
```
image_id: 1.png
subtitle_profile_id: special profile
content: stuff to write
```

Additionally, you can use the default subtitle profile feature to avoid having to write `subtitle_profile_id:` for each subtitle.
```
...
controller.load_default_subtitle_profile_id("special profile")
```

Some knowledge of JSON/YAML is required, though you can refer to the examples.