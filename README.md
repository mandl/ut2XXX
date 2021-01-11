# Simple DSO

This program is useful with UNI-T digital storage oscilloscopes UT2XXX or UT3XXX.
It's intended to be a replace for original software, which doesn't work under Linux.

Requires pyQT5, QT 5, python 3, libusb and usb python module.

If your device is not found, you can add VID and PID to vid_pid.txt file and restart program. 
VID and PID is in decimal NOT hexadecimal !

https://sourceforge.net/p/simpledso/wiki/Home/


This woks with a UTD2202CE

# Install  Ubuntu 20.08 TLS

    sudo apt-get install python-qt5

    sudo apt install pyqt5-dev-tools

    sudo pip3 install pyusb

    
    sudo pip install pyuic5-tool

# Install udev rules

    99-uni-t.rules
  
# Run


Start with some debug output.

    ./simpleDSO.py -v


    INFO: DSO remote app is starting ...
    INFO: DSO remote app started.
    INFO: Loaded VID/PIDS are:
    INFO: VIDs -> [22102, 22102, 22103, 22102]
    INFO: PIDs -> [2098, 2098, 2002, 2100]
    INFO: Found UNI-T DSO on USB:
    INFO: idVendor: 22102
    INFO: idProduct: 2100
    INFO:     Alternate Setting: 0
    INFO:       Interface class: 255
    INFO:       Interface sub class: 0
    INFO:       Interface protocol: 0
    INFO:       Endpoint: 0x82
    INFO:         Type: 2
    INFO:         Max packet size: 512
    INFO:         Interval: 0
    INFO:       Endpoint: 0x6
    INFO:         Type: 2
    INFO:         Max packet size: 512
    INFO:         Interval: 0
    INFO: Dbg: Device is presented
    INFO: Dbg: device opened
    
# Screenshots

Get a bitmap from DSO.


![Screenshot](./screenshot/1.png)

Get live data from DSO.

![Screenshot](./screenshot/2.png)





lsusb -v



    Bus 001 Device 013: ID 5656:0834 Uni-Trend Group Limited DSO          
    Device Descriptor:
    bLength                18
    bDescriptorType         1
    bcdUSB               2.00
    bDeviceClass            0 
    bDeviceSubClass         0 
    bDeviceProtocol         0 
    bMaxPacketSize0        64
    idVendor           0x5656 Uni-Trend Group Limited
    idProduct          0x0834 
    bcdDevice            0.00
    iManufacturer           1 DSO    
    iProduct                2 DSO          
    iSerial                 0 
    bNumConfigurations      1
    Configuration Descriptor:
        bLength                 9
        bDescriptorType         2
        wTotalLength       0x0020
        bNumInterfaces          1
        bConfigurationValue     1
        iConfiguration          0 
        bmAttributes         0x40
        (Missing must-be-set bit!)
        Self Powered
        MaxPower              100mA
        Interface Descriptor:
        bLength                 9
        bDescriptorType         4
        bInterfaceNumber        0
        bAlternateSetting       0
        bNumEndpoints           2
        bInterfaceClass       255 Vendor Specific Class
        bInterfaceSubClass      0 
        bInterfaceProtocol      0 
        iInterface              0 
        Endpoint Descriptor:
            bLength                 7
            bDescriptorType         5
            bEndpointAddress     0x82  EP 2 IN
            bmAttributes            2
            Transfer Type            Bulk
            Synch Type               None
            Usage Type               Data
            wMaxPacketSize     0x0200  1x 512 bytes
            bInterval               0
        Endpoint Descriptor:
            bLength                 7
            bDescriptorType         5
            bEndpointAddress     0x06  EP 6 OUT
            bmAttributes            2
            Transfer Type            Bulk
            Synch Type               None
            Usage Type               Data
            wMaxPacketSize     0x0200  1x 512 bytes
            bInterval               0
    Device Qualifier (for other device speed):
    bLength                10
    bDescriptorType         6
    bcdUSB               2.00
    bDeviceClass            0 
    bDeviceSubClass         0 
    bDeviceProtocol         0 
    bMaxPacketSize0        64
    bNumConfigurations      1
   
