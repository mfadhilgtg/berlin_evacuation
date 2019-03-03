import xml.etree.ElementTree as ET
import argparse
import math
import queue
from copy import deepcopy
import pdb

parser = argparse.ArgumentParser(description='Generate the evacuation network')
parser.add_argument('--network', required=True,
                    help='Network file with path to parse')
parser.add_argument('--center', nargs=2, type=float, required=True,
                    help='Center location of safe radius (in same units as input file')
parser.add_argument('--radius', type=float, required=True,
                    help='Radius of the safe area cirlce (in same units as input file)')
parser.add_argument('--output_network', default='input/evacuation_network.xml',
                    help='Output file for the network')
parser.add_argument('--output_matsim_network', default='input/evacuation_matsim_network.xml',
                    help='Output file for the matsim network')
args = parser.parse_args()

center = (args.center[0], args.center[1])
radius = args.radius
print('Using center of location {}, {}'.format(center[0], center[1]))
print('Using radius of {}'.format(radius))

print('Importing road network...')
network_tree = ET.parse(args.network)

print('Parsing road network...')

# Make some simple containers for easier indexing
class NodeContainer:
    def __init__(self, node_id, x, y, element):
        self.node_id = node_id
        self.x = float(x)
        self.y = float(y)
        self.element = element

class LinkContainer:
    def __init__(self, link_id, from_id, to_id, element):
        self.link_id = link_id
        self.from_id = from_id
        self.to_id = to_id
        self.element = element

# Process all the nodes and store data in containers
all_nodes = {}
mark_add_nodes = {}
nodes_elm = network_tree.getroot().find('nodes')
for node in nodes_elm:
    all_nodes[node.attrib['id']] = NodeContainer(node.attrib['id'],
                                     node.attrib['x'],
                                     node.attrib['y'],
                                     node)

all_edges = {}
links_elm = network_tree.getroot().find('links')
for link in links_elm:
    if 'car' in link.attrib['modes']:
        all_edges[link.attrib['id']] = LinkContainer(
                                         link.attrib['id'],
                                         link.attrib['from'],
                                         link.attrib['to'],
                                         link)

def add_to_neighbors(n, to_id, from_id):
    if from_id not in n:
        n[from_id] = [to_id]
    elif to_id not in n[from_id]:
        n[from_id].append(to_id)
    # Create bi-directional neighbors from unidirectional link
    if to_id not in n:
        n[to_id] = [from_id]
    elif from_id not in n[to_id]:
        n[to_id].append(from_id)


# Cut the network based on proximity from the center
mark_exit = {}  # construct an empty 'set'
mark_add_links = {}
neighbors = {}
for link_id, vals in all_edges.items():
    from_cnt = all_nodes[vals.from_id]
    to_cnt = all_nodes[vals.to_id]
    link_cnt = vals

    from_dist = math.sqrt((from_cnt.x-center[0])**2 +
                        (from_cnt.y-center[1])**2)
    to_dist = math.sqrt((to_cnt.x-center[0])**2 +
                        (to_cnt.y-center[1])**2)
    if from_dist <= radius and to_dist > radius:
        # Road leads out of the safe area. Keep the link, and mark
        # the to node an exit node
        mark_add_links[link_cnt.link_id] = 0
        mark_add_nodes[vals.from_id] = 0
        mark_add_nodes[vals.to_id] = 0
        mark_exit[vals.to_id] = 0
        # Add link information to neighbor information
        add_to_neighbors(neighbors, vals.to_id, vals.from_id)
    elif to_dist <= radius and from_dist > radius:
        # Road leads out of the safe area. Keep the link, and mark
        # the to node an exit node
        mark_add_links[link_cnt.link_id] = 0
        mark_add_nodes[vals.from_id] = 0
        mark_add_nodes[vals.to_id] = 0
        mark_exit[vals.from_id] = 0
        # Add link information to neighbor information
        add_to_neighbors(neighbors, vals.to_id, vals.from_id)
    elif from_dist <= radius and to_dist <= radius:
        # Both points are inside the safe area, so keep them
        mark_add_links[link_cnt.link_id] = 0
        mark_add_nodes[vals.from_id] = 0
        mark_add_nodes[vals.to_id] = 0
        # Add link information to neighbor information
        add_to_neighbors(neighbors, vals.to_id, vals.from_id)

# "Color" the graph for detection of disconnected subgraphs
curr_color_id = -1
color_counts = []
uncolored = dict(mark_add_nodes)
colors = {}
# Loop until all nodes have been colored
while uncolored:
  curr_color_id += 1
  color_counts.append(0)
  # pick a "random" node from the list
  node_id = list(uncolored.keys())[0]
  curr_neighbors = queue.Queue()
  curr_neighbors.put(node_id)
  in_queue = {node_id: 0}  # Because queue doesn't have an in operation
  #Run BFS until all neighbors have been reached
  while not curr_neighbors.empty():
    # Get the next node to process in the BFS tree
    temp_id = curr_neighbors.get()
    assert (temp_id in mark_add_nodes), "Found an element not in the list of nodes to add"
    # Any item in the colored list should not be processed again
    if temp_id in colors:
      assert (colors[temp_id]==curr_color_id), "Processing item {} already colored as {}".format(temp_id,colors[temp_id])
    # Color the current neighbor in the tree
    uncolored.pop(temp_id)
    in_queue.pop(temp_id)
    colors[temp_id] = curr_color_id
    color_counts[curr_color_id] += 1

    # Add any of this node's neighbors to the tree
    for n_id in neighbors[temp_id]:
      assert (n_id in mark_add_nodes), "Attempting to add a neighbor not inside the cut network"
      if n_id in colors:
        assert (colors[n_id]==curr_color_id), "Processing item {} already colored as {}".format(temp_id,colors[temp_id])
      # Prevent loops in the 'tree'
      if n_id not in colors and n_id not in in_queue:
        curr_neighbors.put(n_id)
        in_queue[n_id] = 0

assert (len(uncolored)==0), "Uncolored list not empty"
assert (sum(color_counts)==len(mark_add_nodes)), "Color counts != Number of nodes"
assert (len(colors)==len(mark_add_nodes)), "Size of colors != number of nodes"

# Select the color with the most nodes
print('Subgraphs: ')
print(color_counts)
max_subgraph_id = color_counts.index(max(color_counts))

# Remove the nodes not in the biggest subgraph
for node_id, color_id in colors.items():
    if color_id == max_subgraph_id:
        continue
    # Remove from the list of marked nodes
    mark_add_nodes.pop(node_id,None)
    mark_exit.pop(node_id,None)  # One-liner to remove if it exists

# Remove the links not in the biggest subgraph
mark_add_links = {link_id:0 for link_id,val in all_edges.items() if
                     (link_id in mark_add_links) and
                     (val.from_id in mark_add_nodes) and
                     (val.to_id in mark_add_nodes)}

# Update the exit node number for each marked exit node
curr_exit_node = 1
for key, val in mark_exit.items():
    mark_exit[key] = curr_exit_node
    curr_exit_node += 1

# Go through and update the names of the exit nodes in the links
for link in links_elm:
    if link.attrib['to'] in mark_exit:
        link.attrib['to'] = 'en{}'.format(mark_exit[link.attrib['to']])
    if link.attrib['from'] in mark_exit:
        link.attrib['from'] = 'en{}'.format(mark_exit[link.attrib['from']])

# Go through and update the names of the exit nodes in the node list
for node in nodes_elm:
    if node.attrib['id'] in mark_exit:
        node.attrib['id'] = 'en{}'.format(mark_exit[node.attrib['id']])

# Clear the node list and only add back the necessary ones
# This is faster than removing elements for large lists (prevents O(n) search over list)
attr_copy = nodes_elm.attrib
nodes_elm.clear()
for k,v in attr_copy.items(): # Reset the attributes after the clear
    nodes_elm.set(k,v)
for node_id in mark_add_nodes.keys():
    nodes_elm.append(all_nodes[node_id].element)

# Clear the link list and only add back the necessary ones
# This is faster than removing elements for large lists (prevents O(n) search over list)
# Output the network to a different file for getting MATSIM to work properly.
attr_copy = links_elm.attrib
links_elm.clear()
for k,v in attr_copy.items(): # Reset the attributes after the clear
    links_elm.set(k,v)
for link_id in mark_add_links.keys():
    links_elm.append(all_edges[link_id].element)


print('Completed parsing of network file')
print('{} nodes out of {} were inside the radius'.format(len(mark_add_nodes), len(all_nodes)))
print('{} exit nodes were generated'.format(len(mark_exit)))

print('Saving new evacuation network file...')
with open(args.output_network, 'wb') as f:
    # Required so that the header is parsed correctly by Matsim and Via
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf8'))
    f.write('<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v2.dtd">\n'.encode('utf8'))
    network_tree.write(f, encoding='utf8', xml_declaration=False)

# ====== OUTPUT for MATSIM Only ======
# Clear the node list and only add back the necessary ones
# This is faster than removing elements for large lists (prevents O(n) search over list)
attr_copy = nodes_elm.attrib
nodes_elm.clear()
for k,v in attr_copy.items(): # Reset the attributes after the clear
    nodes_elm.set(k,v)
for node_id in all_nodes.keys():
    nodes_elm.append(all_nodes[node_id].element)

# Clear the link list and only add back the necessary ones
# This is faster than removing elements for large lists (prevents O(n) search over list)
attr_copy = links_elm.attrib
links_elm.clear()
for k,v in attr_copy.items(): # Reset the attributes after the clear
    links_elm.set(k,v)
for link_id in all_edges.keys():
    links_elm.append(all_edges[link_id].element)

with open(args.output_matsim_network, 'wb') as f:
    # Required so that the header is parsed correctly by Matsim and Via
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf8'))
    f.write('<!DOCTYPE network SYSTEM "http://www.matsim.org/files/dtd/network_v2.dtd">\n'.encode('utf8'))
    network_tree.write(f, encoding='utf8', xml_declaration=False)
