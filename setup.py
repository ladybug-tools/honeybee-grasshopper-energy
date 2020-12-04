import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="honeybee-grasshopper-energy",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Ladybug Tools",
    author_email="info@ladybug.tools",
    description="Honeybee Energy plugin for Grasshopper.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ladybug-tools/honeybee-grasshopper-energy",
    packages=setuptools.find_packages(exclude=["samples"]),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: IronPython",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent"
    ],
    license="AGPL-3.0"
)
