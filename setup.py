import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gxipy",
    version="2.0.2407.9061",
    author="Daheng Imaging",
    description="Python API to use with the Daheng Imaging Galaxy SDK.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/maximecharriere/gxipy",
    packages=["gxipy"],
    install_requires=[
        "numpy"
        ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
