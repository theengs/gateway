rm -r ./dist
pip3 uninstall -y TheengsGateway
python3 setup.py sdist
cd distpip install TheengsGateway-0.1.4.tar.gz