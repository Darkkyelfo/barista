#!/bin/sh
echo "CREATING CONFIGURATION FILE..."
echo "conf:
  download_path: $PWD/versions
  jdk_path: $PWD
  path_file: ~/.bashrc
  repository: openjdk
  bucket: yourawsbucket" > conf.yaml

echo "DOWNLOADING PYTHON DEPENDECIES..."
pip3 install -r requirements
echo "CREATING SYMBOLIC LINK..."
sudo ln -s "$(pwd)/conf.yaml" /usr/bin/conf.yaml
sudo ln -s "$(pwd)/conf.yaml" /usr/bin/barista/conf.yaml
echo "CONFIGURATION OF ENVIROMENT VARIABLE"
python barista.py configure -f
echo "INSTALLATION COMPLETED SUCCESSFULLY"





