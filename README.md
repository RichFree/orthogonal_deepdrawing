# Orthogonal DeepDrawing

## What is this

This is a fork of the original [DeepDrawing](https://github.com/jiayouwyhit/deepdrawing). This repo attempts to test if the model can be applied to orthogonal graphs. Please refer to the original [project webpage](http://yong-wang.org/proj/deepDrawing.html) for the original paper.

## Citation
If you find the original authors' work useful in your research, please consider citing:
```
@ARTICLE{wang19deepdrawing, 
  author  = {Wang, Yong and Jin, Zhihua and Wang, Qianwen and Cui, Weiwei and Ma, Tengfei and Qu, Huamin},
  title   = {DeepDrawing: A Deep Learning Approach to Graph Drawing},
  journal = {IEEE Transactions on Visualization and Computer Graphics},
  year    = {2019}, 
  volume  = {}, 
  number  = {}, 
  pages   = {1-1}
}
```

## Required Packages

For graph generation:

- pygmlparser (pip only)
- pandas
- numpy

For DeepDrawing:

- pytorch-geometric 
- pytorch-sparse
- pytorch-cluster
- pytorch-scatter
- pytorch-spline-conv
- pytorch
- dgl
- cairosvg
- cudatoolkit (if Nvidia GPU is needed)

## Constructing Datasets

```
$ cd graph_generation
$ conda activate <env>
$ bash auto_make_pkl.sh
```

`auto_make_pkl.sh` produces 5 graphs of different nodes. The same data is used for
train/test/valid sets to study memorization properties of the model.

To test generalizability, independent train/test/valid splits can be created with:

```
$ cd graph_generation
$ conda activate <env>
$ bash auto_make_pkl_independent.sh
```

### Modifying auto_make_pkl.sh

From `auto_make_pkl.sh`, an example of how to use `make_graphs` is:

```
$ ./make_graphs 10 30 1 150 1 step1
```

The arguments are:

```
$ ./make_graphs [number of nodes] [max number of edges] [number of graphs to generate] [seed] [is planar?] [output folder]
```

This program was taken from the [pc-tree](https://github.com/N-Coder/pc-tree/) repo. It requires a local installation of OGDF to compile.

The number of edges is set to 3x of number of nodes due to Euler's formula (3\*nodes - 6). For convenience, (3\* number of nodes) is used as the program will correct it to the correct number. [useful reference](https://mathoverflow.net/questions/124116/maximum-number-of-edges-in-a-planar-graph)

## Train Model

In order to train the model

```
$ conda activate <env>
$ python main_train.py
```

The model is saved to `main_data_folder/model_save` for every 10 epochs.

Settings for the model (model parameters, model save location, batch size, etc.)
can be changed in `args.py`.

## Test the Model

To test the model, just run:

```
$ conda activate <env>
$ python main_test.py
```

The generated results will be found in `main_data_folder/testing_results/test_random/`

Additional settings can be set in `main_test.py`.

### Use pretrained model
A pretrained model for data generated from `auto_make_pkl.sh` is in the `main_data_folder/model_save/` folder named `model_GraphLSTM_pyg-ortho_permute_pretrained.pkl`

To use the pretrained model, just copy it to the name used by `main_train.py`

```
$ cd main_data_folder/model_save/
$ cp model_GraphLSTM_pyg-ortho_permute_pretrained.pkl model_GraphLSTM_pyg-ortho_permute.pkl
```

## Data
The data is in a Python pkl format. It contains key graph attributes. The code
to generate the pkl file can be found in `graph_generation/json_to_pkl.py`.

Some additional insights into the data not covered in the original repo:

- The input feature `x` is a generated sequence of features that is almost like a one-hot encoding scheme. 
- The sorted order that `x_idx` and `x_ridx` refers to are the BFS sorted order
  of the graph
    - It is ambiguous where is the starting node, so I used the node with the
      highest between-ness centrality
- Attributes like `adj` and `graph` can be generated using networkx. In fact
  networkx is key to generating many of the attributes in the table.
- The idea behind the pre-processing of OGDF outputs lies in generating new
  nodes in networkx that represents the bend-nodes. This allows the model to
  learn where to introduce bends in the edges.


```
{
  // Core Attribute
  ori -> object, topological information about the graph, includes
  {
    id -> graph id,
    nodelist -> a list contains node information, one row contains [node_id, node_group, cx, cy, r, fill],
    linelist -> a list contains line information, one row contains [node_id_1, node_id_2] representing those two nodes are connected,
    width -> canvas width,
    height -> canvas height
  },
  x -> input feature, note: it is a list
  /////////////////// 
  // ‘x_idx’, ‘x_ridx’ are used to specify the correspondence of the nodes before and after the sorting. 
  // For a graph with four nodes, we will give each node a unique id, e.g., 0,1,2,3. Suppose after the sorting, 
  //     Node 3 => the first location, 
  //     Node 1 => the second location,
  //     Node 0 => the third location,
  //     Node 2 => the fourth location. Then x_idx will be [3,1,0,2].
  // For x_ridx (it is also a list), the i-th location will store the location of Node i in x_idx. Thus, it will be [2,1,3,0]. 
  /////////////////// 
  x_idx -> specify the node IDs (or index) after the sorting,
  x_ridx -> specify the new index of each node after the sorting,
 
  pos -> normalized coordinates,

  // Auxiliary attribute
  len -> the number of nodes,
  bounding_box -> object, specifying the bounding box of layout, includes
  {
    left,right,top,bottom
  },
  adj -> adjacency matrix,
  graph -> adjacency table,
  connected -> whether this graph is connected
}
```

## Caveats

The model cannot really generalize beyond what it is trained on. The reason is that we are overfitting on the structure of the bend nodes. 

Despite the shortcomings, it is interesting to note that the model can be used to
memorize different graph layouts.
