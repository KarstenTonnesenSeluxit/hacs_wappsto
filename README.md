# hacs_wappsto
Integration Wappsto in HACS

It is required that you have HACS installed in Home Assistant for you to use this integration.

## Setup
Go to the HACS tap, and choose custom integration, and enter the github url for this library.
You have to restart Home Assistant after this step.
Then go to Settings and install the Wappsto integration.

## Setup Wappsto
First login with an existing email and password from wappsto.com

This creates a Network on Wappsto.com, and a value for where you can see that it is online.

After this you can use integration-> settings menu to choose which entity id's you would like to forward to Wappsto.
If the entity has a device it will be grouped under that and if not it will go in the default device.

If the entity does not show up, the entity type is maybe not supported yet.

Friendly names are unfortunately not an option at the moment, sorry.
