from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_ras_antenna',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Domenico Garlisi',
    author_email='domenico.garlisi@cnit.it',
    description='WiSHFUL RAS antenna Module',
    long_description='Implementation of a RAS agent module using the unified programming interfaces (UPIs) of the Wishful project.',
    keywords='wireless control',
    install_requires=[]
)
