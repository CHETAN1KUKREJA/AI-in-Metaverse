from setuptools import setup, find_packages

setup(
    name="memory_system",  
    version="1.0.0",  
    packages=find_packages(), 
    install_requires=[
        "chromadb>=0.4.0", 
    ],
    python_requires=">=3.8",
    description="A sophisticated memory system mimicking human memory processes made for AI in Metaverse",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Achal Jain",
    author_email="achal.jain@tum.de", 
    url="https://gitlab.lrz.de/AImetaverse/llm-backend/-/tree/memory_system?ref_type=heads",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
)
