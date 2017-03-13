#!/usr/bin/python

from __future__ import print_function


def main_loop():
    slots = []
    print(slots)
    slots.append([700, 1300])
    print(slots)
    slots.append([1700, 2100])
    print(slots)

    slot = slots[0]
    print(slot)
    print(slot[0])
    print(slot[1])

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nExiting application\n")
        # exit the application
        sys.exit(0)
