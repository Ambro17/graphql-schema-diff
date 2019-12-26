from setuptools import setup, find_packages


with open("README.md", "r") as f:
    long_description = f.read()

with open("requirements.txt", "r") as f:
    requirements = f.read()

package_name = "graphql-schema-diff"

setup(
    name=package_name,
    version="0.0.3",
    author="Nahuel Ambrosini",
    author_email="ambro17.1@gmail.com",
    description="Compare GraphQL Schemas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ambro17/schemadiff",
    packages=find_packages(include=['schemadiff*'], exclude=['tests', 'tests.*']),
    install_requires=requirements,
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'schemadiff=schemadiff.__main__:cli',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    data_files=[('', ['LICENSE'])]
)