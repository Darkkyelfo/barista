ERROR_SET_ENV_VAR = "Error setting environment variable. Try running this command as an administrator!"
ERROR_FILE_NOT_FOUND_LOCAL_JAVA = """The version you want install is not avaliable in local repository, please make 
the download before or use the tag -f
barista java use <version> -f
"""


class AWSRepositoryNotFoundException(Exception):
    def __init__(self):
        super(AWSRepositoryNotFoundException, self).__init__(
            "Error:Bucket not found or with invalid name. "
            "If you want to use aws as repository inform the correct name of bucket")


class MavenVersionNotFoundException(Exception):
    def __init__(self, version):
        super(MavenVersionNotFoundException, self).__init__(f"The Maven {version} not exists in current repository!")


class JavaVersionNotFoundException(Exception):
    def __init__(self, version):
        super(JavaVersionNotFoundException, self).__init__(f"The Java: {version} not exists in current repository!")
