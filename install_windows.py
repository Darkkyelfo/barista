from os import system
import pathlib


def create_a_file(name, content):
    conf_file = open(name, "w")
    conf_file.write(content)
    conf_file.close()


path = pathlib.Path(__file__).parent.resolve()
print("CREATING CONFIGURATION FILE...")
yaml_content = f"""conf:
  path_file: ~/.bashrc
  jdk:
    download_path: {path}\\java_versions
    install_path: {path}
    repository: openjdk
    aws:
      bucket: <BUCKET_NAME>
      #Remove the comments bellow if you want to use a different key than the local one
#      access_key_id: <ACESS_KEY>
#      secret_access_key: <SECRET_KEY
  maven:
    download_path: {path}\\maven_versions
    install_path: {path}
"""
create_a_file("conf.yaml", yaml_content)
print("Installing dependecies")
system("pip install -r requirements")
# Create tables
system("python create_db.py ")
#create a .bat file
python_cmd = f"@ECHO OFF\npython {path}/barista.py %*"
create_a_file("barista.bat", python_cmd)
system("python barista.py configure path -f ")
