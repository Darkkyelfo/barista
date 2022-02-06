#!/usr/bin/env python3
import argparse

from exceptions import ERROR_DOWNLOAD, ERROR_SET_ENV_VAR
from resources import Barista


def set_enviroment_var(barista):
    try:
        barista.set_enviroment_var()
        print("CONFIGURATION REALIZED !")
    except:
        print(ERROR_SET_ENV_VAR)


parser = argparse.ArgumentParser(description='Manager for java and maven versions')
parser.add_argument("source", help="pass java or maven", type=str, choices=["java", "maven"])
parser.add_argument("operation", help="determine what action will be realizaded.", type=str,
                    choices=["use", "download", "list", "clear", "configure"])
parser.add_argument("-v", "--version", help="the version of java ou maven to be utilized", type=str, required=False)
parser.add_argument("-f", "--force", help="force download of file", required=False, action='store_true')
parser.add_argument("-l", "--local", help="check the local java or maven version", required=False, action='store_true')
args = parser.parse_args()

barista = Barista()
if args.operation == 'list':
    if args.local:
        for version in barista.list_installed_java_versions():
            print(version)
    else:
        for version in barista.list_java_versions():
            print(version)
elif args.operation == 'download':
    try:
        barista.download_java_version(args.version, args.force)
    except KeyError:
        print(ERROR_DOWNLOAD)
elif args.operation == 'use':
    if args.force:
        try:
            barista.download_java_version(args.version, args.force)
        except KeyError:
            print(ERROR_DOWNLOAD)
    barista.change_java_version(args.version)
elif args.operation == 'clear':
    barista.delete_all()
elif args.operation == 'configure':
    if args.force:
        set_enviroment_var(barista)
    else:
        response = str(input(f"This command will set the jdk enviroment var to barista folder. S/N ? "))
        if response in 'S':
            set_enviroment_var(barista)
