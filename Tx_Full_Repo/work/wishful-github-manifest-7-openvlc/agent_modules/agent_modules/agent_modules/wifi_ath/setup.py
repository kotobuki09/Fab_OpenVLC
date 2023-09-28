from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_wifi_ath',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Piotr Gawlowicz',
    author_email='gawlowicz@tu-berlin.de',
    description='WiSHFUL ATH Modules',
    long_description='WiSHFUL ATH Modules',
    keywords='wireless control',
    install_requires=['netifaces','scapy-python3','numpy', 'python-iptables', 'pyroute2']
)
