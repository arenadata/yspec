import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="yspec",
    version="0.0.7",
    author="Anton Chevychalov",
    author_email="cab@arenadata.io",
    description="YAML structure validator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/arenadata/yspec",
    packages=setuptools.find_packages(),
    install_requires=['pyyaml'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/yspec']
)
