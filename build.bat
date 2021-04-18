@echo off

if "%~1%" == "test"(del /q dist
del /q build
del /q Kilt.egg-info
python setup.py sdist bdist_wheel
twine check dist/* && twine upload --repository testpypi dist/* && echo Test Package Uploaded!
)