from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_lte',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Domenico Garlisi',
    author_email='domenico.garlisi@cnit.it',
    description='WiSHFUL WIFI Module',
    long_description='Implementation of a wireless agent using the unified programming interfaces (UPIs) of the Wishful project.',
    keywords='wireless control',
    install_requires=[]
)
