#!/usr/bin/env python

import socket
import os, os.path
import sys
import re
import optparse

colors = {
    "reset":"\033[m",
    "normal":"\033[0m",
    "dark":"\033[2m",
    "red":"\033[0;31m",
    "dark_red":"\033[2;31m",
    "green":"\033[0;32m",
    "dark_green":"\033[2;32m",
    "yellow":"\033[0;33m",
    "dark_yellow":"\033[2;33m",
    "blue":"\033[0;34m",
    "dark_blue":"\033[2;34m",
    "magenta":"\033[0;35m",
    "dark_magenta":"\033[2;35m",
    "cyan":"\033[0;36m",
    "dark_cyan":"\033[2;36m",
    "white":"\033[0;37m",
    "dark_white":"\033[0;37m"
}
sock_path = "/var/run/lockdown/syslog.sock"
line_regex = "(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+|)\s+(\w+)\[(\d+)\]\s+\<(\w+)\>:\s(.*)"

prog = re.compile(line_regex)

def msgColorsForType(msg_type):
    if msg_type == "Notice":
        return (colors['green'],colors['dark_green'])
    elif msg_type == "Warning":
        return (colors['yellow'],colors['dark_yellow'])
    elif msg_type == "Error":
        return (colors['red'],colors['dark_red'])
    elif msg_type == "Debug":
        return (colors['red'],colors['dark_red'])
    return (colors['white'],colors['dark_white'])

def startSyslog(process_filter="all"):
    print("[*] Connecting...")
    if process_filter != "all":
        filtered_processes = [proc_name.strip() for proc_name in process_filter.split(',')]
    if os.path.exists(sock_path):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(sock_path)
        print("[*] Ready")
        print("[*] Press CTRL+C to quit.")
        client.send("watch\n") #tells syslog sock to start sending stuff
        while True:
            try:
                line = client.recv(1024)
                result = prog.match(line)
                if result != None:
                    groups = result.groups()
                    if len(groups) == 6:
                        (date, device_name, process_name, process_id, msg_type, msg) = groups
                        if process_filter != "all" and process_name not in filtered_processes:
                                continue
                        output_line = colors["dark_white"] + str(date) + " " #append colored date
                        output_line += str(device_name) + " " #append device name
                        output_line += colors["cyan"] + str(process_name) + "[%s]" % (str(process_id)) #append process_name[process_id]
                        msg_colors = msgColorsForType(msg_type)
                        output_line += msg_colors[1] + " <" + msg_colors[0] + msg_type + msg_colors[1] + "> " #append msg type
                        output_line += colors['dark_white'] + msg + "\n" #append message
                        print(output_line)
            except KeyboardInterrupt, k:
                print(colors['reset'] + "\n[!] Shutting down.")
                client.close()
                break
    else:
        print("[!] Could not connect to syslog.")
        sys.exit()
        print(colors['reset'] + "[*] Done")

parser = optparse.OptionParser()
parser.add_option('-p', '--process', dest="process", help="filter out this process name", default="all")
options, args = parser.parse_args()
startSyslog(options.process)
