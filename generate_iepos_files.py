import xml.etree.ElementTree as ET
import argparse
import math
import heapdict
import os
import pdb

parser = argparse.ArgumentParser(description='Generate the I-EPOS simulation files')
parser.add_argument('--network', required=True,
                    help='Network file for evacuation scenario')
parser.add_argument('--plans', required=True,
                    help='Input plans file for where people start')
parser.add_argument('--center', nargs=2, type=float, required=True,
                    help='Center location of safe radius (in same units as input file')
parser.add_argument('--radius', type=float, required=True,
                    help='Radius of the safe area cirlce (in same units as input file)')
parser.add_argument('--output_mapping', default='input/agent_mapping.csv',
                    help='Output file for mapping between epos person id and matsim person id')
parser.add_argument('--target_file', default='input/epos/optimal.target')
parser.add_argument('--agents_folder', default='input/epos/')
parser.add_argument('--scale', type=float, default=1.0,
                    help='Scale factor to apply to EPOS local costs. 1/scale')

args = parser.parse_args()
center = (args.center[0], args.center[1])
radius = args.radius
print('Using center location of {}, {}'.format(center[0], center[1]))
print('Using radius of {}'.format(radius))

print('Importing road network...')
network_tree = ET.parse(args.network)

class Neighbor:
    def __init__(self, neighbor_id, distance):
        self.neighbor_id = neighbor_id
        self.distance = distance

class Node:
    def __init__(self, node_id, neighbors=[]):
        self.node_id = node_id
        self.neighbors = neighbors
        self.previous = None
        self.distances = {}

exit_nodes = {}
all_nodes = {}
for node in network_tree.getroot().find('nodes'):
    node_id = node.attrib['id']
    all_nodes[node_id] = Node(node_id)
    if 'en' in node_id:
        exit_nodes[node_id] = 0
num_exit_nodes = len(exit_nodes)

all_links = {}
neighbors = {}
capacities = [0 for i in range(num_exit_nodes)]
for link in network_tree.getroot().find('links'):
    from_id = link.attrib['from']
    to_id = link.attrib['to']
    dist = float(link.attrib['length'])
    all_nodes[from_id].neighbors.append(Neighbor(to_id, dist))
    all_links[link.attrib['id']] = (from_id, to_id)
    if to_id not in neighbors:
        neighbors[to_id] = []
    # Reverse the link direction b/c we are traveling through backwards
    neighbors[to_id].append((from_id, dist))
    if 'en' in to_id:
        exit_id = int(to_id.split('en')[1])
        capacities[exit_id-1] = float(link.attrib['capacity'])

# Run Dijkstra's algorithm from every exit node to every node in the graph
all_dists = {}  # Using dictionaries instead of class containers is way faster
previous_node = {}
for exit_node_id in exit_nodes.keys():
    print('Calculating distances to exit node {}'.format(exit_node_id))
    # Intiialize the open and closed sets
    import os

    visited = {}  # Use dictionaries because it is much faster than searching a list
    unvisited = heapdict.heapdict() # Really fast priority heap with in-tree modification
    for node_id in all_nodes.keys():
        unvisited[node_id] = float('Inf')
    unvisited[exit_node_id] = 0

    # Run the algorithm until the unvisited set is empty
    while unvisited:
        # Get the min cost item from the unvisited set
        (curr_node_id, curr_node_cost) = unvisited.popitem()
        # Mark the current node as evaluated
        visited[curr_node_id] = 0

        if curr_node_id not in neighbors:
            continue

        # Evaluate all the neighbors of the current node
        for neighbor_id, dist in neighbors[curr_node_id]:
            if neighbor_id not in visited:
                # Update the cost only if it is better
                new_cost = curr_node_cost + dist
                if new_cost < unvisited[neighbor_id]:
                    unvisited[neighbor_id] = new_cost
                    if neighbor_id not in all_dists:
                        all_dists[neighbor_id] = {}
                    all_dists[neighbor_id][exit_node_id] = new_cost
                    if neighbor_id not in previous_node:
                        previous_node[neighbor_id] = {}
                    previous_node[neighbor_id][exit_node_id] = curr_node_id


print('Importing dummy plans file...')
plans_tree = ET.parse(args.plans)

print('Calcuting Agent Costs...')
agents_start = {}
agents_costs = {}
for person in plans_tree.getroot().findall('person'):
    agent_id = person.attrib['id']
    agent_start_link = person[0][0].attrib['link']
    # Handle agents starting in a link not in the graph?
    if agent_start_link not in all_links:
        # Just don't add this agent...
        continue
    agents_costs[agent_id] = []
    for i in range(num_exit_nodes):
        exit_id = 'en{}'.format(i+1)
        from_node_id = all_links[agent_start_link][0]
        to_node_id = all_links[agent_start_link][1]
        # Handle the from or to nodes being the exit node
        if 'en' in from_node_id:
            if exit_id not in all_dists[to_node_id]:
                agents_costs[agent_id].append(-1)
                continue
            to_dist = all_dists[to_node_id][exit_id]
            agents_costs[agent_id].append(to_dist/2)
            continue
        if 'en' in to_node_id:
            if exit_id not in all_dists[from_node_id]:
                agents_costs[agent_id].append(-1)
                continue
            from_dist = all_dists[from_node_id][exit_id]
            agents_costs[agent_id].append(from_dist/2)
            continue
        # Handle a disconnected graph
        if (exit_id not in all_dists[from_node_id]) or (exit_id not in all_dists[to_node_id]):
            agents_costs[agent_id].append(-1)
            continue
        from_dist = all_dists[from_node_id][exit_id]
        to_dist = all_dists[to_node_id][exit_id]
        agents_costs[agent_id].append((from_dist+to_dist)/2.0)

# Write out all the agents files
print('Writing out EPOS agent files...')
# Fixup the agents folder path
if not args.agents_folder.endswith('/'):
  args.agents_folder = args.agents_folder + '/'

# Add the folder if it does not exist
if not os.path.exists(args.agents_folder):
    os.makedirs(args.agents_folder)
num_agents = len(agents_costs)
agent_num = 0
agent_mapping = {}
for (agent_id, costs) in agents_costs.items():
    with open(args.agents_folder+'agent_{}.plans'.format(agent_num), 'w') as f:
        ordered_costs_idxs = sorted(range(len(agents_costs[agent_id])), key=lambda k: agents_costs[agent_id][k])
        for i in range(num_exit_nodes):
            cost_idx = ordered_costs_idxs[i]
            cost = agents_costs[agent_id][cost_idx]/args.scale
            if cost < 0:
                continue
            f.write('{}:'.format(cost))
            for j in range(num_exit_nodes):
                if cost_idx==j:
                    f.write('1')
                else:
                    f.write('0')
                if (j+1)<num_exit_nodes:
                    f.write(',')
            f.write('\n')
    agent_mapping[agent_num] = agent_id
    agent_num += 1

print('Writing out closest exit node plan file...')
with open('input/closest.csv', 'w') as f:
    f.write('Run,Iteration')
    for i in range(len(agents_costs)):
        f.write(',agent-{}'.format(i))
    f.write('\n')
    f.write('0,1')
    f.write(',0'*num_agents)
    f.write('\n')

print('Writing out epos->matsim agent mapping file...')
# Write out the mapping between epos and matsim agents
with open(args.output_mapping, 'w') as f:
    for (epos_agent, matsim_agent) in agent_mapping.items():
        f.write('{}, {}\n'.format(epos_agent, matsim_agent))

print('Writing out global target file')
# Check that the path exists to target file, otherwise make it
target_dir = os.path.dirname(args.target_file)
if not os.path.exists(target_dir):
    os.makedirs(target_dir)
with open(args.target_file, 'w') as f:
    total_capacity = sum(capacities)
    for i in range(num_exit_nodes):
        f.write('{}'.format(int(capacities[i]*num_agents/float(total_capacity))))
        if i+1<num_exit_nodes:
            f.write(',')

