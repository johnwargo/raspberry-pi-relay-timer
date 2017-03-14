# Raspberry Pi Relay Timer

I've been doing a lot of relay-based projects lately; building several light timer projects. The first couple used Arduino-class devices, simple relays and provided the ability to set multiple on and off times throughout the day, just like those $10 power timers you can buy anywhere. These projects give me the ability to turn my Christmas lights at sundown and off when I go to bed, but not much more. 

What I really wanted though, is a way to have the lights turn on and off randomly (during specific time periods) to more accurately simulate me being home when I'm not. Products may exist that do this, but I've not seen any, so I decided to make my own. This repository contains the code for this project. 

> **Note**: You can use this code for your own, personal projects, but if you make a commercial product that does this, can you share the love (10% for example)?

## Hardware Components

To use this project, you'll need at a minimum the following hardware components:

+ [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/)
+ A compatible relay/relay board (see below)
+ 5V, 2.5A Micro USB power source (basically, a smartphone charger) - I use the [CanaKit 5V 2.5A Raspberry Pi 3 Power Supply/Adapter/Charger](https://www.amazon.com/gp/product/B00MARDJZ4)
+ An enclosure for the Raspberry Pi and relay. 
 
For the relay, I used the [1-channel relay board](http://www.yourduino.com/sunshop/index.php?l=product_detail&p=181) from yourduino.com. The boards they're selling now are different than the ones I had lying around. They have a really good [relay tutorial](http://arduino-info.wikispaces.com/ArduinoPower) on their web site; even though it's geared primarily at Arduino users, it's still a lot of good information. Amazon.com also has a good [selection of relay boards](https://www.amazon.com/s/ref=nb_sb_noss_1?url=search-alias%3Daps&field-keywords=1+channel+relay) you can use as well.

## Configuring Your Raspberry Pi

Download the latest version of the Raspbian OS from the [Raspberry Pi web site](https://www.raspberrypi.org/downloads/raspbian/) and follow the [instructions](https://www.raspberrypi.org/documentation/installation/installing-images/README.md) for writing the OS image to a Micro SD card for the Pi. Insert the **SD card** in the Pi, connect **Ethernet**, **keyboard**, **mouse**, and a **monitor** to the Pi and finally **power it up** using a smartphone charger or some suitable power source.

The first thing you'll want to do is open the **Raspberry Pi menu** (in the upper-left corner of the screen), select **Preferences**, then **Raspberry Pi Configuration** as shown in the following figure:

![Assembly](screenshots/figure-01.png)

Raspbian comes configured with its **keyboard**, **timezone**, and other **locale** settings configured for the United Kingdom (UK), so if you're in the US, or elsewhere that's not the UK, you'll want to switch over to the **localisation** tab and adjust the settings there as well.

When you're done configuring locale settings, you'll likely be prompted to reboot the Pi. Go ahead and do that before continuing. 

When the Pi comes back up, open a terminal window and execute the following command:

	sudo apt-get update

This updates the local catalog of application repositories. Next, execute the following command:

	sudo apt-get upgrade

This command updates the Raspbian OS with all updates released after the latest image was published. The update process may take a long time, so pay attention, answer any prompts, and expect this process to take a few minutes or more (the last time I did this, it took about 15 minutes or more to complete).

Next, install some Python libraries used by the project; in the same terminal window, execute the following command:

    sudo pip install pytz tzlocal numpy
        
Now, lets download and project code; still in the same terminal window (almost done now), execute the following command:

	git clone https://github.com/johnwargo/raspberry-pi-relay-timer

This downloads the project's code from its Github repository and copies the files to the local (relative to your terminal window) `raspberry-pi-relay-timer` folder. When it's done, you'll find the following files in the new folder:

+	`controller.py` - The project's main application file. You'll run this program to start the relay controller.
+	`LICENSE` - The MIT license for the application. You're free to use this code as you see fit, but, like I said, if you make a commercial product out of this, share the love (with me, of course).
+	`readme.md` - This file.
+	`relay.py` - A simple Python module that exposes the capabilities the application needs to control the relay. I broke this out into a separate module to make it easier for you to use my code in other projects.
+	`relay-test.py` - A Python application that I built to help me write and test the `relay.py` module. You can run it to make sure your hardware works correctly.
+	`solar-times.py` - A simple Python application I wrote to help me write and test the code that connects to a web service to determine sunrise and sunset times for the current location. This code is also in the `controller.py` file.
+	`start-controller.sh` - A shell script you'll use to configure the Pi to start the controller application on start up.

## Customizing the Controller Application

If you look in the project's `controller.py` file, you'll find an area neat the top of the file that contains configuration settings I'm expecting you to update to make this application work for your configuration. It will look something like this:

	# ============================================================================
	# User (that's you) adjustable variables
	# ============================================================================
	# adjust these variables based on your particular hardware configuration
	
I'll describe each of the settings components in the following sub-sections.

### Button Pin


	# set this variable to the button pin used in your implementation
	BUTTON_PIN = 19

### Relay Pin


	# set this variable to the GPIO pin the relay is connected to
	RELAY_PIN = 18

### Location


	# Sunrise and sunset times vary depending on location, so...
	# If using sunrise or sunset as trigger options, populate the locLat
	# and locLong values with the location's latitude and longitude values
	# These values are for Charlotte, NC, to get Sunrise/Sunset values for
	# your location, replace these strings with the appropriate values for
	# your location.
	LOC_LAT = "35.227085"
	LOC_LONG = "-80.843124"


### Default Solar Times


	# default times for sunrise and sunset. If solar data is enabled, the
	# code will reach out every day at 12:01 and populate these values with
	# the correct values for the current day. If this fails for any reason,
	# the values will fall back to the previous day's values, or, finally,
	# these values
	time_sunrise = 700
	time_sunset = 1900

### Time Slots


	# Slots array defines time windows and behavior for the relay
	# format: [ OnTrigger, OnValue, OffTrigger, OffValue, doRandom]
	slots = np.array(
	    # ONLY modify the following array with your time settings
	    [
	        (SETTIME, 700, SETTIME, 900, False),
	        (SETTIME, 1700, SETTIME, 2300, True),
	        (SUNRISE, 15, SUNSET, -10, True)
	    ],
	    # leave the rest of this alone
	    dtype=[
	        ('onTrigger', np.dtype(int)),
	        ('onValue', np.dtype(int)),
	        ('offTrigger', np.dtype(int)),
	        ('offValue', np.dtype(int)),
	        ('doRandom', np.dtype(bool))
	    ]
	)

## Starting the Controller

Open a terminal window, and change to the project folder using the following command:

	cd raspberry-pi-relay-timer

Your terminal window prompt should change to reflect the switch to the new folder. Now, let start the server application. In the terminal window pointing to the `raspberry-pi-relay-timer` folder (you changed to this folder with the last command you typed), execute the following command:

	python ./controller.py

The controller process will start and begin managing the relay using the time slots you selected.

![The controller in action](screenshots/figure-02.png)
 
## Starting The Controller Server Process Automatically

Right now, the server is only running because you started it manually. There are a few steps you must complete to configure the Raspberry Pi so it executes the the relay controller app on startup. You can read more about this here: [Autostart Python App on Raspberry Pi in a Terminal Window](http://johnwargo.com/index.php/microcontrollers-single-board-computers/autostart-python-app-on-raspberry-pi-in-a-terminal-window.html).

If you don't already have a terminal window open, open one then navigate to the folder where you extracted the project files (if you followed these instructions, it should be at `home/pi/raspberry-pi-relay-timer`. 

1.	Make the project's bash script file (`start-controller.sh`) executable by executing the following command:

    	chmod +x start-controller.sh
    
2.	Open the pi user's session autostart file using the following command:  

		sudo nano ~/.config/lxsession/LXDE-pi/autostart    

3.	Add the following line to the end (bottom) of the file:

		@lxterminal -e /home/pi/raspberry-pi-relay-timer/start-controller.sh

	To save your changes, press `ctrl-o` then press the Enter key. Next, press `ctrl-x` to exit the `nano` application.
  
4.	Reboot the Raspberry Pi; when it restarts, the controller server process should execute in its own terminal window.

## Update History

Nothing yet.

***
By [John M. Wargo](http://www.johnwargo.com) - If you find this code useful, and feel like thanking me for providing it, please consider making a purchase from [my Amazon Wish List](https://amzn.com/w/1WI6AAUKPT5P9). You can find information on many different topics on my [personal blog](http://www.johnwargo.com). Learn about all of my publications at [John Wargo Books](http://www.johnwargobooks.com). 