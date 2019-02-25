from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    author="BeamIO, Inc.",
    author_email="info@beamio.net",
    name="algorithm_toolkit",
    description=(
        "This project provides an easy way for researchers and "
        "developers to develop and share algorithms related to "
        "geospatial data and imagery."
    ),
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/BeamIO-Inc/algorithm_toolkit",
    license="MIT",
    install_requires=[
        'configparser',
        'distro',
        'flask >= 1.0',
        'flask-cors',
        'flask_wtf',
        'inflect',
        'numpy',
        'psutil',
        'python-dotenv',
        'requests',
        'tabulate',
        'psutil'
    ],
    entry_points={
        'console_scripts': ['alg=cli.cli:cli']
    },
    project_urls={
        "Documentation":
            "https://algorithm-toolkit.readthedocs.io/en/latest/index.html",
        "Source Code": "https://github.com/BeamIO-Inc/algorithm_toolkit",
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    version='0.1.2'
)
