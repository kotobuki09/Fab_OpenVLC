from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_mininet',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Anatolij Zubow',
    author_email='{zubow}@tkn.tu-berlin.de',
    description='WiSHFUL Mininet',
    long_description='Running WiSHFUL agents/controllers in Mininet',
    keywords='wireless control mininet',
    install_requires=['pyyaml', 'docopt']
)
