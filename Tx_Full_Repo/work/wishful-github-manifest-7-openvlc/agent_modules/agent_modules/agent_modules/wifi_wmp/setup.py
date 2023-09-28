from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='wishful_module_wifi_wmp',
    version='0.1.0',
    packages=find_packages(),
    url='http://www.wishful-project.eu/software',
    license='',
    author='Domenico Garlisi',
    author_email='domenico.garlisi@cnit.it',
    description='WiSHFUL WMP Modules',
    long_description='WiSHFUL WMP Modules',
    keywords='WMP wireless control',
    install_requires=['netifaces','scapy-python3','numpy', 'python-iptables', 'pyroute2']
)
