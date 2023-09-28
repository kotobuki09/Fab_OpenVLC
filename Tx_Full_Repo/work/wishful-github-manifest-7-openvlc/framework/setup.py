from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_framework',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz',
    author_email='gawlowicz@tu-berlin.de',
    description='WiSHFUL Framwork',
    long_description='WiSHFUL Framwork',
    keywords='wireless control',
    install_requires=['protobuf==3.0.0b2', 'future']
)
