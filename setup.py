from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="multi-vis",
    version="0.1.4",
    description="multi-vis is a data visualisation package that produces both static and interactive visualisations targeted towards the Omics community.",
    long_description=long_description,
    license="MIT License",
    url="https://github.com/brettChapman/multi-vis",
    packages=["multi-vis", "multi-vis.utils"],
    python_requires=">=3.5",
    install_requires=["numpy>=1.12",
                      "pandas",
		      "matplotlib",
		      "seaborn",
	 	      "networkx",
                      "scipy",
                      "scikit-learn",
		      "tqdm"],
    author="Brett Chapman, David Broadhurst",
    author_email="brett.chapman@ecu.edu.au, d.broadhurst@ecu.edu.au"
)
