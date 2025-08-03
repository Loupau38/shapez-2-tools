These are scripts to automatically generate some pages on the shapez 2 wiki.

Requires [shapez2](https://pypi.org/project/shapez2/).

The editable templates are all the files in the `formats/` folder. Content inside them use exactly the same format as on wiki pages, with the exception that braces have to be doubled (`{` becomes `{{`, and `}` becomes `}}`). Variable parts that will get filled in by the script are indiacted by words between barces (example: `Task name : {taskName}`).

The `genPages.py` script can be run to generate the pages, the outputs are : `outputBpShapeLists.txt`, `outputMilestoneLists.txt`, `outputOLGoalLineLists.txt`, `outputOLRewardLists.txt`, `outputOLShapeBadgeLists.txt` and `outputTaskLists.txt`.