Usage :

- Execute either the `.py` or `.exe` file and input the blueprint in the console
- Or execute the file but with an additional command line argument being the blueprint
- Or execute the file but input the blueprint in stdin

In all of those methods, a blueprint can be either a blueprint code, a path to a blueprint file, or a path to a folder containing blueprint files


Output format :

- In case a blueprint code is given, it will print the fixed blueprint code in the console (if stdin is used, it will instead output it to stdout with no additional formatting)
- In case a blueprint file is given, a copy of the file will be created for the fixed version (with the name being `name.extension` -> `name.fixed.extension`) (if stdin is used, it will output the fixed file path to stdout)
- In case a folder is given, a copy of the folder will be created (with the name being `folderName` -> `folderName.fixed`), it will also recursively execute in sub-folders (if stdin is used, it will output the fixed folder path to stdout)

When a blueprint gets processed :

- Island IDs get updated
- Purple is changed to magenta in shape producers, fluid producers and constant signals
- Item producers are reset to `CuCuCuCu` and constant generators are reset to `null` if they contain a shape or fluid crate