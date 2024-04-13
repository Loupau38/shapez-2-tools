GAME_VERSIONS = {
    1005 : ["a1","a2","a3"],
    1008 : ["a4"],
    1009 : ["a5"],
    1013 : ["a6"],
    1015 : ["a6.1","a6.2"],
    1018 : ["a7"],
    1019 : ["a7.1","a7.2","a7.3"],
    1022 : ["a7.4"],
    1024 : ["a8"],
    1027 : ["a9","a10","a10.1","a10.2"],
    1029 : ["a11"],
    1030 : ["a12d","a12"],
    1031 : ["a13d","a13","a13.5d","a13.6d","a13.7d","a14d","a14.1d"],
    1032 : ["a14.2d","a14.3d","a15d","a15.1d","a15.2d","a15.3d"],
    1033 : ["a15.2","a15.3d"],
    1036 : ["a16"],
    1038 : ["a16","a16.1"],
    1040 : ["a17"]
}
LATEST_GAME_VERSION = 1040
LATEST_PUBLIC_GAME_VERSION = 1033
LATEST_MAJOR_VERSION = 1

BP_VERSION_REACTION_A = "\U0001f1e6"
BP_VERSION_REACTION_D = "\U0001f1e9"
BP_VERSION_REACTION_DOT = "\u23fa"
BP_VERSION_REACTION_UNITS = {str(i) : f"{i}\ufe0f\u20e3" for i in range(10)}
BP_VERSION_REACTION_TENS = {str(i) : v for i,v in enumerate([
    1159909533074866286,1159909535872471162,1159909537944457226,
    1159909542193270824,1159909546735702108,1159909549323587757,
    1159909551697576056,1159909554532913203,1159909556336468008,
    1159909559066964110
])}
BP_VERSION_REACTION_TENTHS = {str(i) : v for i,v in enumerate([
    1159909769876877352,1159909772133400707,1159909773643358228,
    1159909775526592512,1159909784305283133,1159909786956087326,
    1159909788130476124,1159909789741105282,1159909792106676405,
    1159909793578877028
])}

def versionNumToText(version:int,returnAll:bool=False) -> None|str|list[str]:

    versionTexts = GAME_VERSIONS.get(version)

    if versionTexts is None:
        return None

    if not returnAll:
        versionTexts = [versionTexts[-1]]

    outputs = []
    for versionText in versionTexts:
        output = ""

        if versionText[0] == "a":
            output += "Alpha "
            versionText = versionText[1:]

            if versionText[-1] == "d":
                output += versionText[:-1] + " demo"
            else:
                output += versionText

        outputs.append(output)

    if returnAll:
        return outputs

    return outputs[0]

def versionNumToReactions(version:int) -> None|list[str|int]:

    versionTexts = GAME_VERSIONS.get(version)

    if versionTexts is None:
        return None

    versionText = versionTexts[-1]

    if versionText[0] == "a":
        output = [BP_VERSION_REACTION_A]
        versionText = versionText[1:]

        suffix = None
        if versionText[-1] == "d":
            suffix = BP_VERSION_REACTION_D
            versionText = versionText[:-1]

        split = versionText.split(".")

        if len(split[0]) > 1:
            output.append(BP_VERSION_REACTION_TENS[split[0][0]])
        output.append(BP_VERSION_REACTION_UNITS[split[0][-1]])

        if len(split) > 1:
            output.append(BP_VERSION_REACTION_DOT)
            output.append(BP_VERSION_REACTION_TENTHS[split[1]])

        if suffix is not None:
            output.append(suffix)

    return output