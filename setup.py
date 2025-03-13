from setuptools import setup, find_packages

setup(
    name="ethicrawl",
    version="1.0.0a1",
    packages=find_packages(),
    install_requires=[
        "requests>=2.32.0",
        "lxml>=5.3.0",
        "protego>=0.4.0",
        "colorama>=0.4.6",
        "selenium>=4.29.0",
    ],
    python_requires=">=3.10",
)
