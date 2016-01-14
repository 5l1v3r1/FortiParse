#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 (                                               
 )\ )              )                     )       
(()/(      (    ( /( (   (  (      )  ( /(   (   
 /(_)) (   )(   )\()))\  )\))(  ( /(  )\()) ))\  
(_))_| )\ (()\ (_))/((_)((_))\  )(_))(_))/ /((_) 
| |_  ((_) ((_)| |_  (_) (()(_)((_)_ | |_ (_))   
| __|/ _ \| '_||  _| | |/ _` | / _` ||  _|/ -_)  
|_|  \___/|_|   \__| |_|\__, | \__,_| \__|\___|  
                        |___/                    

Configuration Parser, by Cornelis de Plaa © 2015

Depends on paramiko, scp and colorama python modules
Install these dependencies using pip or easy_install
'''

import sys
import os
import re
import socket
import getpass
import platform
import paramiko
from scp import SCPClient

from colorama import init, Back, Fore
init(autoreset=True)

config_src = "FGT-config.conf"
vdom_count = 0
vdoms = []
selected_vdom = None
selected_vdom_config = None


def Clear_Screen():
    osver = platform.system()
    if osver == 'Windows':
        os.system("cls")
    else:
        os.system("clear")


def Greeting():
    Clear_Screen()
    print (Back.BLUE + "\n***********************************************************")
    print (Back.BLUE + "*  (                       (                              *")
    print (Back.BLUE + "*  )\ )              )     )\ )                           *")
    print (Back.BLUE + "* (()/(      (    ( /( (  (()/(    )  (          (        *")
    print (Back.BLUE + "*  /(_)) (   )(   )\()))\  /(_))( /(  )(   (    ))\       *")
    print (Back.BLUE + "* (_))_| )\ (()\ (_))/((_)(_))  )(_))(()\  )\  /((_)      *")
    print (Back.BLUE + "* | |_  ((_) ((_)| |_  (_)| _ \((_)_  ((_)((_)(_))        *")
    print (Back.BLUE + "* | __|/ _ \| '_||  _| | ||  _// _` || '_|(_-</ -_)       *")
    print (Back.BLUE + "* |_|  \___/|_|   \__| |_||_|  \__,_||_|  /__/\___|       *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Fortigate Config Parser                                 *")
    print (Back.BLUE + "* By Cornelis de Plaa 2015                                *")
    print (Back.BLUE + "*                                                    v1.0 *")
    print (Back.BLUE + "***********************************************************\n")


def SCP_Backup():
    global config_src
    
    firewall = raw_input("Enter Firewall IP address or hostname: ")
    username = raw_input("Enter your username: ")
    passwd = getpass.getpass("Enter your password: ")
            
    print "\n+ Trying to connect to " +firewall+ "",
    
    try:
        remote_conn_pre=paramiko.SSHClient()
        remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_conn_pre.connect(firewall, username=username, password=passwd)
        scp = SCPClient(remote_conn_pre.get_transport())
    except paramiko.AuthenticationException:
        print ("\n+ "+ Back.RED + "Authentication failed for some reason")
        sys.exit(1)
    except paramiko.SSHException, error:
        print ("\n+ "+ Back.RED + "Username or Password is invalid:") , error
        sys.exit(1)
    except socket.error, error:
        print ("\n+ "+ Back.RED + "Failed to connect to the firewall " +firewall+ ":"), error
        sys.exit(1)
    except:
        print ("\n+ "+ Back.RED + "Unknown error!")
        sys.exit(1)

    print "-> Connection Established!"
    
    if not os.path.exists("Saved_Configs"):
        os.makedirs('Saved_Configs')
    os.chdir('Saved_Configs')
    
    scp.get('sys_config')

    scp.close()
    
    if os.path.exists("sys_config"):
        print "+ Backup successfully completed!"
        if os.path.exists(config_src):
            os.remove(config_src)
        os.rename("sys_config", config_src)
    else:   
        print "+ Backup failed!"
        sys.exit(1)


def Extract_VDOM():
    global config_src
    global vdom_count
    global vdoms
        
    config = open(config_src, 'r')
    data = config.read()
        
    print "+ The following VDOM's are found:\n" 
    for line in data.splitlines():
        vdom_name = None
        if re.search('^end$', line):
            break
        if re.search('^edit ', line) and not re.search('^edit root', line):
            vdom = line.split()
            if vdom != None:
                vdom_name = vdom[1]
                vdoms.append(vdom_name)
                print vdom_count+1,'- '+vdom_name.ljust(15),
                vdom_strip = re.sub('edit '+vdom_name, '', data, 1, flags=re.M)
                vdom_count +=1
        if vdom_name != None:
            print "\t Extracing VDOM Config",
            vdom_cfg = open("FGT-"+vdom_name+"-config.conf", 'w')
            vdom_cfg.write("config vdom\n")
            vdom_data = re.search(r'^edit '+vdom_name+'.*?^end$\n^end$', vdom_strip, re.DOTALL | re.M)
            if vdom_data:
                vdom_cfg.write(vdom_data.group(0))
            vdom_cfg.close()
            if os.path.exists("FGT-"+vdom_name+"-config.conf"):
                print "\t-> Done\n",
    if vdom_count == 0:
        print "! No VDOM's found"
    config.close()


def Menu():
    global vdom_count
    
    if vdom_count > 0:
        Select_VDOM(vdoms)
        Config_Menu()
    else:
        Config_Menu()
 
    
def Select_VDOM(vdom_names):
    global selected_vdom
    global selected_vdom_config
    
    count = 0
    Clear_Screen()
    print (Back.BLUE + "\n***********************************************************")
    print (Back.BLUE + "*  (                       (                              *")
    print (Back.BLUE + "*  )\ )              )     )\ )                           *")
    print (Back.BLUE + "* (()/(      (    ( /( (  (()/(    )  (          (        *")
    print (Back.BLUE + "*  /(_)) (   )(   )\()))\  /(_))( /(  )(   (    ))\       *")
    print (Back.BLUE + "* (_))_| )\ (()\ (_))/((_)(_))  )(_))(()\  )\  /((_)      *")
    print (Back.BLUE + "* | |_  ((_) ((_)| |_  (_)| _ \((_)_  ((_)((_)(_))        *")
    print (Back.BLUE + "* | __|/ _ \| '_||  _| | ||  _// _` || '_|(_-</ -_)       *")
    print (Back.BLUE + "* |_|  \___/|_|   \__| |_||_|  \__,_||_|  /__/\___|       *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Fortigate Config Parser                                 *")
    print (Back.BLUE + "* By Cornelis de Plaa 2015                                *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Firewall hostname: %s                      *" % Get_Hostname().ljust(15))
    print (Back.BLUE + "* FortiOS version: %s         *" % Get_FortiOS().ljust(30))
    print (Back.BLUE + "* Available VDOM's:                                       *")
    print (Back.BLUE + "*                                                         *")
    for vdom in vdom_names: 
        print (Back.BLUE + "* %d - %s                                     *" % (count+1,vdom.ljust(15)))
        count +=1
    print (Back.BLUE + "*                                                    v1.0 *")
    print (Back.BLUE + "***********************************************************\n")
    
    while True:
        vdom_choice = raw_input("Choose which VDOM config number to parse: ")
        if vdom_choice.isdigit():
            vdom_choice = int(vdom_choice)
            if vdom_choice <= count and vdom_choice != 0: 
                break
            else:
                print (Fore.RED + "That's not a valid number, try again!\n")
        else:
            print (Fore.RED + "That's not a valid number, try again!\n") 
    vdom_choice -=1
    selected_vdom = vdom_names[vdom_choice]
    selected_vdom_config = "FGT-"+selected_vdom+"-config.conf"
    

def Get_Hostname():
    global config_src
    
    config = open(config_src, 'r')
    data = config.read()
    
    host_config = re.search(r'set hostname ".*?"$', data, re.DOTALL | re.M)
    host_list = host_config.group(0).split()
    hostname = host_list[2]
    config.close()
    return hostname[1:-1]


def Get_FortiOS():
    global config_src
    
    config = open(config_src, 'r')
    data = config.read()
    
    os_version = re.search(r'^#config-version=.*?:', data, re.DOTALL | re.M)
    version = os_version.group(0).split('=')
    fortios = version[1]
    config.close()
    return fortios[:-1]


def Config_Menu():
    global vdom_count
    global selected_vdom
    global selected_vdom_config
    
    if vdom_count > 0:
        menu_items = 12
    else:
        menu_items = 11
    
    Clear_Screen()
    print (Back.BLUE + "\n***********************************************************")
    print (Back.BLUE + "*  (                       (                              *")
    print (Back.BLUE + "*  )\ )              )     )\ )                           *")
    print (Back.BLUE + "* (()/(      (    ( /( (  (()/(    )  (          (        *")
    print (Back.BLUE + "*  /(_)) (   )(   )\()))\  /(_))( /(  )(   (    ))\       *")
    print (Back.BLUE + "* (_))_| )\ (()\ (_))/((_)(_))  )(_))(()\  )\  /((_)      *")
    print (Back.BLUE + "* | |_  ((_) ((_)| |_  (_)| _ \((_)_  ((_)((_)(_))        *")
    print (Back.BLUE + "* | __|/ _ \| '_||  _| | ||  _// _` || '_|(_-</ -_)       *")
    print (Back.BLUE + "* |_|  \___/|_|   \__| |_||_|  \__,_||_|  /__/\___|       *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Fortigate Config Parser                                 *")
    print (Back.BLUE + "* By Cornelis de Plaa 2015                                *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Firewall hostname: %s                      *" % Get_Hostname().ljust(15))
    print (Back.BLUE + "* FortiOS version: %s         *" % Get_FortiOS().ljust(30))
    if vdom_count > 0:
        print (Back.BLUE + "* Selected VDOM: %s                          *" % selected_vdom.ljust(15))
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* Available configuration items:                          *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 1 - Firewall interfaces                                 *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 2 - Firewall address                                    *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 3 - Firewall IPv6 address                               *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 4 - Firewall address groups                             *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 5 - Firewall IPv6 address groups                        *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 6 - Firewall services                                   *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 7 - Firewall service groups                             *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 8 - Firewall policies                                   *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 9 - Firewall IPv6 policies                              *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 10 - Firewall routing                                   *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "*                                                         *")
    print (Back.BLUE + "* 11 - Exit program                                       *")
    if vdom_count > 0:
        print (Back.BLUE + "*                                                         *")
        print (Back.BLUE + "*                                                         *")
        print (Back.BLUE + "* 12 - Return to VDOM selection                           *")
    print (Back.BLUE + "*                                                    v1.0 *")
    print (Back.BLUE + "***********************************************************\n")
    
    while True:
        item_choice = raw_input("Choose which configuration items to parse: ")
        if item_choice.isdigit():
            item_choice = int(item_choice)
            if item_choice <= menu_items and item_choice != 0: 
                break
            else:
                print (Fore.RED + "That's not a valid number, try again!\n")
        else:
            print (Fore.RED + "That's not a valid number, try again!\n")
    print "\n"
    if item_choice == 1:
        Get_Interface_Items()
        Config_Menu()
    if item_choice == 2:
        Get_Addr_Items()
        Config_Menu()
    if item_choice == 3:
        Get_Addr6_Items()
        Config_Menu()
    if item_choice == 4:
        Get_Grp_Items()
        Config_Menu()
    if item_choice == 5:
        Get_Grp6_Items()
        Config_Menu()
    if item_choice == 6:
        Get_Srvc_Items()
        Config_Menu()
    if item_choice == 7:
        Get_SrvcGrp_Items()
        Config_Menu()
    if item_choice == 8:
        Get_Policy_Items()
        Config_Menu()
    if item_choice == 9:
        Get_Policy6_Items()
        Config_Menu()
    if item_choice == 10:
        Get_Router_Items()
        Config_Menu()
    if item_choice == 11:
        print (Fore.RED + "+ Exiting program, bye bye!\n")
        sys.exit(0)
    if item_choice == 12:
        Menu()


def Get_Interface_Items():
    line_count = 0
    
    global config_src
    config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config system interface.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 50 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            item_cfg = open("interfaces.conf", 'w')
            item_cfg.write(cfg_objects.group(0))
            item_cfg.close()
            print "\nConfig saved as: interfaces.conf"
            break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()


def Get_Addr_Items():
    global vdom_count
    global selected_vdom
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall address$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return        
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-addr.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-addr.conf"
                break
            else:
                item_cfg = open("addr.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: addr.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n")    
    config.close()
    
    
def Get_Addr6_Items():
    global vdom_count
    global selected_vdom
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall address6$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-addr6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-addr6.conf"
                break
            else:
                item_cfg = open("addr6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: addr6.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n")    
    config.close()
    
    
def Get_Grp_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall addrgrp$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-grp.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-grp.conf"
                break
            else:
                item_cfg = open("grp.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: grp.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()


def Get_Grp6_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall addrgrp6$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-grp6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-grp6.conf"
                break
            else:
                item_cfg = open("grp6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: grp6.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()
    
    
def Get_Srvc_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall service custom$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-srvc.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-srvc.conf"
                break
            else:
                item_cfg = open("srvc.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: srvc.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()


def Get_SrvcGrp_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall service group$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-srvc-grp.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-srvc-grp.conf"
                break
            else:
                item_cfg = open("srvc-grp.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: srvc-grp.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()
    
    
def Get_Policy_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall policy$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-pol.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-pol.conf"
                break
            else:
                item_cfg = open("pol.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: pol.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()
    
    
def Get_Policy6_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config firewall policy6$.*?^end$', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 100 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-pol6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-pol6.conf"
                break
            else:
                item_cfg = open("pol6.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: pol6.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()
    
    
def Get_Router_Items():
    global vdom_count
    line_count = 0
    
    if vdom_count > 0:
        global selected_vdom
        global selected_vdom_config
        config = open(selected_vdom_config, 'r')
    else:
        global config_src
        config = open(config_src, 'r')
    data = config.read()    
    cfg_objects = re.search(r'^config router.*?^config router multicast$\n^end$.*', data, re.DOTALL | re.M)
    if cfg_objects == None:
        print (Fore.GREEN + "No such item found!")
        raw_input(Fore.RED + "\nPress enter to continue!\n")
        return 
    lines = cfg_objects.group(0).splitlines()
    for line in lines:
        print line
        line_count += 1
        if line_count % 50 == 0:
            raw_input(Fore.RED + "\nPress enter to continue!\n")
    
    choice = raw_input(Fore.GREEN + "\nDo you want to save these objects: [yes/no]? ").lower()
    yes = set(['yes','y'])
    no = set(['no','n'])
    while True:
        if choice in yes:
            if vdom_count > 0:
                item_cfg = open(selected_vdom+"-router.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: "+selected_vdom+"-router.conf"
                break
            else:
                item_cfg = open("router.conf", 'w')
                item_cfg.write(cfg_objects.group(0))
                item_cfg.close()
                print "\nConfig saved as: router.conf"
                break
        elif choice in no:
            config.close()
            return
        else:
            choice = raw_input(Fore.GREEN + "\nPlease respond with 'yes' or 'no': [yes/no]? ").lower()       
    raw_input(Fore.RED + "\nPress enter to continue!\n") 
    config.close()
    
                  
if __name__ == '__main__':
    Greeting()
    SCP_Backup()
    Extract_VDOM()
    Menu()
    
    sys.exit(0)
    