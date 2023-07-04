from setuptools import setup, find_packages

setup(
    name='labtools',
    version='0.1',
    py_modules=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'pydantic',
        'pystac',
        'stac-pydantic',
        'astropy',
        'pyMarsSeason @ git+https://github.com/pole-surfaces-planetaires/pymarsseason.git'
    ],
    entry_points='''
        [console_scripts]
        labtools=labtools.cli:cli
    ''',
)
