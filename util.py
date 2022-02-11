import re

from exceptions import ERROR_SET_ENV_VAR


def get_major_version(java_version_name: str):
    version = re.findall(r'\d+', java_version_name)
    return int(version[0])


def mapp_version(versions_dict, holder):
    versions_dict[holder.version] = holder.link
    major_version = get_major_version(holder.version)
    if versions_dict.get(major_version) is None:
        versions_dict[major_version] = holder.version


def set_enviroment_var(barista):
    try:
        barista.set_enviroment_var()
        print("CONFIGURATION REALIZED !")
    except:
        print(ERROR_SET_ENV_VAR)
