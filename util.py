def get_major_version(java_version_name):
    return int(java_version_name[:2].replace(".", "").strip())
