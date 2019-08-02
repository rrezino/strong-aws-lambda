import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="strong-aws-lambda",
    version="0.0.1",
    author="Rodrigo Farias Rezino",
    author_email="rodrigofrezino@gmail.com",
    description="AWS Lambda enhanced with Python 3 features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rrezino/strong-aws-lambda",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
