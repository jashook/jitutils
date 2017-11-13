#! /usr/bin/env python
################################################################################
################################################################################
#
# Module config_visualizer.py 
#
# Notes:
#
# Script to help visualize the config xml that is grabbed by
# coreclr_config_download.py. Ideally this will help validate that
# a netci.groovy change has expected changes.
#
################################################################################
################################################################################

import argparse
import datetime
import json
import multiprocessing
import os
import re
import subprocess
import sys
import shutil
import tempfile
import threading
import time
import urllib2
import zipfile

from collections import defaultdict


################################################################################
# Argument Parser
################################################################################

description = """Script to help visualize the config xml that is grabbed by
              coreclr_config_download.py. Ideally this will help validate that
              a netci.groovy change has expected changes.
              """

parser = argparse.ArgumentParser(description=description)

parser.add_argument("-output_location", dest="output_location", nargs='?', default=None, help="Location of config.xml files.")
parser.add_argument("-html_location", dest="html_location", nargs='?', default=None, help="Location to write the html visualizer.")

parser.add_argument("--baseline_only", dest="baseline_only", action="store_true", default=False, help="Download the baseline config files only.")
parser.add_argument("--diff_only", dest="diff_only", action="store_true", default=False, help="Download the diff config files only.")
parser.add_argument("--ignore_whitespace_diffs", dest="ignore_whitespace_diffs", action="store_true", default=False, help="Ignore whitespace.")

################################################################################
# Helper Functions
################################################################################

def get_steps_from_config(config_file):
    """ Given a config file's location parse and return the build steps

    Args:
        config_file (str): config file location location
    
    Returns:
        steps ([str]): steps the job will do

    """
    assert os.path.isfile(config_file)

    config_contents = None
    with open(config_file) as file_handle:
        config_contents = file_handle.read()

    ret_value = None

    # This is a flow job. It should not have steps.
    # Just parse out the dsl contents
    if "<dsl>" in config_contents:
        ret_value = config_contents.split("<dsl>")[1].split("</dsl>")[0].strip()

    else:
        split = config_contents.split("<command>")[1:]

        commands = []

        for item in split:
            commands.append(item.split("</command>")[0].strip())

        ret_value = commands

    return ret_value


def get_all_jobs(output_location):
    """ Given an output location return a list of all the config xml files

    Args:
        output_location (str): output location for config xml files
    
    Returns:
        config_files ([str]): locations of the config xml files

    """
    assert os.path.isdir(output_location)

    files = os.listdir(output_location)

    return [os.path.join(output_location, item) for item in files]

def write_out_config_visualizer(flow_contents, contents, html_location, diff_flow_contents=None, diff_contents=None, ignore_whitespace_diffs=False):
    do_diff = diff_contents is not None

    if diff_contents is None:
        diff_contents = contents
    
    if diff_flow_contents is None:
        diff_flow_contents = flow_contents

    def get_flow_html():
        elements = []
        ordered_diff_flow_contents = diff_flow_contents.keys()
        ordered_diff_flow_contents.sort()
        for item in ordered_diff_flow_contents:
            item_name = item

            if do_diff is True:
                diff_flow_dsl = diff_flow_contents[item]
                flow_dsl = flow_contents[item]

                if diff_flow_dsl is None:
                    # removed continue
                    continue
                elif flow_dsl is None:
                    item_name = "%s (New)" % item_name

                if diff_flow_dsl is not None and flow_dsl is not None:
                    if flow_dsl == diff_flow_dsl:
                        continue
                    elif ignore_whitespace_diffs is True:
                        flow_dsl_whitespace_removed = flow_dsl.replace(" ", "")
                        diff_flow_dsl_whitespace_removed = diff_flow_dsl.replace(" ", "")

                        if flow_dsl_whitespace_removed == diff_flow_dsl_whitespace_removed:
                            continue
                    else:
                        # There is a diff.
                        item_name = "%s (Diff)" % item_name
                        diff_flow_contents[item] = "Base:\n" + flow_dsl + "\n---------------------------------------------------------------------------\n\nDiff:\n" + diff_flow_dsl

            elements.append("""<li>
      	<div data-role="inner1" class="ui-content">
      	<div data-role="collapsible">
        	<h4>%s</h4>
      		<ul data-role="listview">
            	<li><pre>%s</pre></li>
            </ul>
        </div>
      </li>""" % (item_name, diff_flow_contents[item]))

        return len(elements), "\n".join(elements)

    def get_contents_html():
        elements = []
        ordered_diff_contents = diff_contents.keys()
        ordered_diff_contents.sort()

        for item in diff_contents:
            item_name = item

            if do_diff is True:
                base_steps = contents[item]
                diff_steps = diff_contents[item]

                if base_steps is not None and diff_steps is not None:
                    if len(base_steps) == len(diff_steps):
                        same = True
                        for index, inner_item in enumerate(base_steps):
                            if ignore_whitespace_diffs is True:
                                inner_item_wi = inner_item.replace(" ", "")
                                diff_steps_wi = diff_steps[index].replace(" ", "")

                                if inner_item_wi == diff_steps_wi:
                                    continue

                            if inner_item != diff_steps[index]:
                                same = False
                                item_name = "%s (Diff)" % item_name

                                diff_contents[item] = ["Base:"] + base_steps + ["---------------------------------------------------------------------------", "", "Diff:"] + diff_steps

                                break
                        
                        if same:
                            continue

                elif diff_steps is None:
                    # This is most likely a removed job.
                    # Skip
                    continue
                else:
                    # This is most likely a new job.
                    # Add that info to the name
                    item_name = "%s (New)" % item_name
                
            elements.append("""<li>
      	<div data-role="inner1" class="ui-content">
      	<div data-role="collapsible">
        	<h4>%s</h4>
      		<ul data-role="listview">
            	<li><pre>%s</pre></li>
            </ul>
        </div>
      </li>""" % (item_name, "\n".join(diff_contents[item])))

        return len(elements), "\n".join(elements)
    
    flow_count, flow_html = get_flow_html()
    count, contents_html = get_contents_html()


    start_html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css">
<script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
<script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
</head>
<body>

<div data-role="page" id="pageone">
  <div data-role="header">
    <h1>Config Visualizer</h1>
  </div>

  <div data-role="main" class="ui-content">
    <div data-role="collapsible">
    <h4>Flow Jobs (%d)</h4>
    <ul data-role="listview">
      %s
    </ul>
    </div>

    <div data-role="collapsible">
    <h4>Non Flow Jobs (%d)</h4>
    <ul data-role="listview">
       %s
    </ul>
    </div>
  </div>

</div> 

</body>
</html>""" % (flow_count, flow_html, count, contents_html)

    with open(html_location, 'w') as file_handle:
        file_handle.write(start_html)


def main(args):
    output_location = args.output_location
    html_location = args.html_location

    baseline_only = args.baseline_only
    diff_only = args.diff_only
    ignore_whitespace_diffs = args.ignore_whitespace_diffs

    diff_location = None

    if diff_only:
        output_location = os.path.join(output_location, "diff")
    elif baseline_only:
        output_location = os.path.join(output_location, "base")
    else:
        diff_location = os.path.join(output_location, "diff")
        output_location = os.path.join(output_location, "base")

    config_files = get_all_jobs(output_location)
    diff_config_files = None

    if diff_location is not None:
        diff_config_files = get_all_jobs(diff_location)

    flow_contents = defaultdict(lambda: None)
    contents = defaultdict(lambda: None)

    diff_flow_contents = defaultdict(lambda: None)
    diff_contents = defaultdict(lambda: None)

    for config_file in config_files:
        item = get_steps_from_config(config_file)

        config_file = os.path.basename(config_file)

        if isinstance(item, list):
            contents[config_file] = item
        else:
            flow_contents[config_file] = item

    for config_file in diff_config_files:
        if "arm64" in config_file and "windows" in config_file and "flow" in config_file:
            pass

        item = get_steps_from_config(config_file)

        config_file = os.path.basename(config_file)

        if isinstance(item, list):
            diff_contents[config_file] = item
        else:
            diff_flow_contents[config_file] = item

    if diff_location is None:
        write_out_config_visualizer(flow_contents, contents, html_location)
    else:
        write_out_config_visualizer(flow_contents, contents, html_location, diff_flow_contents=diff_flow_contents, diff_contents=diff_contents, ignore_whitespace_diffs=ignore_whitespace_diffs)

################################################################################
# __main__ (entry point)
################################################################################

if __name__ == "__main__":
   main(parser.parse_args(sys.argv[1:]))