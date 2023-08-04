from pygmlparser.Parser import Parser
from pygmlparser.Graph import Graph
from pygmlparser.Edge import Edge
from pygmlparser.Node import Node
from pygmlparser.graphics.NodeGraphics import NodeGraphics
from pygmlparser.graphics.EdgeGraphics import EdgeGraphics
from pygmlparser.graphics.Point import Point
import json
from pathlib import Path
import re
import codecs
import sys

data = sys.argv[1]
parser: Parser = Parser()
parser.loadGML(data)
parser.parse()

# Retrieve the graph nodes 
nodes: Graph.Nodes = parser.graph.graphNodes  # a map of id -> Node objects

# Retrieve the graph edges
edges: Graph.Edges = parser.graph.graphEdges  # list of Edge objects


# Write the graph structure as txt

output = {}
output["nodes"] = []
for i in range(len(nodes)):
    node = nodes[i]
    dictionary = {}
    dictionary["id"] = node.id
    # res_str = re.sub("&#45;", "-", node.label) 
    # dictionary["label"] = res_str
    dictionary["x"] = node.graphics.x
    dictionary["y"] = node.graphics.y
    dictionary["w"] = node.graphics.w
    dictionary["h"] = node.graphics.h
    output["nodes"].append(dictionary)

output["edges"] = []
for i in range(len(edges)):
    edge = edges[i]
    dictionary = {}
    dictionary["source"] = edge.source
    dictionary["target"] = edge.target
    dictionary["arrow"]  = edge.graphics.arrow
    path = edge.graphics.line
    dictionary["path"] = []
    for point in path:
        dictionary["path"].append([point.x, point.y])
    output["edges"].append(dictionary)

json_object = json.dumps(output, indent=4, ensure_ascii=False)
stem = Path(data).stem
# Writing to sample.json
with codecs.open(f"{stem}.json", "w+", "utf-8") as outfile:
    outfile.write(json_object)
