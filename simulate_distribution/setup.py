from setuptools import setup, find_packages

setup(
    name="object_distribution",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A library for simulating different object distribution algorithms",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/object_distribution",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 