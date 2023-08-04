import networkx as nx 
import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
import pickle as pkl
import itertools
from sys import argv
import sys
from collections import defaultdict

sys.path.insert(0, '../')

from utils import *

# function to get the orientation/direction of the current edge
# edge contains (node1, node2), where node = [x,y]
def get_direction(edge):
    node1 = edge[0]
    node2 = edge[1]

    if abs(node1[0] - node2[0]) < 0.1:
        return "vertical"
    elif abs(node1[1] - node2[1]) < 0.1:
        return "horizontal"
    else:
        return "don't know"
    
# return true bend points 
# context: ogdf sometimes gives points that are not bend points in the edge list
def get_bend_points(edge_path):
    bend_points = []
    prev_direction = ""
    for i in range(len(edge_path)):
        # exit condition
        if (i == len(edge_path) - 1):
            break;
        
        # compute current edge direction
        current_path = (edge_path[i], edge_path[i+1])
        direction = get_direction(current_path)
    
        if (i == 0):
            prev_direction = direction
        if (i > 0):
            if ((prev_direction == "vertical" and direction == "horizontal") or 
                (prev_direction == "horizontal" and direction == "vertical")):
                bend_points.append(edge_path[i])
            # set the current direction to be prev for next iteration
            prev_direction = direction

    return bend_points
        

# function to produce modified graph
def create_graph(data):

    G = nx.DiGraph()

    # read in actual nodes first
    node_coordinate = {}
    # first, add the real nodes
    for node_obj in data['nodes']:
        identity = node_obj['id']
        G.add_node(identity)
        node_coordinate[identity] = (node_obj['x'], node_obj['y'], 0)

    # create virtual nodes to split an edge
    node_counter = G.number_of_nodes() -1  # node_id starts from 0
    for edge in data['edges']:
        source = edge['source']
        target = edge['target']
        # full_points_list = [list(node_coordinate[source][0:3])] + edge['path'] + [list(node_coordinate[target][0:3])]
        full_points_list = edge['path']
        # get all bend points only - ignore other points
        bend_points_list = get_bend_points(full_points_list)
        num_points = len(bend_points_list) 
        # connect from real node to first intermediate node
        inter = source
        if num_points == 0:
            G.add_edge(source, target)
            # add reverse edge
            G.add_edge(target, source)
        else:
            for i in range(num_points):
                current_node = bend_points_list[i]
                node_counter = node_counter + 1
                G.add_node(node_counter)
                node_coordinate[node_counter] = (current_node[0], current_node[1], 1)
                G.add_edge(inter, node_counter)
                # add reverse edge
                G.add_edge(node_counter, inter)
                inter = node_counter
            # last edge
            G.add_edge(inter, target)
            # add reverse edge
            G.add_edge(target, inter)
            
    # start of nodelist generation
    nodelist = []

    for node_id in G.nodes:
        # main nodes
        if node_coordinate[node_id][2] == 0:
            node_group = 0
            r = 5
            fill = 'blue'
        # bend nodes
        elif node_coordinate[node_id][2] == 1:
            node_group = 1
            r = 2
            fill = 'orange'
        # alignment nodes
        else:
            node_group = 2
            r = 2
            fill = 'red'

        cx = node_coordinate[node_id][0]
        cy = node_coordinate[node_id][1]
        node = [node_id, node_group, cx, cy, r, fill]
        nodelist.append(node)

    # start of linelist generation
    linelist = G.edges

    return G, nodelist, linelist
        

# produce the "ori" dictionary object required for the dataset
def produce_ori(ori_id, nodelist, linelist, height, width):
    ori = {}

    ori['id'] = ori_id
    ori['nodelist'] = nodelist
    ori['linelist'] = linelist
    ori['height'] = height
    ori['width'] = width

    return ori

# helper function to create initialization features
def create_feature_vector(size):
    # Generate all permutations of indices for two ones in the feature vector
    indices = list(range(size))
    permutations = itertools.permutations(indices, 2)

    # Create feature vectors with two ones at each permutation
    feature_vectors = []
    for perm in permutations:
        vector = [0] * size
        vector[perm[0]] = 1
        vector[perm[1]] = 1
        feature_vectors.append(vector)

    return feature_vectors

# Usage example
# feature_vectors = create_feature_vector(20)
def input_features(feature_vectors, nodelist):
    return feature_vectors[:len(nodelist)]

# compute BFS-ordered nodes
def sorted_list(G):

    # degree centrality
    # degCent = nx.degree_centrality(G)
    # degCent_sorted=dict(sorted(degCent.items(), key=lambda item: item[1],reverse=True))

    # find highest betweenness_centrality
    #Computing betweeness
    betCent = nx.betweenness_centrality(G, normalized=True, endpoints=True)
    #Descending order sorting betweeness
    betCent_sorted=dict(sorted(betCent.items(), key=lambda item: item[1],reverse=True))
    root = list(betCent_sorted)[0]
    # root = 0
    edges = nx.bfs_edges(G, root)
    nodes = [root] + [v for u,v in edges] 
    x_idx = nodes
    x_ridx = sorted(range(len(x_idx)), key=lambda i: x_idx[i])
    return x_idx, x_ridx


# compute normalized coordinates
def norm_coord(nodelist, width, height, x_idx):
    norm_list = []
    for node in nodelist:
        norm_list.append((node[2]/(width - 50), node[3]/(height - 50)))
    norm_arr = np.array(norm_list)
    
    return norm_arr[x_idx,:];


# template for individual file generation
def file_generation(file_id, height, width, file_name):
    G, nodelist, linelist = create_graph(data)
    ori = produce_ori(file_id, nodelist, linelist, height, width)
    feature_vectors = create_feature_vector(49)
    input_feat_list = input_features(feature_vectors, nodelist)
    x_idx, x_ridx = sorted_list(G)
    norm_coord_list = norm_coord(nodelist, width, height, x_idx)

    object = {}
    object["ori"] = ori
    object["x"] = np.array(input_feat_list)
    object["x_idx"] = x_idx
    object["x_ridx"] = x_ridx
    object['pos'] = norm_coord_list
    object['len'] = G.number_of_nodes()
    object['adj'] = nx.to_numpy_array(G)
    object['graph'] = nx.to_dict_of_lists(G)

    with open(file_name, "wb") as f:
        pkl.dump(object, f)

height = 1000
width = 1000
# accept the argument
# output = argv[1]
global_id = 0
for root, dirs, files in os.walk(f"step2"):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        # Do something with the file_path
        new_folder = f"step3"
        with open(file_path, "rb") as f:
            data = json.load(f)   
        stem_name = os.path.splitext(file_name)[0]
        new_file = os.path.join(new_folder, stem_name)
        new_file = new_file + ".pkl"
        file_generation(global_id, height, width, new_file) 
        global_id = global_id + 1

