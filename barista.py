#!/usr/bin/env python3
import argparse

from resources import Barista

parser = argparse.ArgumentParser(description='Manager for java and maven versions')
parser.add_argument("source", help="pass java or maven", type=str, choices=["java", "maven"])
parser.add_argument("operation", help="determine what action will be realizaded.", type=str,
                    choices=["use", "download", "list", "clear"])
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
    barista.download_java_version(args.version, args.force)
elif args.operation == 'use':
    barista.download_java_version(args.version)
    barista.change_java_version(args.version)
elif args.operation == 'clear':
    barista.delete_all()
