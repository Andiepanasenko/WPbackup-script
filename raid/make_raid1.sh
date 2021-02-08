#!/bin/bash
# Inspired by:
# https://aws.amazon.com/articles/1074
# http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/raid-config.html

DISK1=/dev/xvdb
DISK2=/dev/xvdc
RAID_LABEL=MY_RAID
RAID_MASSIVE=/dev/md0
RAID_MOUNTPOINT=/mnt/raid

yum -y install mdadm

(
echo n  # Add a new partition
echo p  # Primary partition
echo 1  # Partition number
echo    # First sector (Accept default: 1)
echo    # Last sector (Accept default: varies)
echo t  # Change a partition's system id
echo fd # Linux raid auto
echo w  # Write changes
) | fdisk $DISK1


(
echo n  # Add a new partition
echo p  # Primary partition
echo 1  # Partition number
echo    # First sector (Accept default: 1)
echo    # Last sector (Accept default: varies)
echo t  # Change a partition's system id
echo fd # Linux raid auto
echo w  # Write changes
) | fdisk $DISK2


echo $((500*1024)) > /proc/sys/dev/raid/speed_limit_min
echo $((500*1024)) > /proc/sys/dev/raid/speed_limit_max


echo Y | mdadm --create --verbose $RAID_MASSIVE --level=1 --name=$RAID_LABEL --raid-devices=2 $DISK1'1' $DISK2'1' &&\
    mkfs.ext4 -L $RAID_LABEL $RAID_MASSIVE &&\
    mkdir -p $RAID_MOUNTPOINT &&\
    mount LABEL=$RAID_LABEL $RAID_MOUNTPOINT &&\
    cp /etc/fstab /etc/fstab.orig &&\
    echo LABEL=$RAID_LABEL   $RAID_MOUNTPOINT   ext4   defaults,nofail   0   2 >> /etc/fstab &&\
    mount -a
