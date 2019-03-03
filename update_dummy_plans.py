import xml.etree.ElementTree as ET
import argparse
import math
import csv


parser = argparse.ArgumentParser(description='Generate Matsim plans')
parser.add_argument('--plans', default='input/dummy_plans.xml')
parser.add_argument('--epos_plans',default='input/selected-plans.csv')
parser.add_argument('--mapping',default='input/agent_mapping.csv')
parser.add_argument('--network', default='input/evacuation_network.xml')
parser.add_argument('--output',default='input/updated_plans.xml')
parser.add_argument('--agents_folder',default='input/epos/',
                    help='Folder for EPOS agents and their plans')

args = parser.parse_args()
plans_tree = ET.parse(args.plans)
network_tree = ET.parse(args.network)

epos_file = open(args.epos_plans,'r')
agent_mapping = open(args.mapping,'r')

# Fixup the agents plans file path
if not args.agents_folder.endswith('/'):
  args.agents_folder = args.agents_folder + '/'

# Assume the default agent prefix
epos_agent_fmt_string = 'agent_{}.plans'

class NodeContainer:
    def __init__(self, node_id, x, y, element):
        self.node_id = node_id
        self.x = float(x)
        self.y = float(y)
        self.element = element

# Process all the nodes and store data in containers
all_nodes = {}
nodes_elm = network_tree.getroot().find('nodes')
for node in nodes_elm:
    all_nodes[node.attrib['id']] = NodeContainer(node.attrib['id'],
                                     node.attrib['x'],
                                     node.attrib['y'],
                                     node)

#Get updated plans
for row in reversed(list(csv.reader(epos_file))):
    epos_plans = row
    break

#Dictionary agents name: exit nodes
new_plans = {}
i = 1
for row in list(csv.reader(agent_mapping)):
    agent_matsim_id = row[1].strip()
    agent_epos_id = int(row[0].strip())
    selected_trimmed_plan = int(epos_plans[i+1])
    selected_exit = -1
    with open(args.agents_folder+epos_agent_fmt_string.format(agent_epos_id), 'r') as f:
      lines = f.readlines()
      selected_exit = lines[selected_trimmed_plan].strip().split(':')[1].split(',').index('1') + 1
    assert (selected_exit!=-1), 'Could not find selected exit node'

    new_plans[agent_matsim_id]='en{}'.format(selected_exit)
    i+=1

elm = plans_tree.getroot()

print('Adding post-evac activity...')
#Update Plans
for person in elm.findall('person'):
    person[0].attrib['score']='0.0'
    person[0].attrib['selected']='yes'
    leg = ET.SubElement(person[0],'leg')
    leg.attrib['mode']='car'
    activity = ET.SubElement(person[0],'activity')
    activity.attrib['type']='post-evac'
    personid = person.attrib['id']
    if personid not in new_plans:
        elm.remove(person)
        continue
    link = new_plans[personid]
    activity.attrib['link']=link
    activity.attrib['x']=str(all_nodes[link].x)
    activity.attrib['y']=str(all_nodes[link].y)
    activity.attrib['end_time']='00:00:00'


with open(args.output, 'wb') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf8'))
    f.write('<!DOCTYPE population SYSTEM "http://www.matsim.org/files/dtd/population_v6.dtd">'.encode('utf8'))
    plans_tree.write(f, encoding='utf8', xml_declaration=False)
