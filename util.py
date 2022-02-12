import re
import tarfile
import zipfile
from urllib import request

from bs4 import BeautifulSoup


def get_major_version(java_version_name: str):
    version = re.findall(r'\d+', java_version_name)
    return int(version[0])


def mapp_version(versions_dict, holder):
    versions_dict[holder.version] = holder.link
    major_version = get_major_version(holder.version)
    if versions_dict.get(major_version) is None:
        versions_dict[major_version] = holder.version


def extract_tar(tar_file, extract_path):
    tar = tarfile.open(tar_file, "r:gz")
    tar.extractall(path=extract_path)
    tar.close()


def extract_zip(zip_file, extract_path):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)


def get_html_page(url):
    request_conn = request.urlopen(url)
    html_bytes = request_conn.read()
    html_page = html_bytes.decode("utf8")
    request_conn.close()

    return BeautifulSoup(html_page, features="html.parser")
