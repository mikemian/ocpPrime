#!/bin/bash
echo "                                                                               "
echo "          MMM                                                                  "
echo "         MMMMD                                                                 "
echo "    DMM   MMMMMMMM                      M                  M                   "
echo "    MMMM       MMMM     NMM    MM,   DMMM   MM    +7+   iI     7+ 7+    7:     "
echo "    IMMMMMMMD  ~MM,    MN  M ZM  MM MI  M MM  MM M  ?M M   M M   M  M M?  M    "
echo "         MMMM          M?  M MM  MM M   M MMMMMM M   M M   M M   M  M MMMMM    "
echo "    7MM   MMM  =MM     M?  M 8M  MM M   M MM     M   M M   M M   M  M M,       "
echo "    MMMM   M   MMMM    M?  M   MM,   MMMI   MMM: MMM+  M   M N   M  M  :MMM    "
echo "    DMM   MMD  ZMM                               M                             "
echo "         MMMM                                                                  "
echo "          MMM                                                                  "
echo "                                                                               "
echo "Creating NodePrime Disposable OS"
echo " "
echo "Installing livecd-tools"
yum -y install livecd-tools
ls -l | egrep '^d' | xargs rm -rf
livecd-creator -v --config=np-disposable.ks --fslabel=NodePrime-Disposable-OS
livecd-iso-to-pxeboot NodePrime-Disposable-OS.iso
