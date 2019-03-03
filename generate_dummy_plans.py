import xml.etree.ElementTree as ET
import argparse
import math

parser = argparse.ArgumentParser(description='Generate the I-EPOS simulation files')
parser.add_argument('--plans', required=True,
                    help='Input plans file for where people start')
parser.add_argument('--center', nargs=2, type=float, required=True,
                    help='Center location of safe radius (in same units as input file')
parser.add_argument('--radius', type=float, required=True,
                    help='Radius of the safe area cirlce (in same units as input file)')
parser.add_argument('--output', default='input/dummy_plans.xml',
                    help='Dummy plans file to save to')
args = parser.parse_args()


center = (args.center[0], args.center[1])
radius = args.radius
print('Using center location of {}, {}'.format(center[0], center[1]))
print('Using radius of {}'.format(radius))

print('Importing source plans file...')
plans_tree = ET.parse(args.plans)

pop_elm = plans_tree.getroot()
pop_attrib = pop_elm.findall('attributes')

print('Filtering people and activities...')
# Process all of the person elements
kept_people = []
total_people = 0
for person in pop_elm.findall('person'):
    total_people += 1
    if 'freight' not in person.attrib['id']:
        # Check if this persons starting location is within the radius
        # 1pct file only has one plan for each person
        dist = math.sqrt(
                (float(person[0][0].attrib['x'])-center[0])**2 +
                (float(person[0][0].attrib['y'])-center[1])**2)
        if dist <= radius:
            start_activity = person[0][0]
            start_activity.attrib['end_time'] = '00:00:00'
            # Clear out everything except for the start at home
            person[0].clear()
            person[0].append(start_activity)
            kept_people.append(person)

# Clear out everything and only add the relevant people back in
# because it's faster
pop_elm.clear()
for attr in pop_attrib:
    pop_elm.append(attr)
for person in kept_people:
    pop_elm.append(person)

print('Completed parsing of plans file')
print('{} persons remain out of {}'.format(len(kept_people), total_people))

print('Saving new dummy plans file...')
with open(args.output, 'wb') as f:
    f.write('<?xml version="1.0" encoding="utf-8"?>\n'.encode('utf8'))
    f.write('<!DOCTYPE population SYSTEM "http://www.matsim.org/files/dtd/population_v6.dtd">'.encode('utf8'))
    plans_tree.write(f, encoding='utf8', xml_declaration=False)
