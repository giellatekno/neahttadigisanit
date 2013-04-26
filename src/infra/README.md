Infrastructure notes
--------------------

Configuring Neahttadigisánit for server installation has some requirements.
Here are some example files to help the process.

## Contents

 * nds.nginx.conf - An example config file that connects to a flup fastcgi
   process launched by manage.py runfcgi

 * nds-sanit - An example init.d service definition

 * nginx/ - contains include files required for nds.nginx.conf, but be sure to
   check everything before implementing it in an actual installation. Some
   names and variables are changed to be general or vague.

## Automatically restarting processes

TODO: rewrite for fedora

### chkconfig

After defining an init.d service, the service must be regitered with chkconfig.
In order for chkconfig to recognize an init.d service definition, the first
lines must contain comments of the following general structure:

    # chkconfig: 2345 95 20
    # description: NDS Sánit instance 
    # processname: nds-sanit

Then, the process may be registered (NAME matching the processname:

	sudo chkconfig --add NAME
	sudo chkconfig --levels 2345 lookupserv on

This will ensure that when the server is restarted, the fastcgi process is
started automatically.

