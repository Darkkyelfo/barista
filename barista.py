import tarfile
from os import path, mkdir, listdir, getcwd, system as os_system, remove
from platform import system
from shutil import move, rmtree

import boto3
import yaml
from botocore import UNSIGNED
from botocore.client import Config


class Configuration:
    def __init__(self, file="conf.yaml"):
        with open(file) as f:
            conf_yaml = yaml.load(f, Loader=yaml.FullLoader)["conf"]
            self.__path_download = conf_yaml['download_path']
            self.__path_file = conf_yaml['path_file']
        self.__so = system().lower()

    def path_download(self):
        return self.__path_download

    def so_name(self):
        return self.__so

    def path_file(self):
        return self.__path_file


class Barista:

    def __init__(self):
        self._configuration = Configuration()
        self.__s3client = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='us-east-2')
        self.__bucket_name = 'baristajdkrepo'
        if not path.exists(self._configuration.path_download()):
            mkdir(self._configuration.path_download())
        self.__versions = self.get_list_java_versions()

    def download_java_version(self, version, force=False):
        file_to_download = self.__versions[version]
        version_exists = False
        file_name = None
        for file in listdir("./versions"):
            file_name = file.lower()
            if version in file_name:
                version_exists = True
                break
        if not version_exists:
            print(f"DOWNLOADING {version}...")
            self.__s3client.download_file(self.__bucket_name, file_to_download, self.__version_to_file(version))
        elif force:
            print(f"DOWNLOADING {version}...")
            self.__delete_local_version(file_name)
            self.__s3client.download_file(self.__bucket_name, file_to_download, self.__version_to_file(version))
            print(f"DOWNLOAD {version} FINISHED !")

    def __delete_local_version(self, java_targz_name):
        remove(f'./versions/{java_targz_name}')

    def change_java_version(self, version):
        java_folder = "jdk"
        if path.exists(java_folder):
            rmtree(java_folder)
        targz_file_name = self.__version_to_file(version)
        tar = tarfile.open(targz_file_name, "r:gz")
        tar.extractall()
        tar.close()
        folder_name = None
        for file in listdir("./"):
            if "jdk" in file and "versions" not in file:
                folder_name = file
                print(file)
        if folder_name is not None:
            move(folder_name, "jdk")
        print(f"JDK {version} ACTIVATED!!")

    def get_list_java_versions(self):
        versions = {}
        for java in self.__s3client.list_objects(Bucket=self.__bucket_name)["Contents"]:
            java_version = java["Key"]
            if self._configuration.so_name() in java_version and "jdk" in java_version:
                format_version = java_version.replace(f"{self._configuration.so_name()}/", "")\
                    .replace(".tar.gz", "")\
                    .replace("_bin", "")
                versions[format_version] = java_version
        return versions

    def list_java_versions(self):
        versions = list(self.__versions.keys())
        versions.sort()
        return versions

    def __version_to_file(self, version):
        return f"{self._configuration.path_download()}/{version.lower()}"

    def list_installed_java_versions(self):
        pass

    def set_enviroment_var(self):
        if 'windows' in self._configuration.so_name():
            os_system(f'setx /M path "%path%;{getcwd()}"')
        else:
            os_system(f"echo 'export PATH={getcwd()}/jdk/bin:$PATH' >> {self._configuration.path_file()}")


barista = Barista()
versoes = Barista().list_java_versions()
print(versoes)
barista.download_java_version(versoes[0], force=True)
barista.change_java_version(versoes[0])
# barista.set_enviroment_var()
