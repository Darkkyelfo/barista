from shutil import move, rmtree
from platform import system
from botocore import UNSIGNED
from botocore.client import Config
from os import path, mkdir, listdir

import yaml, boto3
import tarfile



class Configuration:
    def __init__(self,file = "conf.yaml"):
        with open(file) as f:
            self.__path_download = yaml.load(f, Loader=yaml.FullLoader)["conf"]['download_path']
            print(self.__path_download)
        self.__so = system().lower()

    def path_download(self):
        return self.__path_download

    def so_name(self):
        return self.__so



class Barista:

    def __init__(self):
        self._configuration = Configuration()
        self.__s3client = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='us-east-2')
        self.__bucket_name = 'baristajdkrepo'
        if not path.exists(self._configuration.path_download()):
            mkdir(self._configuration.path_download())
        self.__versions = self.get_list_java_versions()

        # objects = s3client.list_objects(Bucket='baristajdkrepo')
        # print(objects)
        # s3client.download_file('baristajdkrepo', 'linux/jdk-11.0.12_linux-x64_bin.tar.gz', 'jdk-11.0.12_linux-x64_bin.tar.gz')


    def download_java_version(self, version):
        self.__s3client.download_file(self.__bucket_name, version, self.__version_to_file(version))

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


    def get_list_java_versions(self):
        versions = []
        for java in self.__s3client.list_objects(Bucket=self.__bucket_name)["Contents"]:
            java_version = java["Key"]
            if self._configuration.so_name() in java_version and "jdk" in java_version:
                versions.append(java_version)
        return versions

    def list_java_versions(self):
        return self.__versions

    def __version_to_file(self, version):
        so_name_with_slash = self._configuration.so_name()+"/"
        return f"{self._configuration.path_download()}/{version.lower().split(so_name_with_slash)[1]}"


    def list_installed_java_versions(self):
        pass


barista = Barista()
versoes = Barista().list_java_versions()
print(versoes)
# barista.download_java_version(versoes[2])
barista.change_java_version(versoes[1])
