"""
Setup script for AI Research Assistant
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    return "AI Personal Research Assistant - Chat with your documents using AI"

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-research-assistant",
    version="1.0.0",
    author="Pratibha Rawat",
    author_email="pratibharawat6991@gmail.com",
    description="An AI-powered personal research assistant for document analysis",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Pratibha36/AI-Personal-Research-Assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: General",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "pytest-cov>=4.1.0",
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
        ]
    },
    entry_points={
        "console_scripts": [
            "ai-research-assistant=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="ai, research, assistant, documents, nlp, vector-database, gradio",
    project_urls={
        "Bug Reports": "https://github.com/Pratibha36/AI-Personal-Research-Assistant",
        "Source": "https://github.com/Pratibha36/AI-Personal-Research-Assistant",
        "Documentation": https://github.com/Pratibha36/AI-Personal-Research-Assistant",
    },
)
