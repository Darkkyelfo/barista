from abc import ABC, abstractmethod
from os import path, mkdir, listdir, remove
from shutil import move, rmtree
from urllib import request
from xml.etree import ElementTree

import boto3
from botocore.exceptions import ParamValidationError

from exceptions import AWSRepositoryNotFoundException, MavenVersionNotFoundException, JavaVersionNotFoundException, \
    MavenFolderNotFound
from model import Maven, Java
from parsers import OpenJDKExtractor, MavenExtractor
from util import get_major_version, extract_tar, extract_zip


class Manager(ABC):

    @abstractmethod
    def download_version(self, version: str, force=False):
        pass

    @abstractmethod
    def change_current_version(self, version):
        pass

    @abstractmethod
    def list_versions(self):
        pass

    @abstractmethod
    def list_installed_versions(self):
        pass

    @abstractmethod
    def delete_all(self):
        pass

    def reset_version_list(self):
        pass


class JavaManager(Manager):

    def __init__(self, configuration):
        try:
            self._configuration = configuration
            self.__load_dataset()
            if 'aws' in self._configuration.repository():
                self.__s3client = boto3.client('s3',
                                               aws_access_key_id=self._configuration.acess_key(),
                                               aws_secret_access_key=self._configuration.secret_key())
            if not path.exists(self._configuration.path_download()):
                mkdir(self._configuration.path_download())
        except ParamValidationError:
            raise AWSRepositoryNotFoundException

    def download_version(self, version: str, force=False):
        try:
            file_to_download = Java.select().where(Java.version == version)[0].link
            version_exists = False
            file_name = None
            for file in self.list_installed_versions():
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
        except KeyError:
            raise JavaVersionNotFoundException(version)

    def change_current_version(self, version):
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

    def list_versions(self):
        return Java.select().where(
            Java.so == self._configuration.so_name() and Java.repository == self._configuration.repository()).order_by(
            Java.major_version, Java.version)

    def list_installed_versions(self):
        versions = listdir(self._configuration.path_download())
        versions.sort(reverse=True, key=get_major_version)
        return versions

    def reset_version_list(self):
        Java.delete().execute()
        self.__load_dataset()

    def delete_all(self):
        for file in self.list_installed_versions():
            self.__delete_local_version(file)

    def find_major_version_from_number(self, passed_version: int):
        try:
            return Java.select().where(Java.major_version == passed_version) \
                .order_by(Java.major_version, Java.version.desc())[0].version
        except IndexError:
            raise JavaVersionNotFoundException(passed_version)

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
            extract_tar(file, f"{self._configuration.jdk_path()}/")
        else:
            extract_tar(file, f"{self._configuration.jdk_path()}\\")

    def __load_dataset(self):
        if len(Java.select()) == 0:
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

            Java.save_multiple_versions(versions, self._configuration.so_name(), self._configuration.repository())


class MavenManager(Manager):

    def __init__(self, configuration):
        versions = Maven.select()
        if len(versions) == 0:
            Maven.save_multiple_versions(MavenExtractor.get_versions())

        self._configuration = configuration
        if not path.exists(self._configuration.path_maven_download()):
            mkdir(self._configuration.path_maven_download())

    def download_version(self, version: str, force=False):
        try:
            version_url = Maven.select().where(Maven.version == version)[0].link
            print(version_url)
            is_installed = self.__version_in_local(version)
            if not is_installed:
                print(f"DOWNLOADING {version}...")
                self.__download_file(version, version_url)
                print(f"DOWNLOAD {version} FINISHED !")
            elif force:
                print(f"DELETING current version...")
                self.__delete_local_version(version)
                print(f"DOWNLOADING {version}...")
                self.__download_file(version, version_url)
                print(f"DOWNLOAD {version} FINISHED !")
        except KeyError:
            raise MavenVersionNotFoundException(version)

    def change_current_version(self, version):
        maven_folder = f"{self._configuration.maven_path()}/maven"
        if path.exists(maven_folder):
            rmtree(maven_folder)
        targz_file_name = self.__maven_tar_name(version)
        extract_tar(f"{self._configuration.path_maven_download()}/{targz_file_name}",
                    f"{self._configuration.maven_path()}/")
        folder_name = None
        for file in listdir(self._configuration.maven_path()):
            if "maven" in file and version in file:
                folder_name = file
                break
        if folder_name is not None:
            move(f"{self._configuration.jdk_path()}/{folder_name}", maven_folder)
        self.__set_m2_folder(version)
        print(f"MAVEN {version} ACTIVATED!!")

    def list_versions(self):
        return Maven.select().order_by(Maven.version)

    def list_installed_versions(self):
        versions = listdir(self._configuration.path_maven_download())
        versions.sort()
        return versions

    def delete_all(self):
        for file in self.list_installed_versions():
            self.__delete_local_version(file)

    def reset_version_list(self):
        Maven.reset_dataset(MavenExtractor.get_versions())

    def __version_in_local(self, version):
        for local_version in self.list_installed_versions():
            if version in local_version:
                return True
        return False

    def __delete_local_version(self, version):
        remove(f'{self._configuration.path_maven_download()}/{self.__maven_tar_name(version)}')

    def __download_file(self, version, version_url):
        request.urlretrieve(version_url,
                            f"{self._configuration.path_maven_download()}/{self.__maven_tar_name(version)}")

    def __maven_tar_name(self, version):
        return f"apache-maven-{version}-bin.tar.gz"

    def __set_m2_folder(self, name_folder):
        folder_to_save = f"{self._configuration.m2_path()}/m2_{name_folder}"
        if not path.exists(f"{self._configuration.maven_path()}/maven"):
            raise MavenFolderNotFound
        if not path.exists(folder_to_save):
            mkdir(folder_to_save)
        settings_file = f"{self._configuration.maven_path()}/maven/conf/settings.xml"

        file_xml = ElementTree.parse(settings_file)
        root = file_xml.getroot()
        local_repository = ElementTree.Element("localRepository")
        local_repository.text = folder_to_save
        root.insert(0, local_repository)
        file_xml.write(settings_file)
