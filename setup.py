from setuptools import setup

def readme():
    with open('README.md', encoding='utf-8') as f:
        return f.read()

setup(
    name="multivis",
    version="0.5.11",
    description="MultiVis is a data visualisation package that produces both static and interactive visualisations targeted towards the Omics community.",
    long_description=readme(),
    long_description_content_type='text/markdown',
    license="MIT License",
    url="https://github.com/brettChapman/multivis",
    packages=["multivis", "multivis.utils"],
    python_requires="==3.11.4",
    install_requires=["numpy==1.25.2",
                      "openpyxl==2.6.1",
                      "pandas==2.1.0",
                      "matplotlib==3.8.0",
                      "seaborn==0.12.2",
                      "networkx==3.1.0",
                      "statsmodels==0.14.0",
                      "scikits-bootstrap==1.1.0",
                      "scipy==1.11.2",
                      "scikit-learn==1.3.1",
                      "tqdm==4.66.1",
                      "xlrd==2.0.1"],
    author="Brett Chapman",
    author_email="brett.chapman@murdoch.edu.au, brett.chapman78@gmail.com"
)
