This is scripts to automatically generate some pages on the shapez 2 wiki.

The editable templates are all the files in the `formats/` folder. Content inside them use exactly the same format as on wiki pages, with the exception that braces have to be doubled (`{` becomes `{{`, and `}` becomes `}}`). Variable parts that will get filled in by the script are indiacted by words between barces (example: `Task name : {taskName}`).

The scripts that can be run to generate the pages are:
- `genScenarios.py`, output: `taskListsOutput.txt`, `taskShapesOutput/`, `milestoneListsOutput.txt` and `milestoneShapesOutput/`

`shapeViewer.py` and `pygamePIL.py` are taken from [ShapeBot 2](https://github.com/tobspr-games/shapez-2-discord-bot)