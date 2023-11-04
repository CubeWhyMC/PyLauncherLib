import requests
import json

API = "https://api.lunarclientprod.com/launcher/launch"
METADATA_API = "https://api.lunarclientprod.com/launcher/metadata?launcher_version=2.15.1"


def get_metadata() -> dict:
    """Get metadata json"""
    r = requests.get(METADATA_API)
    return r.json()


def get_version(version: str, branch: str, module: str) -> dict:
    """Get a version's json"""
    data = {
        "hwid": "PRIVATE",
        "hwid-private": "PRIVATE-HWID",
        "installion_id": "INSTALLED",
        "os": "win32",
        "arch": "x64",
        "os_release": "19045.3086",
        "launcher_version": "2.15.2",
        "launch_type": "lunar",
        "version": version,
        "branch": branch,
        "module": module
    }
    r = requests.post(API, data=json.dumps(data), headers={"Content-Type": "application/json"})
    return r.json()


def get_support_version() -> list:
    """Get support patches of LunarClient"""
    metadata = get_metadata()
    versions = []
    versions_in_json = metadata["versions"]
    version: dict
    for version in versions_in_json:
        for sub in version["subversions"]:
            versions.append(sub["id"])
    return versions


def get_subversion(version: str) -> None | dict:
    """Get the info of the version"""
    for version1 in get_metadata()["versions"]:
        if version1["id"] in version:
            for sub in version1["subversions"]:
                if sub["id"] == version:
                    return sub
    return None


def get_support_modules(version: str) -> list:
    """Get support modules for a special version"""
    version1 = get_subversion(version)
    modules = []
    for module in version1["modules"]:
        modules.append(module["id"])
    return modules


def get_lunar_artifacts(version: str, branch: str, module: str) -> dict:
    """Get artifacts info of the special version"""
    version_json = get_version(version, branch, module)
    artifacts: list = version_json["launchTypeData"]["artifacts"]
    out: dict = {}
    artifact: dict
    for artifact in artifacts:
        out[artifact["name"]] = artifact["url"]
    return out


def get_lunar_textures_baseurl(version: str = None, branch: str = None, module: str = None) -> str:
    """Get the baseUrl of textures' index
    :param version: Minecraft version
    :param branch: Branch of LunarClient
    :param module: Enabled module
    """
    if not all([version, branch, module]):
        return "https://textures.lunarclientcdn.com/file/"
    return get_version(version, branch, module)["baseUrl"]

