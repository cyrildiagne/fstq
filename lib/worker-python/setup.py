import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fstq-worker-python",
    version="0.0.1",
    author="Cyril Diagne",
    author_email="diagne.cyril@gmail.com",
    description="Python worker lib for FSTQ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyrildiagne/fstq",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)