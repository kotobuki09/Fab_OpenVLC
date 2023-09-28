from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_upis',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz',
    author_email='gawlowicz@tu-berlin.de',
    description='WiSHFUL UPIS',
    long_description='WiSHFUL UPIS',
    keywords='wireless control',
    install_requires=[]
)
