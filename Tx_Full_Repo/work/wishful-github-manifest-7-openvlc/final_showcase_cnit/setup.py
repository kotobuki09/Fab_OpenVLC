from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='final_showcase',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Peter Ruckebusch',
    author_email='peter.ruckebusch@ugent.be',
    description='WiSHFUL Final Showcase',
    long_description='WiSHFUL Final Showcase',
    keywords='wireless control',
    install_requires=['pyyaml', 'docopt', 'matplotlib']
)

