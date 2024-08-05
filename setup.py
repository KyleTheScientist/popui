from setuptools import setup, find_packages

setup(
    name='popui',
    version='0.0.1',
    description='A Python module for creating GUI popups with Dear PyGui and AutoHotkey on Windows',
    author='KyleTheScientist',
    author_email='kylethescientist@gmail.com',
    url='https://github.com/KyleTheScientist/popui',
    packages=find_packages(),
    install_requires=[
        'ahk',
        'dearpygui',
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