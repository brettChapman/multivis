from setuptools import setup

def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name="multivis",
    version="0.5.0",
    description="MultiVis is a data visualisation package that produces both static and interactive visualisations targeted towards the Omics community.",
    long_description=readme(),
    long_description_content_type='text/markdown',
    license="MIT License",
    url="https://github.com/brettChapman/multivis",
    packages=["multivis", "multivis.utils"],
    python_requires=">=3.5",
    install_requires=["numpy==1.20.2",
                      "pandas==1.2.4",
                      "matplotlib==3.4.1",
                      "seaborn==0.11.1",
                      "networkx==2.4.0",
                      "scipy==1.6.3",
                      "scikit-learn==0.24.2",
                      "tqdm==4.36.1",
                      "xlrd==1.2.0"],
    author="Brett Chapman",
    author_email="brett.chapman@murdoch.edu.au, brett.chapman78@gmail.com"
)
