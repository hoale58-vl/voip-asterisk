# VoIP server for Japan Raspberry Smart Speaker.
**[Asterisk Docs](http://asterisk-service.com/downloads/Asterisk-%20The%20Definitive%20Guide,%204th%20Edition.pdf)**  
**[GG Docs](https://docs.google.com/document/d/13xg8OiiVBLtOipUFVUNQc5p9_y1YaaGH10Czpy4asGo/edit?usp=sharing)**  
[SIP Basic Explained](https://www.youtube.com/watch?v=erICfPV8-Lg)  

# 1. Asterisk installation from scratch
- Ubuntu 18.04 LTS
- Asterisk 16.4
- **Replace username (hiep) of yours**

## 1.1 Necessary package
```
sudo apt-get install ntp
sudo /etc/init.d/ntp restart
sudo apt-get install linux-headers-$(uname -r)
sudo apt-get install gcc g++ make build-essential subversion libncurses5-dev libssl-dev libxml2-dev libsqlite3-dev uuid-dev vim-nox libnewt-dev libedit* libjansson* autoconf libelf-dev libtool
mkdir -p ~/src
```

## 1.2 DAHDI installation
[Asterisk 16.4.0](https://downloads.asterisk.org/pub/telephony/asterisk/old-releases/asterisk-16.4.0.tar.gz)  
```
cd ~/src
wget http://downloads.asterisk.org/pub/telephony/dahdi-linux-complete/dahdi-linux-complete-3.1.0-rc1+3.1.0-rc1.tar.gz
tar -xvzf dahdi-linux-complete-3.1.0-rc1+3.1.0-rc1.tar.gz
mv dahdi-linux-complete-3.1.0-rc1+3.1.0-rc1 dahdi-linux-complete-3.1.0
cd dahdi-linux-complete-3.1.0
make all
sudo make install
```

## 1.3 LibPRI installation
```
cd ~/src
wget http://downloads.asterisk.org/pub/telephony/libpri/libpri-1.6.0.tar.gz
tar -xvzf libpri-1.6.0.tar.gz
cd libpri-1.6.0
make
sudo make install
```


## 1.4 Build Asterisk
```

cd ~/src
wget http://downloads.asterisk.org/pub/telephony/asterisk/asterisk-16-current.tar.gz
tar -xvzf asterisk-16-current.tar.gz
mv asterisk-16.5.0 asterisk
cd asterisk
sudo ./contrib/scripts/install_prereq install
sudo ./contrib/scripts/install_prereq install-unpackaged
./configure
make
```
- If have **warning**, clear ```/usr/lib/asterisk/modules```
```
sudo make install
sudo make config
```

## 1.5 ***Install Extra Sounds Packages from menuselect***
```
make menuselect
menuselect/menuselect --enable-all menuselect.makeopts
sudo make install
```

## 1.6 Asterisk files permission
```
sudo chown -R hiep:hiep /var/run/asterisk/
sudo chown -R hiep:hiep /var/lib/asterisk/
sudo chown -R hiep:hiep /var/spool/asterisk/
sudo chown -R hiep:hiep /var/log/asterisk/
sudo chown -R hiep:hiep /etc/asterisk

```

## 1.7 Create the /etc/asterisk directory and copy the indications.conf sample file into it
```
sudo mkdir -p /etc/asterisk
sudo chown hiep:hiep /etc/asterisk
cd /etc/asterisk/
cp ~/src/asterisk/configs/samples/indications.conf.sample ./indications.conf
cp ~/src/asterisk/configs/samples/asterisk.conf.sample ./asterisk.conf
```

## 1.8 Add .conf files (examples config for test)
```
cd /etc/asterisk/
cp ~/voip_system/asterisk/config/modules.conf ./modules.conf
cp ~/voip_system/asterisk/config/musiconhold.conf ./musiconhold.conf
nano /etc/asterisk/asterisk.conf
runuser=hiep
rungroup=hiep
```

## 1.9 Asterisk Command Test
```
/usr/sbin/asterisk -cvvv
asterisk -cddd
asterisk -r
module show
core stop now
```

# 2. Menu select
## 2.1 Interfaces
```
cd ~/src/asterisk
make menuselect
```
- Choose needed package -> install your new prompts by downloading them from the Asterisk downloads site  
  - Sound files is on ```/var/lib/asterisk/sounds/```   
```
sudo make install
sudo chown -R hiep:hiep /var/lib/asterisk/sounds/
```

## 2.1 Scripting Automate process
- Installation process
  - Execute the configure script in order to determine what dependencies are installed on the system
  - Build the menuselect application
  - Run ```make menuselect-tree``` command to build the initial tree structure
  - **Any time you install additional packages, you will need to run the ```./configure``` script in your Asterisk source in order for the new package to be detected.**
```
./configure
cd menuselect
make menuselect
cd ..
make menuselect-tree
menuselect/menuselect --help
menuselect/menuselect --disable-all menuselect.makeopts
menuselect/menuselect --disable-all --enable chan_sip --enable app_dial menuselect.makeopts
menuselect/menuselect --enable-all menuselect.makeopts
```
- See ```menuselect.makeopts``` (module will not be built)

# 3. Initial Configuration
- Default location: ```/etc/asterisk```

- **asterisk.conf**: affect how Asterisk runs as a whole
  - [directories]: ***(!)*** that marks it as a template (meaning changes under this header will not take effect)
  - [options]: global runtime options - use ```man asterisk``` for details
  - [files]: options related to the Asterisk control socket
  - [compat]: contains some options that allow reverting behavior of certain modules back to previous behavior

- **modules.conf**: without any modules Asterisk won’t really be able to do anything
  - If ```autoload=yes```, all modules in the ```/usr/lib/asterisk/modules``` will be loaded at startup.
  - Can be controled by ```make menuselect```
  - [modules]: contains a single

- **indications.conf**: defines the parameters for the various sounds that a telephone system might be expected to produce, and allows you to customize them

- **musiconhold.conf**: convert to easier format for CPU
```
sudo apt-get install sox libsox-fmt-all mpg321
sox sample_moh.mp3 --type raw --rate 8000 --show-progress --channels 1 sample_moh.sln
cp sample_moh.sln /var/lib/asterisk/moh
asterisk -rx "module unload res_musiconhold.so"
asterisk -rx "module load res_musiconhold.so"
```
- **Another .conf files**
```
cd ~/src/asterisk

for f in acl manager udptl features ccss res_stun_monitor smdi;
do  
  cp configs/samples/$f.conf.sample /etc/asterisk/$f.conf;
done
```

## 4. User Device Configuration
- Telling **Asterisk** about the **Device**
- Telling the **Device** about **Asterisk**

## 4.2 Configuring Asterisk
- **sip.conf**:
  - [general]: common information about the channel driver
```
cp ~/voip_system/asterisk/config/sip.conf /etc/asterisk/sip.conf
asterisk -r
module load chan_sip.so
module reload chan_sip.so
sip show peers
sip show users
sip set debug on
```
- **extensions.conf** basic for test:
```
cp ~/voip_system/asterisk/config/extensions.conf /etc/asterisk/extensions.conf
dialplan reload
```

# 5. ConfBridge
[Docs](https://wiki.asterisk.org/wiki/display/AST/ConfBridge+Configuration)  
[Tutorial](https://damow.net/dynamic-conferences-with-asterisk/)  
[Tutorial 2](https://stackoverflow.com/questions/47364852/how-to-automatically-add-users-to-confbridge-asterisk-from-dialplan)  
- Config file
```
confbridge.conf
```
- CLI command
```
confbridge kick                -- Kick participants out of conference bridges.
confbridge list                -- List conference bridges and participants.
confbridge lock                -- Lock a conference.
confbridge mute                -- Mute participants.
confbridge record start        -- Start recording a conference
confbridge record stop         -- Stop recording a conference.
confbridge show menu           -- Show a conference menu
confbridge show menus          -- Show a list of conference menus
confbridge show profile bridge -- Show a conference bridge profile.
confbridge show profile bridges -- Show a list of conference bridge profiles.
confbridge show profile user   -- Show a conference user profile.
confbridge show profile users  -- Show a list of conference user profiles.
confbridge unlock              -- Unlock a conference.
confbridge unmute              -- Unmute participants.
```
- CBAnn: Announcing channel
- CBRec: Recording channel

# 6. Asterisk REST Interface
[ARI Docs](https://wiki.asterisk.org/wiki/pages/viewpage.action?pageId=29395573)  
- Config file
```
ari.conf
http.conf
```
