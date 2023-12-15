from setuptools import setup, find_packages

setup(
    name='escriptorium-collate ',
    version='0.1.0',
    author="Osama Mohamed Eshera",
    author_email="@",
    description="A python package for collecting ....",
    packages=find_packages(),
    ],
    install_requires=[
        # List your dependencies here
        "minineedle",
        "pydantic",
        "escriptorium_connector",
        "nltk",
    ],
    )

