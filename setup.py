from setuptools import find_packages, setup

setup(
    name='escriptorium-collate ',
    version='0.1.0',
    author="Osama Eshera",
    author_email="osama.eshera@gmail.com",
    description="A python package for collating eScriptorium documents.",
    packages=find_packages(),
    install_requires=[
        "escriptorium_connector",
        "minineedle",
        "nltk",
        "pydantic",
    ],
)
