'''
To build the package, run:
    pip install --upgrade build && rm dist/*; python -m build

The built package will be in the dist/ directory

To upload the package to PyPI, run:
    pip install --upgrade twine && twine upload dist/*
'''

from setuptools import setup, find_packages
from pathlib import Path

readme = Path(__file__).parent / 'README.md'

setup(
    name='popui',
    version='0.0.12',
    description='A Python module for creating GUI popups with Dear PyGui and AutoHotkey on Windows',
    long_description=readme.read_text(),
    long_description_content_type='text/markdown',
    author='KyleTheScientist',
    author_email='kylethescientist@gmail.com',
    url='https://github.com/KyleTheScientist/popui',
    packages=find_packages(),
    install_requires=[
        'ahk',
        'ahk[binary]',
        'dearpygui',
        'pywin32',
        'screeninfo'
    ],
    keywords=['gui', 'popup', 'dearpygui', 'autohotkey'],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: Microsoft :: Windows',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
