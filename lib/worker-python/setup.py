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
    entry_points='''
        [console_scripts]
        fstq=fstq.cli.cli:main
    ''',
    install_requires=[
        'click==7.1.2', 'firebase-admin==4.4.0', 'docker==4.3.1',
        'google-cloud-container==2.1.0', 'kubernetes==11.0.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)