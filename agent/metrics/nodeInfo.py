#!/usr/bin/python
# ##############################################################################
#
#  (C) 2013 nodeprime Inc.  All rights reserved.
#
#  THIS SOFTWARE IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT IS
#  PROVIDED "AS IS" WITHOUT ANY WARRANTY, EXPRESS, IMPLIED OR OTHERWISE,
#  INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTY OF MERCHANTABILITY OR
#  FITNESS FOR A PARTICULAR PURPOSE OR ANY WARRANTY REGARDING TITLE OR
#  AGAINST INFRINGEMENT.  IN NO EVENT SHALL MATRIU BE LIABLE FOR ANY DIRECT,
#  INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTUTUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#  STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#  IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#  POSSIBILITY OF SUCH DAMAGE.
#
#  This script is provided as part of ocpPrime, and is not warranted
#  in any way by nodeprime; nodeprime disclaims any liability in connection therewith.
#  nodeprime provides no technical support with regard to content herein. For
#  more information on libraries and tools used in this example, refer to
#  applicable documentation
#
# ##############################################################################
# Filename: metrics/nodeInfo.py
# Authors: Nathan Rockhold - nate@nodeprime.com

# This script return the current uptime.

import commands, dmidecode, json, platform, time
from subprocess import Popen, PIPE

# Calling nodeinfo

isPXE = 1

nodeInfo = {}

# Add date to JSON
nodeInfo["date"] = int(time.time())

# Basic Chassis Information
nodeInfo["attributes"] = {}
nodeInfo["attributes"]["UUID"] = commands.getoutput("echo $(dmidecode -t 1 | grep UUID | awk '{print $2}')-$(ifconfig | egrep 'eth0|em1' | sed 's/://g' | awk '{print $5}')")
nodeInfo["attributes"]["vendor"] =  ""
if dmidecode.type(1)[dmidecode.type(1).keys()[0]]["data"]["Manufacturer"].find("Quanta") > -1:
    nodeInfo["attributes"]["vendor"] = "Quanta"
elif dmidecode.type(1)[dmidecode.type(1).keys()[0]]["data"]["Manufacturer"].find("Tyan") > -1:
    nodeInfo["attributes"]["vendor"] = "Tyan"
nodeInfo["attributes"]["platform"] = dmidecode.type(1)[dmidecode.type(1).keys()[0]]["data"]["Product Name"]
nodeInfo["attributes"]["serial"] = dmidecode.type(1)[dmidecode.type(1).keys()[0]]["data"]["Serial Number"]
nodeInfo["attributes"]["cVendor"] = dmidecode.type(3)[dmidecode.type(3).keys()[0]]["data"]["Manufacturer"]
nodeInfo["attributes"]["cSerial"] = dmidecode.type(3)[dmidecode.type(3).keys()[0]]["data"]["Serial Number"]
nodeInfo["attributes"]["assetTag"] = dmidecode.type(3)[dmidecode.type(3).keys()[0]]["data"]["Asset Tag"]
nodeInfo["attributes"]["type"] = dmidecode.type(3)[dmidecode.type(3).keys()[0]]["data"]["Type"]
nodeInfo["attributes"]["fqdn"] = commands.getoutput("hostname --long") 
nodeInfo["attributes"]["ips"] = commands.getoutput("ifconfig | grep \"inet addr:\" | grep -v \"127.0.0.1\" | cut -d: -f2 | awk '{print $1}'").splitlines()
nodeInfo["attributes"]["isPXE"] = isPXE

# Processor Information
nodeInfo["components"] = {}
nodeInfo["components"]["processors"] = []
procDMI = dmidecode.type(4)
for key in procDMI.keys():
    procDict = {}
    procDict["vendor"] = procDMI[key]["data"]["Manufacturer"]["Vendor"] 
    procDict["family"] = procDMI[key]["data"]["Family"] 
    procDict["platform"] = procDMI[key]["data"]["Version"] 
    procDict["speed"] = float(procDMI[key]["data"]["Version"].split("@")[1].replace("GHz","").strip())
    procDict["units"] = procDMI[key]["data"]["Version"].split("@")[1].split(" ")[1].strip()
    procDict["cores"] = procDMI[key]["data"]["Core Count"] 
    procDict["threads"] = procDMI[key]["data"]["Thread Count"] 
    procDict["socket"] = procDMI[key]["data"]["Socket Designation"] 
    procDict["status"] = procDMI[key]["data"]["Status"]
    nodeInfo["components"]["processors"].append(procDict)

# Memory Information
nodeInfo["components"]["memory"] = []
memDMI = dmidecode.type(17)
for key in memDMI.keys():
    memDict = {}
    memDict["vendor"] = memDMI[key]["data"]["Manufacturer"] 
    memDict["platform"] = memDMI[key]["data"]["Part Number"]
    memDict["serial"] = memDMI[key]["data"]["Serial Number"]
    memDict["locator"] = memDMI[key]["data"]["Locator"]
    memDict["bank"] = memDMI[key]["data"]["Bank Locator"]
    memDict["speed"] = memDMI[key]["data"]["Speed"]
    size = memDMI[key]["data"]["Size"]
    if not size is None:
        memDict["size"] = int(size.split()[0])
        memDict["units"] = size.split()[1]
    else:
        memDict["size"] = 0
        memDict["units"] = ""
    nodeInfo["components"]["memory"].append(memDict)

# Calculate Memory Total
nodeInfo["attributes"]["memTotal"] = 0
for dim in nodeInfo["components"]["memory"]:
    nodeInfo["attributes"]["memTotal"] = nodeInfo["attributes"]["memTotal"] + dim["size"]
nodeInfo["attributes"]["memTotal"] = nodeInfo["attributes"]["memTotal"] / 1024

# Storage Controller Info
nodeInfo["components"]["storageController"] = []
storageInfo = commands.getoutput("lspci -v | egrep -A1 'RAID bus|IDE interface|SATA controller' | grep -v '\-\-'")
for num, line in enumerate(storageInfo, 1):
    controller = {}
    if num % 2 == 0:
        controller["pciID"] = line.split(" ")[0]
        controller["oPlatform"] = line.split(": ")[1].strip()
    if not num % 2 == 0:
        controller["platform"] = line.split(": ")[1].strip()
    # MegaRAID Controller Info
    if controller["oPlatform"].find("MegaRAID") > -1:
        stdout = Popen("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog", shell=True, stdout=PIPE).stdout
        stdout.read() 
        if int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL | grep Name | wc -l")) > 0:
            nodeInfo["attributes"]["isRAID"] = 1
        controller["vendor"] = "LSI"
        controller["firmware"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog | grep 'FW Package Build' | awk '{print $4}'")
        controller["bbu"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog| grep 'BBU' | head -n1 | awk '{print $3}'")
        controller["cache"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog| grep 'Memory Size' | awk '{print $4}'")
        controller["tDisks"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog | grep 'Disks' | sed -n '1p' | awk '{print $3}'"))
        controller["cDisks"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog| grep 'Disks' | sed -n '2p' | awk '{print $4}'"))
        controller["fDisks"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -AdpAllInfo -aALL -NoLog| grep 'Disks' | sed -n '3p' | awk '{print $4}'"))
        controller["eID"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -EncInfo -aALL -NoLog| grep 'Device ID' | awk '{print $4}'"))
        controller["eSlots"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -EncInfo -aALL -NoLog| grep 'Number of Slots' | awk '{print $5}'"))

# RAID Info
nodeInfo["attributes"]["isRAID"] = False
if not commands.getoutput("cat /proc/mdstat | grep md | wc -l") == "0":
    nodeInfo["attributes"]["isRAID"] = 1

# Physical Disks Array
nodeInfo["components"]["pDisks"] = []

# MegaRAID Physical Disks Info
if nodeInfo["components"]["storageController"]["oPlatform"].find("MegaRAID") > -1 and nodeInfo["attributes"]["isRAID"]:
    for disk in range(nodeInfo["components"]["storageController"]["tDisks"]):  
        diskDict = {}
        diskDict["slot"] = disk
        for line in commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -PDInfo -PhysDrv [" + str(nodeInfo["components"]["storageController"]["eID"]) + ":" + str(disk) + "] -aALL").splitlines():
            if "Inquiry Data:" in line:
                diskDict["vendor"] = line.split()[2]
            elif "Inquiry Data:" in line:
                diskDict["platform"] = line.split()[3]
            elif "Device Firmware Level:" in line:
                diskDict["firmware"] = line.split()[3]
            elif "PD Type:" in line:
                diskDict["interface"] = line.split()[2]
            elif "Media Type:" in line:
                diskDict["type"] = line.split(":")[1]
            elif "Raw Size:" in line:
                diskDict["size"] = line.split()[2]
                diskDict["units"] = line.split()[3]
            elif "Media Error Count:" in line:
                diskDict["mErrors"] = int(line.split()[3])
            elif "Predictive Failure Count:" in line:
                diskDict["sErrors"] = int(line.split()[3])
        nodeInfo["components"]["pDisks"].append(diskDict)

# No RAID Physical Disk Info
if not nodeInfo["attributes"]["isRAID"]:
    for disk in commands.getoutput("ls /dev/ | egrep 'sd[a-z]$' | uniq").splitlines():
        if commands.getoutput("hdparm -I /dev/" + disk).find("SG_IO: bad") > -1:
            continue
        diskDict = {}
        diskDict["vendor"] = "N/A"
        diskDict["platform"] = commands.getoutput("hdparm -I /dev/" + disk + " | grep 'Model Number' | awk '{print $3}'").strip()
        diskDict["serial"] = commands.getoutput("hdparm -I /dev/" + disk + " | grep 'Serial Number' | awk '{print $3}'").strip()
        diskDict["firmware"] = commands.getoutput("hdparm -I /dev/" + disk + " | grep 'Firmware Revision' | awk '{print $3}'").strip()
        diskDict["interface"] = commands.getoutput("hdparm -I /dev/" + disk + " | grep 'Transport' | awk -F: '{print $2}'").strip()
        diskDict["type"] = "N/A"
        diskDict["size"] = int(commands.getoutput("hdparm -I /dev/" + disk + " | grep '1000\*1000' | awk '{print $7}'"))
        diskDict["units"] = "MB"
        diskDict["mErrors"] = "N/A"
        diskDict["sErrors"] = "N/A"
        diskDict["slot"] = "N/A" 
        nodeInfo["components"]["pDisks"].append(diskDict)

# RAID Virtual Disks Info
if nodeInfo["attributes"]["isRAID"]:
    nodeInfo["components"]["vdisks"] = []
    # MegaRAID Virtual Disks Info
    if nodeInfo["components"]["storageController"]["oPlatform"].find("MegaRAID") > -1:
        for disk in range(int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -Lall -aALL | grep Name | wc -l"))):  
            diskDict = {}
            diskDict["name"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'Name' | awk -F: '{print $2}'").strip()
            diskDict["raid"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'RAID Level' | awk -F: '{print $2}'").strip()
            diskDict["size"] = float(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'Size' | sed -n '1p' | awk '{print $3}'"))
            diskDict["units"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'Size' | sed -n '1p' | awk '{print $4}'").strip()
            diskDict["disks"] = int(commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'Number Of Drives' | awk '{print $5}'"))
            diskDict["state"] = commands.getoutput("/opt/MegaRAID/MegaCli/MegaCli64 -LDInfo -L" + str(disk) + " -aALL | grep 'State' | awk -F: '{print $2}'").strip()
            nodeInfo["components"]["vdisks"].append(diskDict)

# NIC Info
nodeInfo["components"]["nics"] = []
for nic in commands.getoutput("ifconfig | egrep 'em[0-9]|eth[0-9]' | awk '{print $1}'").splitlines():
    nicDict = {}
    nicDict["type"] = commands.getoutput("ethtool " + nic + " | grep 'Port:' | awk -F: '{print $2}'").strip()
    nicDict["mac"] = commands.getoutput("ifconfig " + nic + " | grep HWaddr | awk '{print $5}'").strip()
    nicDict["platform"] = commands.getoutput("lspci -v | grep -B 11 " + nicDict["mac"].lower()[10:].replace(":","-") + " | grep 'Ethernet controller' | awk -F: '{print $3}'").strip()
    nicDict["interface"] = nic
    nicDict["firmware"] = commands.getoutput("ethtool -i " + nic + " | grep 'firmware-version' | sed 's/firmware-version: //g'").strip()
    nicDict["pciID"] = commands.getoutput("lspci -v | grep -B 11 " + nicDict["mac"].lower()[10:].replace(":","-") + " | grep 'Ethernet controller' | awk '{print $1}'").strip()
    nicDict["vendor"] = commands.getoutput("cat mac.db | grep $(ifconfig " + nic + "| egrep '" + nic + "' | awk '{print $5}' | awk '{print substr($1,1,8)}')")[9:].strip()
    nicDict["link"] = commands.getoutput("ethtool " + nic + " | grep 'Link detected:' | awk -F: '{print $2}'").strip()
    nodeInfo["components"]["nics"].append(nicDict)
    
# BIOS Info
nodeInfo["components"]["bios"] = {}
nodeInfo["components"]["bios"]["firmware"] = dmidecode.type(0)[dmidecode.type(0).keys()[0]]["data"]["Version"]
nodeInfo["components"]["bios"]["vendor"] = dmidecode.type(0)[dmidecode.type(0).keys()[0]]["data"]["Vendor"]

# BMC Info
nodeInfo["components"]["bmc"] = {}
if len(dmidecode.type(38)) > 0:
    for line in commands.getoutput("bmc-info | head -n15").splitlines():
        if "Firmware Version" in line:
            nodeInfo["components"]["bmc"]["firmware"] = line.split(":")[1].strip() 
        if "Manufacturer ID" in line:
            nodeInfo["components"]["bmc"]["vendor"] = line.split(":")[1].strip()
        if "IPMI Version" in line:
            nodeInfo["components"]["bmc"]["ipmi"] = line.split(":")[1].strip()
    for line in commands.getoutput("ipmitool lan print").splitlines():
        if "IP Address" in line:
            nodeInfo["components"]["bmc"]["ip"] = line.split(":")[1].strip()
        if "MAC Address" in line:
            nodeInfo["components"]["bmc"]["mac"] = line.split(" : ")[1].strip()

# PCI Info
nodeInfo["components"]["pci"] = []
for dev in commands.getoutput("lspci").splitlines():
    pciDict = {}
    pciDict["pciID"] = dev.split(" ")[0].strip()
    pciDict["type"] = dev.split(":")[1][dev.find(" ")-2:].strip()
    pciDict["platform"] = dev.split(":")[2][1:].strip()
    nodeInfo["components"]["pci"].append(pciDict)

# USB Info
nodeInfo["components"]["usb"] = []
for dev in commands.getoutput("lsusb").splitlines():
    usbDict = {}
    usbDict["usbID"] = dev[0:31].strip()
    usbDict["platform"] = dev[32:].strip()
    nodeInfo["components"]["usb"].append(usbDict)

# OS Info
nodeInfo["components"]["OS"] = {}
nodeInfo["components"]["OS"]["dist"] = platform.dist()
nodeInfo["components"]["OS"]["system"] = platform.system()
nodeInfo["components"]["OS"]["release"] = platform.release()
nodeInfo["components"]["OS"]["version"] = platform.version()
nodeInfo["components"]["OS"]["machine"] = platform.machine()
nodeInfo["components"]["OS"]["arch"] = platform.processor()
nodeInfo["components"]["OS"]["platform"] = platform.platform()

print json.JSONEncoder().encode(nodeInfo)