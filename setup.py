import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="servicecomposer",
        version="0.1",
        description="tool for composing several services",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="",
        packages=setuptools.find_packages(),
        package_dir={"": "src"},
        author="Timo Stüber",
        author_email="omit66@gmail.com",
        install_requires=["Click", "pyyaml", "GitPython"],
        classifiers=[
            "Programming Language :: Python 3",
        ],
        python_requires=">3.6",
        entry_points={
            'console_scripts': ['servicecomposer=servicecomposer.cli:main'],
        }
        )
