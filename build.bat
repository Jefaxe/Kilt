@echo off

python kilt/version.py

if "%~1%" == "test"(del /q dist
del /q build
del /q Kilt.egg-info
del /q dist
python setup.py sdist
twine check dist/* && twine upload --repository testpypi dist/* && echo Test Package Uploaded!
)