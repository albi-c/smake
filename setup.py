import setuptools

long_description = """"""

setuptools.setup(
    name="SMake",
    version="0.0.1",
    author="albi-c",
    description="simple c/c++ build system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    project_urls={},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": {
            "smake = smake.cli:main"
        }
    }
)
