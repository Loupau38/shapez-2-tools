import os
import json

GAME_VERSION = 1122

BASE_PATH = os.path.expandvars(f"%LOCALAPPDATA%low/tobspr Games/shapez 2/basedata-v{GAME_VERSION}/")
GAME_SCENARIO_PATHS = [
    BASE_PATH + "scenarios/default-scenario.json",
    BASE_PATH + "scenarios/hard-scenario.json",
    BASE_PATH + "scenarios/hexagonal-scenario.json",
    BASE_PATH + "scenarios/insane-scenario.json",
    BASE_PATH + "scenarios/onboarding-scenario.json"
]
TRANSLATIONS_PATH = BASE_PATH + "translations-en-US.json"
# CHANGELOG_PATH = BASE_PATH + "Changelog.json"

EXTRACTED_SCENARIO_PATHS = [
    "./gameFiles/default-scenario.json",
    "./gameFiles/hard-scenario.json",
    "./gameFiles/hexagonal-scenario.json",
    "./gameFiles/insane-scenario.json",
    "./gameFiles/onboarding-scenario.json"
]
EXTRACTED_TRANSLATIONS_PATH = "./gameFiles/translations-en-US.json"
# EXTRACTED_CHANGELOG_PATH = "./gameFiles/Changelog.json"

for gamePath,extractedPath in zip(GAME_SCENARIO_PATHS,EXTRACTED_SCENARIO_PATHS):
    with open(gamePath,encoding="utf-8") as f:
        raw = json.load(f)
    with open(extractedPath,"w",encoding="utf-8") as f:
        json.dump(raw,f,ensure_ascii=False,indent=4)

with open(TRANSLATIONS_PATH,encoding="utf-8") as f:
    raw = json.load(f)
with open(EXTRACTED_TRANSLATIONS_PATH,"w",encoding="utf-8") as f:
    json.dump(raw["Entries"],f,ensure_ascii=False,indent=4)

# with open(CHANGELOG_PATH,encoding="utf-8") as f:
#     raw = json.load(f)
# with open(EXTRACTED_CHANGELOG_PATH,"w",encoding="utf-8") as f:
#     json.dump(raw,f,ensure_ascii=False,indent=4)