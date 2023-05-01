from setuptools import setup, find_packages

setup(
    name='MonoAPI',
    version='0.1',
    description='A Python package for Monobank API integration',
    author='Oleksii Kravchenko',
    author_email='andibull@gmail.com',
    packages=find_packages(),
    install_requires=[
        requests
    ],
)
