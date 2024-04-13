Input method 1 :
- Execute either the `.py` or `.exe` file
- In the console, input either a blueprint code, a path to a blueprint file, or a path to a folder containing blueprint files

Input method 2 :

- Execute the `.py` or `.exe` file but with an additional command line argument being a blueprint code, file or folder

Output format :

- In case a blueprint code is given, it will print the fixed blueprint code in the console
- In case a blueprint file is given, a copy of the file will be created for the fixed version (with the name being `name.extension` -> `name.fixed.extension`)
- In case a folder is given, a copy of the folder will be created (with the name being `folderName` -> `folderName.fixed`), it will also recursively execute in sub-folders

When a blueprint gets processed :

- Island IDs get updated
- Purple is changed to magenta in shape producers, fluid producers and constant signals
- Item producers are reset to `CuCuCuCu` and constant generators are reset to `null` if they contain a shape or fluid crate