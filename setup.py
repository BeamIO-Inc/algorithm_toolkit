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
    version='0.1.0'
)
