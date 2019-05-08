from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="cimcb_vis",
    version="0.1",
    description="This is a pre-release.",
    long_description=long_description,
    license="http://www.apache.org/licenses/LICENSE-2.0.html",
    url="https://github.com/brettChapman/cimcb_vis",
    packages=["cimcb_vis", "cimcb_vis.networks", "cimcb.utils"],
    python_requires=">=3.5",
    install_requires=["numpy>=1.12",
                      "pandas",
		      "matplotlib",
		      "seaborn",
	 	      "networkx",
                      "scipy",
                      "scikit-learn"]
    author="Brett Chapman, David Broadhurst",
    author_email="brett.chapman@ecu.edu.au, d.broadhurst@ecu.edu.au"
)
