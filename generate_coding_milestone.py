from enum import Enum   
from shutil import copyfile
from shutil import rmtree

import json
import os

class LineStatus(Enum):
    same = "same"
    add = "add"
    delete = "delete"

def file_to_lines(filename):
    with open(filename) as f:
        return f.readlines() 

def file_to_string(filename):
    with open(filename) as f:
        return f.read()         

def lines_to_file(filename, lines):
    with open(filename, 'w') as f:
        for line in lines:
            f.write(line)

def diff_lines_to_file(base_html, diff_title, subtitle, milestone_name, filename, lines):    
    prev_line_status = None
    with open(filename, 'w') as f:
        f.write(base_html)
        f.write(("<h2>" + diff_title + "</h2>") % milestone_name)
        f.write("<h3>" + subtitle + "</h3>")
        for line in lines:
            line_status = line[1]
            if line_status != prev_line_status:
                if prev_line_status != None:
                    f.write("</code></pre>\n")
                f.write("<pre><code class='python code_%s'>\n" % line_status.value)
            f.write(line[0])
            prev_line_status = line_status
        f.write("</code></pre>\n")            
            

def get_match_condition(match_comment):
    return match_comment[1:].strip()

def get_match_index(lines, match_condition):
    if match_condition == "":
        return -1
    idx = 0
    for line in lines:
        if line.strip().startswith(match_condition):
            return idx
        idx += 1
    return idx

def transform(sources, diff, snippet_file):
    snippet = file_to_lines(snippet_file)
    assert(snippet[0].startswith("# BEGINMATCH"))
    begin_match = get_match_condition(snippet[1])
    assert(snippet[2].startswith("# ENDMATCH"))
    end_match = get_match_condition(snippet[3])
    
    begin_idx = get_match_index(sources, begin_match)
    end_idx = begin_idx - 1 if end_match == "INSERT" else get_match_index(sources, end_match)
    #print(begin_idx)
    #print(end_idx)
    if begin_idx >= len(sources):
        sources.append("")
    sources[(end_idx+1):(end_idx+1)] = snippet[4:]
    sources[begin_idx:(end_idx+1)] = []

    begin_idx = get_match_index([x[0] for x in diff], begin_match)
    end_idx = begin_idx - 1 if end_match == "INSERT" else get_match_index([x[0] for x in diff], end_match)
    if begin_idx >= len(diff):
        diff.append(("", LineStatus.add))
        diff[(end_idx+1):(end_idx+1)] = [(x, LineStatus.add) for x in snippet[4:]]
    else:
        diff[(end_idx+1):(end_idx+1)] = [(x, LineStatus.add) for x in snippet[4:]]
        diff[begin_idx:(end_idx+1)] = [(l[0], LineStatus.delete) for l in diff[begin_idx:(end_idx+1)]]

    return (sources, diff)

def generate_milestone(folder, prev_dest, milestone, diff_title):
    if not os.path.exists(folder):
        os.makedirs(folder)
    source_folder = folder + "-Sources"        
    if 'source' in milestone:
        source = source_folder + "/" + milestone['source']
    else:
        source = prev_dest
    source = file_to_lines(source)
    diff = [(x, LineStatus.same) for x in source]
    dest_file = folder + "/" + milestone['name']
    diff_dest_file = folder + "/" + milestone['name'].replace(".py", "_diff.html")

    if 'snippets' in milestone:
        for snippet in milestone['snippets']:
            snippet_file = source_folder + "/" + snippet
            if os.path.exists(snippet_file):
                (source, diff) = transform(source, diff, snippet_file)
    lines_to_file(dest_file, source)
    diff_lines_to_file(file_to_string(source_folder + "/base_diff.html"), diff_title, milestone['subtitle'], milestone['name'], diff_dest_file, diff)    
    return dest_file

with open('config.json') as f:
    config = json.load(f)

prev_dest = None
rmtree(config['folder'])
for milestone in config['milestones']:
    print("Generate milestone for", milestone['name'])
    dest_file = generate_milestone(config['folder'], prev_dest, milestone, config['diff_title'])
    prev_dest = dest_file
for file in config['files_to_copy']:
    folder = config['folder']
    source_folder = folder + "-Sources"
    copyfile(source_folder + "/" + file, folder + "/" + file)
    print("Copy file", file)
