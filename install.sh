#!/bin/sh
echo "CREATING CONFIGURATION FILE..."
echo "conf:
  download_path: $PWD/versions
  jdk_path: $PWD
  path_file: ~/.bashrc
  repository: openjdk
  aws:
    bucket: <BUCKET_NAME>
    #Remove the comments bellow if you want to use a different key than the local one
#    access_key_id: <ACESS_KEY>
#    secret_access_key: <SECRET_KEY" >> conf.yaml

echo "DOWNLOADING PYTHON DEPENDECIES..."
pip install -r requirements
echo "GRANTING EXECUTION PERMISSION..."
sudo chmod +x barista.py
echo "CREATING SYMBOLIC LINK..."
sudo ln -s "$(pwd)/conf.yaml" /usr/bin/conf.yaml
sudo ln -s "$(pwd)/barista.py" /usr/bin/barista
echo "CONFIGURATION OF ENVIROMENT VARIABLE"
python3 barista.py java configure -f
echo "INSTALLATION COMPLETED SUCCESSFULLY"





