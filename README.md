# BluetoothDucky
CVE-2023-45866 - BluetoothDucky implementation (Using DuckyScript)

This is an implementation of the CVE discovered by marcnewlin 
[https://github.com/marcnewlin/hi_my_name_is_keyboard]

- I have created a ducky_convert.py to try not to modify the hid.py file as much as I can for future usage.
- Still working on a few payload ideas for it.

- I have it running on a Raspberry Pi 4 using the default bluetooth module in it. I have tested it against every single phone my friends have, and it works. The only issue I have found is with an NZ based phone brand called Vodafone which blocks it by default even though the phone hasn't been turned on in years (Asks for pairing) which is hilarious that is the most secure one. 

Still have to adjust for ALL ducky related wording/terms but limited on devices for testing.

```bash
REM this is just a comment
string test123
ENTER
```

That should type in test123 in a text field and then press ENTER. 


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
