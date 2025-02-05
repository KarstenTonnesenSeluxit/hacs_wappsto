# Deprecated!  No longer maintained.

# Wappsto value forwarder - integrated via HACS

It is required that you have HACS installed in Home Assistant for you to use this integration.
See https://hacs.xyz/ for more information.

## Setup HACS Integration
* Go to the HACS tap, and click "Integrations"
* Click the 3 dots in the top right corner and choose "Custom repositories"
* Enter [https://github.com/Wappsto/hacs_wappsto](https://github.com/Wappsto/hacs_wappsto) in the "Repository" field
* Select "Integration" in the "Category" drop down menu.

You have to restart Home Assistant after this step, and HACS should warn you about this.

## Add Wappsto Integration
* After restart goto Settings -> Devices & Services, and click the "ADD INTEGRATION" button in the lower right corner.
* Search for Wappsto in the list and add/install it.
* If asked for email and password for Wappsto, enter these - if you do not have an account on Wappsto.com you will have to create it first.
* If you do not get asked about email/password, click the Wappsto integration and click "ADD ENTRY" to get the option

This creates a Network on Wappsto.com, and a value for where you can see that it is online.

## Configuring the integration

* After this you can use integration-> "CONFIGURE" menu to choose which entity id's you would like to forward to Wappsto.

Expected behavior at the moment:
* If the entity has a device it will be grouped under that and if not it will go in the "Default device".
* If the entity does not show up, the entity type is maybe not supported yet.
* Friendly names are unfortunately not an option at the moment, sorry.
