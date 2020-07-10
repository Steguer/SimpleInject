import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='simpleinject',
    version='1.1.1',
    author="Steven Gerard",
    description="A simple service provider for Python using service injection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Steguer/SimpleInject",
    packages=["simpleinject"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
 )
