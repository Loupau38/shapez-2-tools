These are scripts to automatically generate some pages on the shapez 2 wiki.

The editable templates are all the files in the `formats/` folder. Content inside them use exactly the same format as on wiki pages, with the exception that braces have to be doubled (`{` becomes `{{`, and `}` becomes `}}`). Variable parts that will get filled in by the script are indiacted by words between barces (example: `Task name : {taskName}`).

The `genPages.py` script can be run to generate the pages, the outputs are : `outputBpShapeLists.txt`, `outputChangelog.txt`, `outputMilestoneLists.txt`, `outputOLGoalLineLists.txt`, `outputOLRewardLists.txt`, `outputOLShapeBadgeLists.txt` and `outputTaskLists.txt`.