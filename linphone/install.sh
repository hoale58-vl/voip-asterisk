#!/bin/bash
cp ./voip.service /lib/systemd/system/
systemctl enable voip
mkdir /usr/local/voip
cp ./src/* /usr/local/voip/
mkdir /etc/voip/
cp config /etc/voip/

# Install dependency
dpkg -R --install deb/

cd gpio/orangepi_PC_gpio_pyH3/
/usr/bin/python setup.py install
cd ../../pip/
/usr/bin/pip install linphone4raspberry-3.9.0-cp27-none-any.whl

systemctl start voip
