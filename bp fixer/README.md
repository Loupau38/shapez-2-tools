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

- If its version is less than 1024 (alpha 8) :
  - T mergers will be rotated 90° CCW

- If its version is less than 1040 (alpha 17) :
  - The shape miner platform ID gets updated

- If its version is less than 1045 (alpha 18) :
  - Platform IDs get updated
  - Purple is changed to magenta in shape, fluid and signal producers
  - Item and signal producers are reset to `CuCuCuCu` if they contain a shape or fluid crate

- If its version is less than 1057 (alpha 20) :
  - Item, fluid and signal producers get updated to the new format
  - The color black gets replaced with uncolored in the above three buildings

- If its version is less than 1064 (alpha 21) :
  - Mirrorable building IDs get updated

- If its version is less than 1067 (alpha 22.2) :
  - Fluid catapult IDs get updated
  - Old space pipe specific fluid catapults get removed
  - Space belts, pipes and rails get updated to the new format

- If its version is less than 1071 (alpha 22.3) :
  - The `"$type"` key gets set to `"Building"` if it doesn't have a value
  - Platforms that don't have additional data get given the default value

- If its version is less than 1082 (alpha 23) :
  - Icon IDs get updated
  - Global wire receivers get updated to the new format
  - Painters and crystal generators get moved one tile to account for their layout change

- If its version is less than 1091 (0.0.2) :
  - The additional data of train locomotives gets removed