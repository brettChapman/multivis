from setuptools import setup

def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name="multivis",
    version="0.4.2",
    description="MultiVis is a data visualisation package that produces both static and interactive visualisations targeted towards the Omics community.",
    long_description=readme(),
    long_description_content_type='text/markdown',
    license="MIT License",
    url="https://github.com/brettChapman/multivis",
    packages=["multivis", "multivis.utils"],
    python_requires=">=3.5",
    install_requires=["numpy>=1.12",
                      "pandas==0.25.1",
                      "matplotlib==3.1.1",
                      "seaborn==0.9.0",
                      "networkx==2.3.0",
                      "scipy==1.3.1",
                      "scikit-learn==0.21.3",
                      "tqdm==4.36.1",
                      "xlrd==1.2.0"],
    author="Brett Chapman",
    author_email="brett.chapman@murdoch.edu.au, brett.chapman78@gmail.com"
)
