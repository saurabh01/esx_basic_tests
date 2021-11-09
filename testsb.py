import os
import re

nic_list = ["vmnic5", "vmnic4"]

def cleanup(switch_name, nic):
	#remove uplink
	#remove vswitch
	cmd="esxcli network vswitch standard uplink remove -v "+ switch_name + " -u " + nic
	os.system(cmd)
	cmd2="esxcli network vswitch standard remove -v " +  switch_name 	
	os.system(cmd2)

def create_vswitch(switch_name, mtu_size=9000):
	cmd ="esxcli network vswitch standard  add -v "+ switch_name
	os.system(cmd)

def assign_uplink_to_switch(switch_name, nic):
	cmd="esxcli network vswitch standard uplink add -v "+ switch_name + " -u " + nic
	print("running command....",cmd)
	os.system(cmd)

def create_pg(switch_name,pg_name,vmk_name, vlan):
	cmd1="esxcli network vswitch standard portgroup add -v "+ switch_name + " -p " + pg_name
	os.system(cmd1)
	cmd2="esxcfg-vswitch -p "+pg_name+ " -v " + vlan+ " "+ switch_name
	os.system(cmd2)
	cmd3="esxcli network ip interface add --interface-name="+vmk_name +" --portgroup-name="+ pg_name
	os.system(cmd3)
	cmd4="esxcli network ip interface ipv4 set -t dhcp -i "+ vmk_name
	os.system(cmd4)

def list_switch():
	os.system("esxcfg-vswitch -l")
	os.system("esxcfg-nics -l")


def get_ip():
	cmd= "esxcfg-vmknic -l | awk ' /IPv4/ {print $4}' > ip.txt"
	os.system(cmd)
	with open("ip.txt") as f:
		print (f.read())	
clean_needed=True
for i in range(len(nic_list)):
	switch_name="vSwitch_test_"+str(i)
	if clean_needed==True:
		cleanup(switch_name, nic_list[i])
	create_vswitch(switch_name)
	assign_uplink_to_switch(switch_name, nic_list[i])
	for j in range(10):
		pg_name = "pg_test_"+str(j)+str(i)
		vmk_name= "vmk"+str(j)+str(i)
		create_pg(switch_name, pg_name, vmk_name, vlan="200")
         
list_switch()
get_ip()

