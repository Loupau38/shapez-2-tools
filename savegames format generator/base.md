# Shapez 2 Savegames File Format
**NOT from the devs<br/>
aka Loupau's understanding of savegame files**

Last updated : 1.1.0-rc2

## Stage 1 : File Location

In the 'Play' menu, click the 'Show Folder' button. The folder that opens contains all of your savegames.

<img width="1151" height="512" alt="image" src="https://gist.github.com/user-attachments/assets/3c2cf3b1-ea75-4c95-aad6-eec2e39452da" />

Locate the UID at the top of your savegame in the ingame list.

<img width="800" height="187" alt="image" src="https://gist.github.com/user-attachments/assets/8778b535-b48d-45eb-8d08-3c93981123f0" />

In the folder that opened previously, open the folder whose name is that UID. This contains all backups of your savegame.

## Stage 2 : File format

A savegame backup is a file whose name has the format `backup-v{backup_number}-{timestamp}.spz2`. Note that this file name format is only required when the file is in the savegame's folder, the file can have any name when you use the 'Import' button in the 'Play' menu. `.spz2` files are zip archives, so to open one, you can open it like you would open a `.zip` file.

## Stage 3 : Contained Files Format

The archive contains multiple files and folders. The files are either `.json` or `.bin`.

Quick links :
- [Common to all .bin files](#common-to-all-bin-files)
- [maps/main/buildings/[#].bin](#mapsmainbuildingsbin)
- [maps/main/islands/[#].bin](#mapsmainislandsbin)
- [maps/main/meta](#mapsmainmeta)
- [maps/main/simulation/state.bin](#mapsmainsimulationstatebin)
- [maps/main/cargo.bin](#mapsmaincargobin)
- [maps/main/resource-chunks.bin](#mapsmainresource-chunksbin)
- [maps/main/trains.bin](#mapsmaintrainsbin)
- [local-player.json](#local-playerjson)
- [research.json](#researchjson)
- [savegame.json](#savegamejson)
- [statistics.bin](#statisticsbin)
- [strings.bin](#stringsbin)
- [Contained Objects](#contained-objects)

### Common to all .bin files

The files are padded with null bytes to have a file size which is a power of two. This padding can be ignored and is also not required for the game to load the save.

Due to a language like C# being used, when an object is said to have a specific type, it can be either that specific type or `null`. When the game allows that object to be `null`, the encoding format will reflect that by having special cases for `null` objects. If the format doesn't specify how an object should be encoded if it's `null`, then that object shouldn't be able to be `null` in normal circumstances.

When a type's name begins with `I`, it means the type is a C# interface. An interface doesn't fully represent a data type, but instead is more like a blueprint for other types to inherit from and build upon. This means that when an object's type is an interface, in reality the object will have a type that inherits from that interface. As for the serialization of interfaces, two cases exist:
- either the interface doesn't provide special serialization code, and the actual object's type's serialization code will be called directly
- or the interface does provide serialization code, in that case it will be called, then that code will decide if it calls the actual type's code or not.

The names of data types in this documentation use the same names as the class names in the game's code, except when name changes or simplifications of the data structures help understandability.

The custom C# objects that make up the contents of a savegame are broken down into basic types to be serialized into the `.bin` files. The format of these basic types is described below.

#### Byte

A single byte is simply written as is. It can be used to represent an integer between 0 and 255 or a single ASCII character.

#### Numbers

All numbers are encoded as little endian.

| Type     | Encoded on |
| -------- | ---------- |
| (u)short | 2 bytes    |
| (u)int   | 4 bytes    |
| (u)long  | 8 bytes    |
| float    | 4 bytes    |

#### Bool

Booleans are encoded on a single byte, `0` for `false` and `1` for `true`.

#### String

Strings are encoded using a lookup table. What actually gets written is the string's index in the table as an [int](#numbers). However, if the string is `null`, it isn't added to the table and instead an index of `-2^31` is written. The lookup table is then written to [strings.bin](#stringsbin).<br/>
Exception : if you ended up here from the blueprint codes specifications, since blueprints don't have a lookup table, the string is directly written in the data :

| Type               | Description                               |
| ------------------ | ----------------------------------------- |
| [short](#numbers) | The string's length, or -1 if it's `null` |
| bytes              | The string encoded in UTF-8               |

#### Checkpoint

Checkpoints are markers along the data stream that ensure a reader is still reading the correct data to avoid creating dummy data if a format mismatch happens.<br/>
They are only used if enabled for the savegame, with that info being found in [savegame.json](#savegamejson). If they aren't enabled, nothing is written when a format specifies using a checkpoint.<br/>
They are initially defined with a string ID, that is then hashed using the below algorithm, with `s` the checkpoint ID :

```C#
uint hash = 523423;
for (int i = 0; i < s.Length; i++)
{
    hash += s[i];
    hash += hash << 10;
    hash ^= hash >> 6;
}
hash += hash << 3;
hash ^= hash >> 11;
hash += hash << 15;
return hash;
```

That algorithm produces a [uint](#numbers) that is then written to represent the checkpoint.<br/>
The checkpoints currently used by the game and their hash can be found below for convenience.

| ID                          | hash (`uint`) | hash (`bytes`) |
| --------------------------- | ------------- | -------------- |
| belt-path-state:end         | 4240874953    | `C9 9D C6 FC`  |
| belt-path-state:start       | 1930277995    | `6B B4 0D 73`  |
| blob:end                    | 2225352737    | `21 30 A4 84`  |
| blob:start                  | 3295808852    | `54 0D 72 C4`  |
| building                    | 899714533     | `E5 8D A0 35`  |
| buildings                   | 2756275580    | `7C 6D 49 A4`  |
| fast-belt-path:end          | 3032662934    | `96 C3 C2 B4`  |
| fast-belt-path:start        | 937161514     | `2A F3 DB 37`  |
| island                      | 2971730586    | `9A 02 21 B1`  |
| super-chunk                 | 2789635310    | `EE 74 46 A6`  |
| super-chunk:fluid-resources | 373766737     | `51 3A 47 16`  |
| super-chunk:shape-resources | 166886618     | `DA 7C F2 09`  |
| TrainData                   | 3975112935    | `E7 68 EF EC`  |

#### Blob

Blobs are used to wrap pieces of data. Since they store the length of their content, a reader can easily skip a blob if needed, in case of outdated data for example.

| Type                      | Description                   |
| ------------------------- | ----------------------------- |
| [Checkpoint](#checkpoint) | `blob:start`                  |
| [int](#numbers)          | The content's length in bytes |
| Any                       | The blob's content            |
| [Checkpoint](#checkpoint) | `blob:end`                    |

#### Array

Arrays don't have special formatting, but they are referenced here for completeness.

| Type | Description     |
| ---- | --------------- |
| Any  | Array element 0 |
| Any  | Array element 1 |
| ...  | ...             |
| Any  | Array element n |

### maps/main/buildings/[#].bin

BUILDINGS_BIN_FORMAT

### maps/main/islands/[#].bin

ISLANDS_BIN_FORMAT

### maps/main/meta

When serializing a savegame, the game writes the string `Game.Core.Modding.ResolvedMod[]` to that folder, which doesn't have any effect (because it's a folder) apart from adding it to [strings.bin](#stringsbin). It's also not read on deserialization.

### maps/main/simulation/state.bin

todo

### maps/main/cargo.bin

todo

### maps/main/resource-chunks.bin

todo

### maps/main/trains.bin

TRAINS_BIN_FORMAT

### local-player.json

todo

### research.json

todo

### savegame.json

todo

### statistics.bin

todo

### strings.bin

STRINGS_BIN_FORMAT

### Contained Objects

Below are the formats of objects contained inside the files described above.

CONTAINED_OBJECTS_FORMAT