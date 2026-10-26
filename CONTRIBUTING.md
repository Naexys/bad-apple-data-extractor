# NO AI MUST BE USED
- No AI-made PRs.
- No AI generated or partially generated code.
- Please avoid asking an AI for help, you can find everything you want on the internet. (This last point is more of a suggestion but please at least try :P )

## The current project structure :

### File structure :
| - [input/](./input/)\
| -- | - [README.md](./input/README.md)\
| - [output/](./output/)\
| --| - [README.md](./output/README.md)\
| - [pictures/](./pictures/)\
| --| - [demo_bin.png](./pictures/demo_bin.png)\
| --| - [demo_char_inverted.png](./pictures/demo_char_inverted.png)\
| --| - [demo_char.png](./pictures/demo_char.png)\
| --| - [progress_gui.png](./pictures/progress_gui.png)\
| --| - [settings_gui.png](./pictures/settings_gui.png)\
| - [src/](./src/)\
| --| - [demo.py](./src/demo.py)\
| --| - [diskspace.py](./src/diskspace.py)\
| --| - [extractor.py](./src/extractor.py)\
| --| - [main.py](./src/main.py)\
| --| - [.gitattributes](./.gitattributes)\
| --| - [.gitignore](./.gitignore)\
| - [CONTRIBUTING.md](./CONTRIBUTING.md)\
| - [LICENSE](./LICENSE)\
| - [README.md](./README.md)\
| - [bad-apple-data-extractor.py](./bad-apple-data-extractor.py)\
| - [requirements.txt](./requirements.txt)

### Branch structure :
- **main** > production, the latest stable update
- **dev** > the latest partially stable update
- **dev-feat-[feature name]** > unstable feature developpement
- **dev-feat-[feature name]-[component name]** > unstable feature component developpement

### Notes :
For now any PR needs my approval but if someone makes one, I might change the rules to allow contributors to approve PRs