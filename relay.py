import gpiozero

# used to track the current state of the relay. At the start, the
# application turns the relay off then sets this variable's value
# the application can then later query this to determine what the
# current state is for the relay, in the toggle function for example
_relay_status = False

# set this variable to the pin the relay is connected to
RELAY_PIN = 18

# initialize the relay object
relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)


def status():
    return _relay_status


def set_status(the_status):
    # sets the relay's status based on the boolean value passed to the function
    # a value of True turns the relay on, a value of False turns the relay off
    global _relay_status

    _relay_status = the_status

    if the_status:
        print("Setting relay: ON")
        relay.on()
    else:
        print("Setting relay: OFF")
        relay.off()


def toggle():
    # toggles the relay's status. If the relay is on, when you call this function,
    # it will turn the relay off. If the relay is off, when you call this function,
    # it will turn the relay on. Easy peasy, right?
    global _relay_status

    # flip our relay status value
    _relay_status = not _relay_status
    if _relay_status:
        print("Toggling relay: ON")
    else:
        print("Toggling relay: OFF")
    relay.toggle()
