from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_iperf',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz',
    author_email='gawlowicz@tu-berlin.de',
    description='WiSHFUL Module iperf',
    long_description='WiSHFUL Module iperf',
    keywords='wireless control',
    install_requires=[]
)
