#!/usr/bin/env python3
import argparse
from os import path

from exceptions import ERROR_DOWNLOAD, ERROR_FILE_NOT_FOUND_LOCAL_JAVA
from resources import Barista
from util import set_enviroment_var

conf_file = "conf.yaml" if path.exists("conf.yaml") else path.relpath("/usr/bin/conf.yaml")

barista = Barista(conf_file=conf_file)

parser = argparse.ArgumentParser(description='Manager for java and maven versions')
parser.add_argument("-v", '--version', action='version', version=f'%(prog)s {barista.version}')
parser.add_argument("source", help="pass java or maven", type=str, choices=["java", "maven"])
parser.add_argument("operation", help="determine what action will be realizaded.", type=str,
                    choices=["use", "download", "list", "clear", "configure"])
parser.add_argument("name", help="name of the version to be used", nargs='?', type=str, default=None)
parser.add_argument("-f", "--force", help="force download of file", required=False, action='store_true')
parser.add_argument("-l", "--local", help="check the local java or maven version", required=False, action='store_true')
args = parser.parse_args()

if args.operation == 'list':
    if args.local:
        for version in barista.list_installed_java_versions():
            print(version)
    else:
        for version in barista.list_java_versions():
            print(version)
elif args.operation == 'download':
    try:
        version = args.name if not args.name.isnumeric() else barista.find_major_version_from_number(int(args.name))
        barista.download_java_version(version, args.force)
    except KeyError:
        print(ERROR_DOWNLOAD)
elif args.operation == 'use':
    try:
        version = args.name if not args.name.isnumeric() else barista.find_major_version_from_number(int(args.name))
        if args.force:
            barista.download_java_version(version, args.force)
        barista.change_java_version(version)
    except KeyError:
        print(ERROR_DOWNLOAD)
    except FileNotFoundError:
        print(ERROR_FILE_NOT_FOUND_LOCAL_JAVA)

elif args.operation == 'clear':
    barista.delete_all()
elif args.operation == 'configure':
    if args.force:
        set_enviroment_var(barista)
    else:
        response = str(input(f"This command will set the jdk enviroment var to barista folder. S/N ? "))
        if response in 'S':
            set_enviroment_var(barista)
