ERROR_DOWNLOAD = "Download FAIL: This version is not avaliable on this repository"
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
