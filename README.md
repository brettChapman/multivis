<img src="cimcb_logo.png" alt="drawing" width="400"/>

# multivis
multivis package containing the necessary tools for the visualisation of correlated data.

## Installation

### Dependencies
multivis requires:
- Python (>=3.5)
- NumPy (>=1.12)
- Pandas
- Matplotlib
- Seaborn
- Networkx
- SciPy
- Scikit-learn
- tqdm

### User installation
The recommend way to install cimcb_vis and dependencies is to using ``conda``:
```console
conda install -c brett.chapman multivis
```
or ``pip``:
```console
pip install multivis
```
Alternatively, to install directly from github:
```console
pip install https://github.com/brettChapman/multivis/archive/master.zip
```

### API
For further detail on the usage refer to the docstring.

#### multivis
- [Edge](https://github.com/brettChapman/multivis/blob/master/multivis/Edge.py): Generates dataframe of edges prior to visualisation.
- [Network](https://github.com/brettChapman/multivis/blob/master/multivis/Network.py) Generates dataframe of edges, with network parameters and a networkx graph prior to visualisation.
- [edgeBundle](https://github.com/brettChapman/multivis/blob/master/multivis/edgeBundle.py): Generates necessary Json structure and produces Hierarchical edge bundle plot.
- [plotNetwork](https://github.com/brettChapman/multivis/blob/master/multivis/plotNetwork.py): Static spring plot using pygraphviz and networkx.
- [forceNetwork](https://github.com/brettChapman/multivis/blob/master/multivis/forceNetwork.py): Interactive force-directed network which inherits data from the networkx graph
- [clustermap](https://github.com/brettChapman//multivis/blob/master/multivis/clustermap.py): Clustered heatmap with dendrograms.
- [polarDendrogram](https://github.com/brettChapman/multivis/blob/master/multivis/polarDendrogram.py): Polar dendrogram

#### multivis.utils
- [mergeBlocks](https://github.com/brettChapman/multivis/blob/master/multivis/utils/mergeBlocks.py): Merges multiply diffent blocks into a single peak table and data table.
- [range_scale](https://github.com/brettChapman/multivis/blob/master/multivis/utils/range_scale.py): Scales a range of values between user chosen values.
- [corrAnalysis](https://github.com/brettChapman/multivis/blob/master/multivis/corrAnalysis.py): Correlation analysis with Pearson, Spearman or Kendall's Tau.
- [cluster](https://github.com/brettChapman/multivis/blob/master/multivis/utils/spatialClustering.py): Clusters data using a linkage cluster method. If the data is correlated the correlations are first preprocessed, then clustered, otherwise a distance metric is applied to non-correlated data before clustering.

### License
multivis is licensed under the ___ license.

### Authors
- Brett Chapman
- https://scholar.google.com.au/citations?user=A_wYNAQAAAAJ&hl=en

### Correspondence
Dr. Brett Chapman, Post-doctoral Research Fellow at the Centre for Integrative Metabolomics & Computational Biology at Edith Cowan University.
E-mail: brett.chapman@ecu.edu.au

### Citation
If you would cite cimcb_vis in a scientific publication, you can use the following: ___
