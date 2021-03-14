import json
import os

def file_to_string(filename):
    with open(filename) as f:
        return f.read() 

def string_to_file(filename, s):
    with open(filename, 'w') as f:
        f.write(s)

def generate_milestone(folder, milestone):
    if not os.path.exists(folder):
        os.makedirs(folder)
    source = folder + "-Sources/" + milestone['source']
    source_file = file_to_string(source)
    dest_file = folder + "/" + milestone['name']
    string_to_file(dest_file, source_file)

with open('config.json') as f:
    config = json.load(f)

for milestone in config['milestones']:
    generate_milestone(config['folder'], milestone)