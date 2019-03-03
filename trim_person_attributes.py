import xml.etree.ElementTree as ET
import argparse

parser = argparse.ArgumentParser(description='Trim population data to just people')
parser.add_argument('--attr_file', required=True,
                    help='Person Attributes file to trim')
parser.add_argument('--output', default='input/person_attributes.xml',
                    help='Output file')
args = parser.parse_args()

print('Importing Person Attributes file..')
person_tree = ET.parse(args.attr_file)

# Copy in all the objects
objects_elm = person_tree.getroot()
kept_elms = []
for person in objects_elm:
    if 'freight' not in person.attrib['id']:
        kept_elms.append(person)

print('Clearing list and re-adding elements..')
# Clear out the list because clearing and adding is faster
objects_elm.clear()
for person_elm in kept_elms:
    objects_elm.append(person_elm)


print('Saving new person attributes file...')
# Write the tree out to disk
with open(args.output, 'wb') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n'.encode('utf8'))
    f.write('<!DOCTYPE objectAttributes SYSTEM "http://matsim.org/files/dtd/objectattributes_v1.dtd">\n'.encode('utf8'))
    person_tree.write(f, encoding='utf8', xml_declaration=False)
