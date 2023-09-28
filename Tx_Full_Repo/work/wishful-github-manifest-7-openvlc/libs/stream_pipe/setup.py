from setuptools import setup, find_packages

def readme():
    with open('README') as f:
        return f.read()

setup(
    name = 'stream',
    version='0.1.0',
    packages=find_packages(),
    url = 'http://github.com/aht/stream.py',
    license='',
    author = 'Anh Hai Trinh',
    author_email = 'moc.liamg@hnirt.iah.hna:otliam'[::-1],
    description = "",
    long_description = "",
    keywords='lazy iterator generator stream pipe parallellization data flow functional list processing',
    install_requires=[]
)