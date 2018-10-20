Cloudify Lumina Flow Manager Plugin
===================================

# Overview

The Cloudify Lumina PCE Plugin integrates the Lumina SDN Controller 
to Cloudify as an orchestration and service automation deployment platform.

The plugin currently has limited functionality for ELine and Path services.

Cloudify receives blueprints and execution instructions and using the plugin 
sends it to the Lumina Flowmanager Controller API using the 
Python Flowmanager Client.

# Configuration

## SDN Configuration

The sdn_config is defined in the Blueprints which gets pulled from the 
Cloudify secrets so that the service can be deployed to any environment.
These are the properties: 
- lsc_ipaddress
- lsc_user
- lsc_password
- lsc_protocol
- lsc_port
- lsc_verify

To set the values, use the Cloudify CLI. e.g 
```commandline
cfy secrets create lsc_user -s admin
```

If the sdn_config is consistent across all Blueprints you can use the 
sdn_config.json which by default will be placed in the user home folder 
`~/.lumina/sdn_config.json`. To set it to a different folder use the 
environment variable SDN_CONFIG_PATH.

## Installation

To get the list of commands use the Make file by typing `make`.

It's recommended to use a python 2.7 virtualenv to keep the environment isolated.

To create an environment:
```commandline
virtualenv .venv
source .venv/bin/activate
```

you can then install all the plugin requirements using the `make dev` which will
run the following:
```commandline
pip install -r dev-requirements.txt
python setup.py develop
```

To package and upload the plugin if the package is on the Cloudify server use 
`make replace`, which will package, delete existing plugin and upload the 
new one. 

Keep in mind if you package it elsewhere, the OS needs to be similar see the 
wagon file extended name `none-linux_x86_64`.

To package and upload manually:
```
wagon create -r dev-requirements.txt -f .
cfy plugin upload -y plugin.yaml cloudify_lfm_plugin-0.1.0-py27-none-linux_x86_64.wgn
```

you can have multiple instances of the plugin with different versions, but 
not the same version and name. To delete an old plugin which commands are
included in the Makefile. List the plugins and get the plugin id to delete with.  
```commandline
cfy plugin list
cfy plugin delete <plugin_id>
```

# Usage

For a sample blueprint check the examples folder: 
- examples/blueprint/eline-ethernet-test.yaml
- examples/blueprint/eline-vlan-test.yaml

For testing on mininet, use ethernet.

The ethernet blueprint creates 2 elines for IP and ARP and 1 path.
Both are created using the connection points / end points, which include the
information that creates the services.

You can upload it through the UI in the Local blueprints section 
`/stage/page/local_blueprints`.  
e.g http://192.168.50.30/stage/page/local_blueprints
Click the `Upload` button, select attachment, set a name, and under blueprint 
file choose the blueprint you want to use.

Blueprints need to be a folder packaged into a zip file. 
e.g 
- blueprint/eline.yaml
blueprint.zip

To upload through CLI: 
`cfy blueprints upload -b blueprint-id blueprintfile` 
e.g 
`cfy blueprints upload -b my-eline examples/blueprint/eline-ethernet-test.yaml`

Then create a new deployment through the UI 
`http://192.168.50.30/stage/page/deployments` click on the 
`Create new deployment` button, set a deployment name, choose a blueprint 
from the list for the blueprint you created above and then set the values.
To quickly prefill the values, use the input file provided 
in the examples inputs folder:
`examples/inputs/eline-ethernet-test.yaml`.

e.g
    eline_name: "eline_test"
    path_name: "path_test"
    
    ep1_switch_id: "openflow:101"
    ep1_switch_port: "1"
    ep1_network_type: "vlan"
    ep1_segmentation_id: "100"
    
    ep2_switch_id: "openflow:303"
    ep2_switch_port: "1"
    ep2_network_type: "vlan"
    ep2_segmentation_id: "100"
    
    path_waypoints: "openflow:102,openflow:103"
    
When using mininet, start with port 1.

After the deployment is created, to execute it click on the hamburger icon 
dropdown and then install.

For creating an execution manually through CLI, use 
```commandline
cfy deployments create -b <blueprint_id> -i <inputs> <deployment_id>
cfy executions start -d <deployment_id> install
```
e.g:
```commandline
cfy deployments create -b my-eline -i examples/inputs/eline-ethernet-test.yaml my-eline-test1
cfy executions start -d my-eline-test1 install
```

# Validating the ELine and Path had been created

## Controller UI
See paths and services tabs on the controller page: 
http://192.168.50.21:9001/apps/lsc-app-flowmanager/paths

## Postman

Set your Local Dev environment with the following variables or manually 
set the URLs bellow with the values:
```
Variable    Initial Value   Current Value
lsc_protocol    http    http
lsc 192.168.50.21   192.168.50.21
lsc_port    8181    8181
```

Set the following headers: 
```
Key     Value
Accept  application/json
Content-Type  application/json
```

Under Authorization tab:
```
Type:   Basic Auth
Username:   admin
Password:   admin
``` 

Get Paths:
{{lsc_protocol}}://{{lsc}}:{{lsc_port}}/restconf/operational/lumina-flowmanager-path:paths

Get ELines:
{{lsc_protocol}}://{{lsc}}:{{lsc_port}}/restconf/operational/lumina-flowmanager-eline:elines


# Extending the plugin

## References

Cloudify writing plugin information: 
https://docs.cloudify.co/4.4.0/developer/writing_plugins/

PEP 8 style guide https://www.python.org/dev/peps/pep-0008/

Cloudify API: https://docs.cloudify.co/api/v3.1/

OpenDayLight Wiki: https://wiki.opendaylight.org/view/Main_Page

## IDE Configuration

Setup Python Virtual Environment and install requirements:
```commandline
virtualenv .venv
source .venv/bin/activate
pip install -r dev-requirements.txt
python setup.py develop
```

Point Pycharm to use the virtual environment you created as the intrepeter. 
PyCharm > Preferences > Project > Project Interpreter > Project intrepeter 
set to the .venv path you're using and apply with OK.

## Makefile

Makefiles are generally very sensitive and only tabs are allowed. 
Python and PyCharm by default use 4 spaces as tabs. 

I use Sublime or Vim to edit the file. To show whitespaces to your Sublime Text
Editor: Sublime > Preferences > Settings and add `"draw_white_space": "all"`.

e.g Looks like this:
```json
{
	"ignored_packages":
	[
		"Vintage"
	],
	"draw_white_space": "all"
}
```

To fix the file in case it gives a missing seperator error, 
use the shell command: `cat -e -t -v Makefile` which will help 
distinguish between 4 spaces and tabs.

To get a list of options, run the `make` command in the folder and it will 
list the options.

## Debugging

Log and debugging messages should show in the Cloudify UI within the execution 
details page.  
If you're looking for the logs, you can find them in the 
`/var/log/cloudify/mgmtworker/logs/` folder with the execution ID.
e.g `sudo tail -f /var/log/cloudify/mgmtworker/logs/my-eline-test1.log`.

## Tox automation validation

To trigger all validation rules use `tox`. 

Validate specific parts, e.g `tox -e validate`

## Tests

Unit tests are provided within the plugin package which are triggered through
tox or can be triggered through CLI / IDE.

The unit tests mockup the API responses and doesn't actually hit the controller.

To actually make the calls during development, change the mock patches 
to the wrong patch, which means that the calls won't be patched and the unit 
test will actually call the API. 

e.g from:
```python
@patch('requests.get')
@patch('requests.put')
```
to: 
```python
@patch('requests.session')
@patch('requests.session')
```

# Testing

## Mininet
Using the mininet topology example, provided in the examples folder, 
sending data between h101 to h303.

Uses topology project: https://pypi.org/project/topology-yaml/

Start the topology on the mininet vagrant machine:
```commandline
sudo topology-yaml mininet start topo.yml
```

The test packets can be sent through the vagrant mininet shell or 
through mininet.

Put the mininet-command.sh from the `examples/mininet/mininet-command.sh` 
at `/usr/local/bin/` with execute permission.

Then you can run the commands below that start with host or switch with 
a prefix: `sudo /usr/local/bin/mininet-command`.

e.g `h101 arp -a` > `sudo /usr/local/bin/mininet-command h101 arp -a`.

**terminal 1:** (vagrant mininet ssh terminal)
 
this will now capture packets and dump them on screen.
```commandline
sudo tcpdump -i s303-eth1
```

**terminal 2:** (vagrant mininet ssh terminal)

send packets using ping or arp.

```commandline
h101 arp -a
h101 ping s303
```

### Sending limited number of packets 

** terminal 1:** (mininet)

receive 10 packets.

```commandline
h303 scapyrecv icmp -i h303-eth0 -c 10 -p 10
```

** terminal 2:** (mininet)

send 5 packets. run twice.

```commandline
h101 scapysend 'Ether() / IP() / ICMP()' -c 5 --iface h101-eth0
```

### Other mininet commands and notes


Some other useful commands to test with:
```
mininet> dump-all
mininet> nodes list
mininet> s101 ping s303
mininet> h101 ping h303
mininet> pingall
h101 scapysend 'Ether() / IP() / ICMP()' -c 5 --if
```

mininet default credentials: `mininet / mininet`