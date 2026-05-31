from setuptools import setup, find_packages

setup(
    name="hypermark-py",  # Name of your package on PyPI
    version="1.0.2",  # Version of your package
    author="SwapCodesDev",  # Replace with your name
    author_email="swapcodes.dev@gmail.com",  # Replace with your email
    description="A Python package for converting Markdown to HTML",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/SwapCodesDev/hypermark",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hypermark=hypermark.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Match the LICENSE file
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=['beautifulsoup4', 'emoji'],  # Add dependencies here if needed
    package_data={'hypermark': ['README.md', 'LICENSE', 'hypermark.css']},
    license="MIT",
)
