from setuptools import setup

setup(
    name='email2pdf',
    version='',
    packages=['tests', 'tests.Direct', 'tests.Subprocess'],
    url='https://github.com/andrewferrier/email2pdf',
    license='MIT',
    author='Andrew Ferrier',
    description='email2pdf is a Python script to convert emails to PDF.',
    install_requires=[
        'beautifulsoup4>=4.6.3',
        'html5lib',
        'lxml',
        'pypdf2',
        'python-magic',
        'reportlab',
    ],
)
