#!/usr/bin/env python3
import argparse

from configuration import Configuration, EnvironmentSetter
from exceptions import ERROR_FILE_NOT_FOUND_LOCAL_JAVA, AWSRepositoryNotFoundException, \
    JavaVersionNotFoundException, MavenVersionNotFoundException
from managers import JavaManager, MavenManager
import pathlib

try:
    version = "1.0.0-alpha"
    real_path = pathlib.Path(__file__).parent.resolve()
    conf_file = f"{real_path}/conf.yaml"

    parser = argparse.ArgumentParser(description='Manager for java and maven versions')
    parser.add_argument("-v", '--version', action='version', version=f'%(prog)s {version}')
    parser.add_argument("source", help="pass java or maven", type=str, choices=["java", "maven", "configure"])
    parser.add_argument("operation", help="determine what action will be realizaded.", type=str,
                        choices=["use", "download", "list", "clear", "path"])
    parser.add_argument("name", help="name of the version to be used", nargs='?', type=str, default=None)
    parser.add_argument("-f", "--force", help="force download of file", required=False, action='store_true')
    parser.add_argument("-l", "--local", help="check the local java or maven version", required=False,
                        action='store_true')
    args = parser.parse_args()
    configuration = Configuration(file=conf_file)
    barista = None
    if args.source == 'maven':
        barista = MavenManager(configuration=configuration)
    elif args.source == 'java':
        barista = JavaManager(configuration=configuration)
    elif args.source == 'configure':
        if args.force:
            EnvironmentSetter.update_path_values(configuration)
        else:
            response = str(input(f"This command will set the jdk enviroment var to barista folder. S/N ? "))
            if response in 'S':
                EnvironmentSetter.update_path_values(configuration)
    if args.operation == 'list':
        if args.local:
            for version in barista.list_installed_versions():
                print(version)
        else:
            versions = barista.list_versions()
            for i, model in enumerate(versions):
                print(f"{i + 1} - {model.version}")
    elif args.operation == 'download':
        try:
            version = args.name if not args.name.isnumeric() else barista.find_major_version_from_number(int(args.name))
            barista.download_version(version, args.force)
        except JavaVersionNotFoundException as e:
            print(e)
        except MavenVersionNotFoundException as e:
            print(e)
    elif args.operation == 'use':
        try:
            version = args.name if not args.name.isnumeric() else barista.find_major_version_from_number(int(args.name))
            if args.force:
                barista.download_version(version, args.force)
            barista.change_current_version(version)
        except JavaVersionNotFoundException as e:
            print(e)
        except MavenVersionNotFoundException as e:
            print(e)
        except FileNotFoundError:
            print(ERROR_FILE_NOT_FOUND_LOCAL_JAVA)

    elif args.operation == 'clear':
        barista.delete_all()

except AWSRepositoryNotFoundException as e:
    print(e)
