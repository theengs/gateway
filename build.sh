rm -r ./dist
pip3 uninstall -y TheengsGateway
python3 setup.py sdist
cd dist
pip3 install TheengsGateway-0.1.4.tar.gz --no-deps
curl --data "compiling durch, bruder" http://192.168.2.64:12101/api/text-to-speech
