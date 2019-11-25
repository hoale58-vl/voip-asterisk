# Firmware
Raspbian for zero H2 v0_1
PATH=$PATH:/sbin
export PATH

# Connect WiFi
- sudo nmtui

# Disable IPv6
- sudo vim /etc/sysctl.d/10-ipv6-privacy.conf
net.ipv6.conf.all.disable_ipv6=1

# Issue Extension board
- Add 2 line to /etc/modules
sun4i_codec
sun8i_codec_analog 

- armbian-config
-> System -> Hardware -> Enable (Analog Codec)


# Issue Apt Repos
- Comment out /etc/apt/sources.list
sudo nano /etc/apt/sources.list.d/armbian.list
sudo nano /etc/apt/sources.list -> jessie-backport

# Install
sudo apt-get install -y python-pip git python-dev
sudo pip install linphone4raspberry

git clone https://github.com/duxingkei33/orangepi_PC_gpio_pyH3

- Edit mapping.h -> https://github.com/duxingkei33/orangepi_PC_gpio_pyH3/issues/7 
{ "PA15", SUNXI_GPA(15), 19 },
{ "PA16", SUNXI_GPA(16), 21 },
{ "RED_LED", SUNXI_GPA(17), 0 },
{ "GREEN_LED", SUNXI_GPL(10), 0 },

sudo python setup.py install
rm -rf orangepi_PC_gpio_pyH3

sudo nano /lib/systemd/system/linphone.service
[Unit]
Description=LinPhone Service
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/black
ExecStart=/usr/bin/python /home/black/main_gpio.py
Restart=always
KillSignal=SIGQUIT

[Install]
WantedBy=multi-user.target

sudo systemctl enable linphone
sudo systemctl start linphone