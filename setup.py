import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esp8266.py",
    version="0.0.3",
    author="letli",
    author_email="letli@74ls74.org",
    description="ESP8266 python library, a wrapper for AT commands (Hayes command set) using UART serial.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/muchrooms/esp8266.py",
    #packages=setuptools.find_packages(),
    packages=['esp8266'],
    install_requires=[
        'pySerial>=3.0'
    ],
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
