from setuptools import setup, find_packages

setup(
    name="atcp",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
        'asyncio',
        'logging',
    ],
)
