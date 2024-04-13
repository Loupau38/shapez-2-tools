# bot itself
TOKEN_PATH = "./token.txt"
BOT_ID = 1131514655404199936

# owner only features
OWNER_USERS = [579288989505421349]
GLOBAL_LOG_CHANNEL = 1132693034673389659
RESTRICT_TO_GUILDS = None # 'None' alone : enable everywhere, 'None' in the list : enable in DMs

# guild settings
GUILD_SETTINGS_PATH = "./guildSettings.json"
MAX_ROLES_PER_LIST = 10

# texts
NO_PERMISSION_TEXT = "You don't have permission to do this or you are in cooldown"
UNKNOWN_ERROR_TEXT = "Unknown error happened"
MESSAGE_TOO_LONG_TEXT = "Message too long"
OWNER_ONLY_BADGE = "[Owner only]"
ADMIN_ONLY_BADGE = "[Admin only]"
SLASH_CMD_BP_PARAM_DESC = "The full blueprint code"
SLASH_CMD_BP_FILE_PARAM_DESC = "A file containing the blueprint code"

# shape viewer
INITIAL_SHAPE_SIZE = 500
SHAPE_COLORS = ["u","r","g","b","c","p","y","w","k"]
SHAPE_LAYER_SEPARATOR = ":"
SHAPE_NOTHING_CHAR = "-"
SHAPE_CHAR_REPLACEMENT = {
    "m" : "p" # change magenta to purple
}

# display parameters
SHAPES_PER_ROW = 8
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 100
DEFAULT_SHAPE_SIZE = 56
SHAPE_3D_VIEWER_LINK_START = "https://shapez.soren.codes/shape?identifier="

# game infos
GI_RESEARCH_PATH = "./gameInfos/research.json"
GI_BUILDINGS_PATH = "./gameInfos/buildings.json"
GI_ISLANDS_PATH = "./gameInfos/islands.json"

# antispam
ANTISPAM_MSG_COUNT_TRESHOLD = 4
ANTISPAM_TIMEOUT_SECONDS = 3600

# other

MESSAGE_MAX_LENGTH = 2000
NO_GUILD_USAGE_COOLDOWN_SECONDS = 5

INVALID_SHAPE_CODE_REACTION = "\u2753"
BOT_MENTIONED_REACTION = "\U0001F916"

FILE_TOO_BIG_PATH = "./fileTooBig.png"
MSG_COMMAND_MESSAGES_PATH = "./messages.json"

BLUEPRINT_3D_VIEWER_LINK_START = "https://shapez.soren.codes/blueprint/view?identifier="
LINK_CHAR_REPLACEMENT = {
    ":" : "%3A",
    "/" : "%2F",
    "+" : "%2B",
    "=" : "%3D",
    "$" : "%24"
}