import re


def get_major_version(java_version_name: str):
    version = re.findall(r'\d+', java_version_name)
    return int(version[0])
