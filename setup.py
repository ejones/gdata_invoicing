from setuptools import setup
from os import path
from os.path import dirname

setup(
    name='gdata_invoicing',
    version='0.0.1',
    author='Evan Jones',
    author_email='evan.q.jones@gmail.com',
    url='http://github.com/ejones/gdata_invoicing',
    license='MIT',
    description='Invoicing with with ReportLab and Google Calendar',
    long_description=open(path.join(dirname(__file__), 'README.rst')).read(),
    packages=['gdata_invoicing'],
    install_requires=['gdata >= 2.0.13', 'reportlab >= 2.5'],
)
