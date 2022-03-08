del /F /Q dist
pip uninstall -y TheengsGateway
python setup.py sdist
cd dist
pip install TheengsGateway-0.1.4.tar.gz --no-deps
python -m TheengsGateway