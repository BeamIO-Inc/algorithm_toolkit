from setuptools import setup


setup(
    name='algorithm_toolkit',
    packages=['algorithm_toolkit'],
    include_package_data=True,
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
        'distro',
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
    version='0.1.0'
)
