# Standalone creative skill review

This is the disposition of the 22 private CutAgent Creative Skill concepts for the public standalone skills. Public text is licensed under the repository's AGPL-3.0-only license. It is adapted for local DaVinci Resolve, CutAgent SDK, CutAgent CLI, and user supplied media. It contains no account pairing, subscription, Cloud catalog, hosted transcription, voice generation, or video generation workflow.

| Private concept | Public skill | Local input or adaptation |
| --- | --- | --- |
| apple-motion-graphics | `cutagent-apple-motion-graphics` | Supplied/local artwork; native Fusion construction. |
| b-roll | `cutagent-b-roll` | Supplied/licensed local footage; missing shots are reported. |
| background-music | `cutagent-background-music` | Supplied/licensed local audio; local asset selection reference. |
| beat-editing | `cutagent-beat-editing` | Local music and footage. |
| clipping | `cutagent-clipping` | Local source, optional local transcript. |
| color-grading | `cutagent-color-grading` | Supplied/licensed local color assets. |
| edit-style-learning | `cutagent-edit-style-learning` | Local project or video reference; no remote analysis service. |
| fusion-motion-graphics | `cutagent-fusion-motion-graphics` | Native Fusion and included editable template. |
| graphic-accents | `cutagent-graphic-accents` | Native Fusion shapes and masks. |
| interface-cursor-animation | `cutagent-interface-cursor-animation` | Supplied/local cursor artwork. |
| motion-text | `cutagent-motion-text` | Native Text+ and Fusion. |
| motion-transitions | `cutagent-motion-transitions` | Native Edit/Fusion operations. |
| object-animation | `cutagent-object-animation` | Local object/image sources and native Fusion. |
| opening-hooks | `cutagent-opening-hooks` | Local footage, typography, and licensed sound. |
| podcast | `cutagent-podcast` | Local cameras/mics; optional local transcript. |
| real-estate-reel | `cutagent-real-estate-reel` | Supplied property footage and truthful local metadata. |
| screen-camera-pip-sync | `cutagent-screen-camera-pip-sync` | Local screen, camera, and microphone. |
| sound-design | `cutagent-sound-design` | Supplied/licensed local effects and ambience. |
| speech-cleanup | `cutagent-speech-cleanup` | Local listening/transcript evidence. |
| text-behind-object | `cutagent-text-behind-object` | Native Text+ and local foreground mask. |
| transcript-captions | `cutagent-transcript-captions` | Supplied subtitle/transcript or native local DaVinci Resolve transcription where supported. |
| voice-generation | `cutagent-voiceover` | Synthetic generation removed; directs, selects, and places recorded or user supplied takes. |

The last row is deliberately renamed: the standalone package does not supply a local text-to-speech engine. A skill named `voice-generation` would falsely imply that it does. If a separate local engine is later added, it needs its own capability and acceptance review.
