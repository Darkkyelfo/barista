import tarfile
import zipfile
from os import path, mkdir, listdir, system as os_system, remove
from platform import system
from shutil import move, rmtree
from urllib import request

import boto3
import yaml
from botocore import UNSIGNED
from botocore.client import Config
from bs4 import BeautifulSoup

from util import get_major_version


class LinkHolderOpenJDK:
    def __init__(self, version, operation_system, architecture, link):
        self.so = operation_system.lower()
        self.architecture = architecture
        self.version = version
        self.link = link

    def __str__(self):
        return f"{self.version} {self.so} {self.architecture}"


class OpenJDKExtractor:

    def __init__(self):
        self.__open_jdk_archive = "https://jdk.java.net/archive/"
        self.__holder = []
        self.__get_link()

    def __get_link(self):
        request_conn = request.urlopen(self.__open_jdk_archive)
        html_bytes = request_conn.read()
        html_page = html_bytes.decode("utf8")
        request_conn.close()

        soup = BeautifulSoup(html_page, features="html.parser")
        current_version = None
        for i in soup.find_all("tr"):
            test = i.find_all("th")
            if len(test) == 0:
                continue
            if len(test) == 1:
                current_version = test[0].text
                continue
            self.__holder.append(LinkHolderOpenJDK(current_version, test[0].text, test[1].text, i.a['href']))

    def get_links_linux(self):
        return [holder for holder in self.__holder if "linux" in holder.so]

    def get_links_windows(self):
        return [holder for holder in self.__holder if "windows" in holder.so]


class Configuration:
    def __init__(self, file="conf.yaml"):
        with open(file) as f:
            conf_yaml = yaml.load(f, Loader=yaml.FullLoader)["conf"]
            self.__path_download = conf_yaml['download_path']
            self.__path_file = conf_yaml['path_file']
            self.__jdk_path = conf_yaml['jdk_path']
            self.__repository = conf_yaml['repository']
            self.__bucket = conf_yaml['bucket']
        self.__so = system().lower()

    def path_download(self):
        return self.__path_download

    def so_name(self):
        return self.__so

    def path_file(self):
        return self.__path_file

    def repository(self):
        return self.__repository

    def bucket(self):
        return self.__bucket

    def jdk_path(self):
        return self.__jdk_path


class Barista:
    version = "0.1.0"

    def __init__(self, conf_file="conf.yaml"):
        self._configuration = Configuration(file=conf_file)
        if 'aws' in self._configuration.repository():
            self.__s3client = boto3.client('s3', config=Config(signature_version=UNSIGNED), region_name='us-east-2')
        if not path.exists(self._configuration.path_download()):
            mkdir(self._configuration.path_download())
        self.__versions = self.get_list_java_versions()

    def download_java_version(self, version, force=False):
        file_to_download = self.__versions[version]
        version_exists = False
        file_name = None
        for file in self.list_installed_java_versions():
            file_name = file.lower()
            if version.lower() in file_name:
                version_exists = True
                break
        if not version_exists:
            print(f"DOWNLOADING {version}...")
            self.__download_java_file(version, file_to_download)
            print(f"DOWNLOAD {version} FINISHED !")
        elif force:
            print(f"DOWNLOADING {version}...")
            self.__delete_local_version(file_name)
            self.__download_java_file(version, file_to_download)
            print(f"DOWNLOAD {version} FINISHED !")

    def change_java_version(self, version):
        java_folder = f"{self._configuration.jdk_path()}/jdk"
        if path.exists(java_folder):
            rmtree(java_folder)
        targz_file_name = self.__version_to_file(version)
        self.__extract_file(targz_file_name)
        folder_name = None
        for file in listdir(self._configuration.jdk_path()):
            if "jdk" in file and "versions" not in file:
                folder_name = file
        if folder_name is not None:
            move(f"{self._configuration.jdk_path()}/{folder_name}", java_folder)
        print(f"JDK {version} ACTIVATED!!")

    def get_list_java_versions(self):
        versions = {}
        if 'aws' in self._configuration.repository():
            for java in self.__s3client.list_objects(Bucket=self._configuration.bucket())["Contents"]:
                java_version = java["Key"]
                if self._configuration.so_name() in java_version and "jdk" in java_version:
                    format_version = java_version.replace(f"{self._configuration.so_name()}/", "") \
                        .replace(".tar.gz", "") \
                        .replace("_bin", "")
                    versions[format_version] = java_version
        else:
            extractor = OpenJDKExtractor()
            if 'linux' in self._configuration.so_name():
                for holder in extractor.get_links_linux():
                    versions[holder.version] = holder.link
            else:
                for holder in extractor.get_links_windows():
                    versions[holder.version] = holder.link

        return versions

    def list_java_versions(self):
        versions = list(self.__versions.keys())
        versions.sort(reverse=True, key=get_major_version)
        return versions

    def list_installed_java_versions(self):
        versions = listdir(self._configuration.path_download())
        versions.sort(reverse=True, key=get_major_version)
        return versions

    def delete_all(self):
        for file in self.list_installed_java_versions():
            self.__delete_local_version(file)

    def set_enviroment_var(self):
        if 'windows' in self._configuration.so_name():
            os_system(f'setx /M path "%path%;{self._configuration.jdk_path()}/jdk/bin"')
        else:
            os_system(
                f"echo 'export JAVA_HOME={self._configuration.jdk_path()}/jdk/bin\nexport PATH={self._configuration.jdk_path()}/jdk/bin:$PATH' >> {self._configuration.path_file()}")

    def __version_to_file(self, version):
        return f"{self._configuration.path_download()}/{version.lower()}.tar.gz"

    def __download_java_file(self, version, file_to_download):
        if 'aws' in self._configuration.repository():
            self.__s3client.download_file(self._configuration.bucket(), file_to_download,
                                          self.__version_to_file(version))
        else:
            request.urlretrieve(file_to_download, self.__version_to_file(version))

    def __forma_version(self, version):
        version.replace(f"{self._configuration.so_name()}/", "") \
            .replace(".tar.gz", "") \
            .replace("_bin", "")

    def __delete_local_version(self, java_targz_name):
        remove(f'{self._configuration.path_download()}/{java_targz_name}')

    def __extract_file(self, file):
        if 'linux' in self._configuration.so_name():
            tar = tarfile.open(file, "r:gz")
            tar.extractall(path=f"{self._configuration.jdk_path()}/")
            tar.close()
        else:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall("./")
