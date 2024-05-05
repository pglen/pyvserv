mkdir -p dist
mkdir -p build
rm -rf dist/*
rm -rf build/*
#python setup.py build
python3 -m build
