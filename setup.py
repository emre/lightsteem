from setuptools import setup, find_packages

setup(
    name='lightsteem',
    version='0.0.3',
    packages=find_packages('.'),
    url='http://github.com/emre/lightsteem',
    license='MIT',
    author='emre yilmaz',
    author_email='mail@emreyilmaz.me',
    description='A light python client to interact with the STEEM blockchain',
    install_requires=["requests"]
)
