from setuptools import setup
from kilt.version import __version__

pre = {
    "beta": "b",
    "alpha": "a",
    "rc": "rc"
}
pypi_version = "{}.{}.{}{}".format(
    __version__.major, __version__.minor, __version__.patch,
    pre[__version__.prerelease[0]] + __version__.prerelease[1])

with open("README.md") as f:
    long_desc = f.read()
setup(
    name='Kilt',
    version=pypi_version,
    description='A Python Library for for high-end interaction wit the Modrinth API/labrinth.',
    url='https://github.com/Jefaxe/Kilt',
    author='Jefaxe',
    author_email='jefaxe.dev@gmail.com',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=['kilt'],
    keywords=["Minecraft", ",Modding", "Labrinth", "Kilt", "Jefaxe", "Modrinth"],
    install_requires=['semantic-version',
                      "Pillow"
                      ],
    classifiers=[
        'Development Status :: 4 - Beta',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3.9'  # Specify which python versions that you want to support
    ],
)
