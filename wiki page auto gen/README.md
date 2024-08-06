This is scripts to automatically generate some pages on the shapez 2 wiki.

The editable templates are all the files in the `formats/` folder. Content inside them use exactly the same format as on wiki pages, with the exception that braces have to be doubled (`{` becomes `{{`, and `}` becomes `}}`). Variable parts that will get filled in by the script are indiacted by words between barces (example: `Task name : {taskName}`).

The `genPages.py` script can be run to generate the pages, the outputs are : `outputBpShapeLists.txt`, `outputBpShapeShapes/`, `outputChangelog.txt`, `outputMilestoneLists.txt`, `outputMilestoneShapes/`, `outputTaskLists.txt` and `outputTaskShapes/`

`shapeViewer.py` and `pygamePIL.py` are taken from [ShapeBot 2](https://github.com/tobspr-games/shapez-2-discord-bot)