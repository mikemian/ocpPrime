#!/bin/bash
echo "                                                                                                                          "
echo "      OOOOOOOOOOOOOZO               OOOZZOOOOOOOOOOZOON            OOZOOOOOOOOOOOOOOOOOZ          OOOOOOOOOOOOOOOOOZZ     "
echo "   DOOOOOOOOOOOOOOOOOOZO           ZOOOOOOOOOOOOOOOOOOOOO          OOOOOOOOOOOOOOOOOOOOOO         ZOOOOOOOOOOOOOOOOOOOOO  "
echo "  DOOOOOOOOOOOOOOOOOOOOOO          OOOOOOOOOOOOOOOOOOOOOOO         OOOOOOOOOOOOOOOOOOOOOO         OOOOOOOOOOOOOOOOOOOOOOZ "
echo "  OOOOOOOOOOOOOOOOOOOOOOZO         OOOOOOOOOOOOOOOOOOOOOOOO        OOOOOOOOOOOOOOOOOOOOO          OOOOOOOOOOOOOOOOOOOOOOO "
echo "  OOOOOO            OOOOOO         OOOOOO            OOOOOZ        OOOOO                          OOOOOO            ZOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOO            OOOOOO        OOOOO                          OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOZOOOOOOOOOOOOOOOOOZ        OOOOOOOOOOOOOOOO               OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOOOOOOOOOOOOOOOOOOO         OOOOOOOOOOOOOOOO               OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOOOOOOOOOOOOOOOOOO          OOOOOOOOOOOOOOOO               OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOOOOOOOOOOOOOOO             OOOOOOOOOOOOOOO8               OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOO                          OOOOO                          OOOOOO            OOOOOO"
echo "  OOOOOO            OOOOOO         OOOOOO                          OOOOO                          OOOOOO            OOOOOO"
echo "  OOOOOOOOOOOOOOOOOOOOOOO          OOOOOO                          OOOOOOOOOOOOOOOOOOOOO8         OOOOOO            OOOOOO"
echo "   OOOOOOOOOOOOOOOOOOOOOO          OOOOOO                          OOOOOOOOOOOOOOOOOOOOOZ         OOOOOO            OOOOOO"
echo "    OOOOOOOOOOOOOOOOOOZO           OOOOOO                          OOOOOOOOOOOOOOOOOOOOOZ         OOOOOO            ZOOOOO"
echo "                                                                                                                          "
echo "Creating OCP Disposable OS"
echo " "
echo "Installing livecd-tools"
yum -y install livecd-tools
ls -l | egrep '^d' | xargs rm -rf
livecd-creator -v --config=np-disposable.ks --fslabel=NodePrime-Disposable-OS
livecd-iso-to-pxeboot NodePrime-Disposable-OS.iso