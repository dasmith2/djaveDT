import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="djavedt",
    version="1.0.0",
    author="David Smith",
    author_email="dasmith2@example.com",
    description="Some useful datetime functions for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dasmith2/djavedt",
    packages=setuptools.find_packages(),
    install_requires=['django',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
