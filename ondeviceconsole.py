#!/usr/bin/env python

import ConfigParser
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

default_colors = {
    'date_color': 'white',
    'device_name_color': 'blue',
    'process_color': 'cyan',
    'msg_color': 'dark_white',
    'highlight_color': 'magenta'
}

config_path = "/var/preferences/ondeviceconsole.cfg"
color_config = ConfigParser.SafeConfigParser(default_colors)

regex = re.compile(line_regex,re.MULTILINE)

def colorStringForColorConfig(conf_value):
    color_setting = color_config.get('Colors', conf_value)
    if color_setting in colors:
        return colors[color_setting]
    return colors['white']

def loadConfig():
    if os.path.exists(config_path) == False:
        color_config.add_section('Colors')
        for key in default_colors:
            color_config.set('Colors', key, default_colors[key])
        with open(config_path, 'wb') as configfile:
            color_config.write(configfile)
            configfile.close()
    else:
        color_config.read(config_path)

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

def startSyslog(process_filter="all",highlights=None):
    print("[*] Connecting...")
    if process_filter != "all":
        filtered_processes = [proc_name.strip() for proc_name in process_filter.split(',')]
    if highlights != None:
        highlights = [hl.strip() for hl in highlights.split(',')]
    if os.path.exists(sock_path):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(sock_path)
        print("[*] Ready")
        print("[*] Press CTRL+C to quit.")
        client.send("watch\n") #tells syslog sock to start sending stuff
        while True:
            try:
                line = client.recv(1024)
                result = regex.match(line)
                if result != None:
                    groups = result.groups()
                    if len(groups) == 6:
                        (date, device_name, process_name, process_id, msg_type, msg) = groups
                        if process_filter != "all" and (process_name not in filtered_processes and process_id not in filtered_processes):
                                continue
                        output_line = colorStringForColorConfig('date_color') + str(date) + " " #append colored date
                        output_line += colorStringForColorConfig('device_name_color') + str(device_name) + " " #append device name
                        output_line += colorStringForColorConfig('process_color') + str(process_name) + "[%s]" % (str(process_id)) #append process_name[process_id]
                        msg_colors = msgColorsForType(msg_type)
                        output_line += msg_colors[1] + " <" + msg_colors[0] + msg_type + msg_colors[1] + "> " #append msg type
                        if highlights != None:
                            for hl in highlights:
                                msg = msg.replace(hl,colorStringForColorConfig('highlight_color') + hl + colorStringForColorConfig('msg_color'))
                        output_line += colorStringForColorConfig('msg_color') + msg + "\n" #append message
                        print(output_line)
            except KeyboardInterrupt, k:
                print(colors['reset'] + "\n[!] Shutting down.")
                client.close()
                break
    else:
        print("[!] Could not connect to syslog.")
        print(colors['reset'] + "[*] Done")
        sys.exit()

def color_config_arg(arg_default):
    def func(option,opt_str,value,parser):
        if len(parser.rargs) == 0:
            setattr(parser.values,option.dest,True)
        elif len(parser.rargs) == 1:
            setattr(parser.values,option.dest,parser.rargs[0])
        else:
            setattr(parser.values,option.dest,True)
    return func

def printColorHelp(colors):
    print("Usage: --config-color [options]\n")
    print("Options:")
    print("--config-color IDENTIFIER\n")
    print("Identifiers are: " + ', '.join(colors.keys()))

parser = optparse.OptionParser()
parser.add_option('-p', '--process', dest="process", help="filter out this process name. pass multiple process comma separated", default="all")
parser.add_option('--highlight', dest="highlight", help="highlight certain words. pass multiple comma separated", default=None)
parser.add_option('--config-color',action='callback',callback=color_config_arg(True),dest='config_color', help="configure colors")
options, args = parser.parse_args()
loadConfig() #load config
if options.config_color == True:
    printColorHelp(default_colors)
elif options.config_color != None:
    if options.config_color in default_colors:
        new_color = str(raw_input("Enter new color name: "))
        if new_color in colors:
            color_config.set('Colors', options.config_color, new_color)
            with open(config_path, 'wb') as configfile:
                color_config.write(configfile)
                configfile.close()
            print("[*] New color set!")
            sys.exit()
        else:
            print("[!] Invalid value, please choose from " + ', '.join(colors.keys()))
            sys.exit()
    else:
        printColorHelp(default_colors)
else:
    startSyslog(options.process,options.highlight)
