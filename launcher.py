"""LunarClient Launcher"""
import os
import zipfile

import downloader.info


class MinecraftArgs(object):
    def __init__(self, game_dir: str, textures_dir: str, width: int, height: int, server: str = None):
        """Minecraft game args
        :param game_dir etc. Saves
        :param textures_dir Lunar textures Dir
        :param width Game Window width
        :param height Game Window height
        :param server join server when launched
        """
        object.__init__(self)
        self.game_dir = game_dir
        self.textures_dir = textures_dir
        self.width = width
        self.height = height
        self.server = server


class JavaAgent(object):
    def __init__(self):
        object.__init__(self)


def get_main_class(version: str = None, branch: str = None, module: str = None) -> str:
    """Get the mainClass of LunarClient"""
    if all([version, branch, module]):
        return downloader.info.get_version(version, branch, module)["launchTypeData"]["mainClass"]
    return "com.moonsworth.lunar.genesis.Genesis"


def get_ichor_state(version: str, branch: str, module: str) -> bool:
    """Get ichor (Lunar addon loader) state"""
    return downloader.info.get_version(version, branch, module)["launchTypeData"]["ichor"]


def get_default_jvm_args(version: str, branch: str, module: str, base_dir: str) -> list:
    out = []
    arg: str
    for arg in downloader.info.get_version(version, branch, module)["jre"]["extraArguments"]:
        if arg == "-Djna.boot.library.path=natives":
            # Natives
            out.append("-Djna.boot.library.path=" + os.path.join(base_dir, "natives"))
            out.append("-Djava.library.path=" + os.path.join(base_dir, "natives"))
            continue
        out.append(arg)
    return out


def get_args(version: str, branch: str, module: str, base_dir: str, mc_args: MinecraftArgs, java_exec: str,
             jvm_args: list, game_args: list, agents: list[JavaAgent], setup_natives: bool):
    args = [java_exec]
    jvm_args += get_default_jvm_args(version, branch, module, base_dir)
    args += jvm_args
    for agent in agents:
        args.append(agent.get_vm_arg())
    # Class path
    classpath = []
    ichor = []
    natives_file: str = ""
    for artifact in downloader.info.get_version(version, branch, module)["launchTypeData"]["artifacts"]:
        if artifact["type"] == "CLASS_PATH":
            # Class path
            classpath.append(artifact["name"])
        elif artifact["type"] == "EXTERNAL_FILE":
            # ICHOR File
            ichor.append(artifact["name"])
        elif artifact["type"] == "NATIVES":
            # Natives
            natives_file = artifact["name"]
    # Add classPath
    args.append("-cp")
    args.append(";".join(classpath))
    # Main class
    args.append(get_main_class(version, branch, module))

    if setup_natives:
        # Unzip natives
        with zipfile.ZipFile(os.path.join(base_dir, natives_file)) as natives_zip:
            natives_zip.extractall(base_dir)
    # LunarClient args
    args.append("--version " + version)
    args.append("--accessToken 0")
    args.append("--userProperties {}")
    args.append("--hwid PUBLIC-HWID")
    args.append("--installationId INSTALL-ID")
    args.append("--workingDirectory " + base_dir)
    args.append("--classpathDir " + base_dir)
    args.append("--width " + str(mc_args.width))
    args.append("--height " + str(mc_args.height))
    args.append("--gameDir " + mc_args.game_dir)
    args.append("--texturesDir " + mc_args.textures_dir)
    if mc_args.server is not None:
        args.append("--server " + mc_args.server)
    args.append("--assetIndex " + ".".join(version.split(".")[0:1]))
    if get_ichor_state(version, branch, module):
        # Add ichor args
        args.append("--ichorClassPath " + ",".join(classpath))  # Lunar classpath
        args.append("--ichorExternalFiles " + ",".join(ichor))  # Lunar ichor files
    return args
