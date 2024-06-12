from setuptools import find_packages, setup

setup(
    name="escriptorium-collate",
    version="0.1.5",
    author="Osama Eshera",
    author_email="osama.eshera@gmail.com",
    description="A Python library for collating eScriptorium documents.",
    url="https://github.com/oeshera/escriptorium-collate",
    packages=find_packages(),
    install_requires=[
        "escriptorium-connector",
        "minineedle",
        "nltk",
        "pydantic",
        "python-dotenv",
    ],
    setup_requires=["pytest-runner", "flake8"],
    tests_require=["pytest"],
)
