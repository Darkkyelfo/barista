import os
from platform import system

import yaml

from exceptions import AWSRepositoryNotFoundException


class Configuration:
    def __init__(self, file="conf.yaml"):
        try:
            with open(file) as f:
                conf_yaml = yaml.load(f, Loader=yaml.FullLoader)["conf"]
                self.__download_java_path = conf_yaml['download_java_path']
                self.__download_maven_path = conf_yaml['download_maven_path']
                self.__path_file = conf_yaml['path_file']
                self.__jdk_path = conf_yaml['jdk_path']
                self.__maven_path = conf_yaml['maven_path']
                self.__repository = conf_yaml['java_repository']
                if self.__repository.lower() in 'aws':
                    self.__bucket = conf_yaml['aws']['bucket']
                    self.__set_aws_acess_and_secret(conf_yaml)
            self.__so = system().lower()
        except KeyError:
            raise AWSRepositoryNotFoundException

    def path_download(self):
        return self.__download_java_path

    def path_maven_download(self):
        return self.__download_maven_path

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

    def acess_key(self):
        return self.__acess_key

    def secret_key(self):
        return self.__secret_key

    def maven_path(self):
        return self.__maven_path

    def __set_aws_acess_and_secret(self, conf_yaml):
        try:
            self.__secret_key = conf_yaml['aws']['secret_access_key']
            self.__acess_key = conf_yaml['aws']['access_key_id']
        except KeyError:
            self.__secret_key = None
            self.__acess_key = None


class EnvironmentSetter:

    @staticmethod
    def update_path_values(configuration: Configuration):

        if 'windows' in configuration.so_name():
            os.system(f'setx /M path "%path%;{configuration.maven_path()}/maven/bin"')
            os.system(f'setx /M path "%path%;{configuration.maven_path()}/maven/bin"')
        else:
            exports_path = f"""
export MAVEN_HOME={configuration.maven_path()}/maven
export JAVA_HOME={configuration.jdk_path()}/jdk
export PATH=$MAVEN_HOME/bin:$JAVA_HOME/bin:$PATH"""
            os.system(f"echo '{exports_path}' >> {configuration.path_file()}")
