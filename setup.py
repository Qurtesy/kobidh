from setuptools import setup, find_packages
from kobidh.meta import VERSION

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("./_requirements/main.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="kobidh",
    version=VERSION,
    description="CLI tool for automating the deployment process of server-side applications with ease and efficiency",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Qurtesy/kobidh",
    author="Souvik Dey",
    author_email="dsouvik141@gmail.com",
    license="MIT",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        kobidh=kobidh.cli:main
    """,
    keywords=["cli", "automation", "deployment", "server-side", "devops"],
)
