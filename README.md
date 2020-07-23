# PwnBin


## What is PwnBin
PwnBin is a webcrawler which searches public pastebins for specified keywords.  
All pastes are then wrote to file after finishing program main loop. Run for ever by default.  
Email alerts can be sent when finishing program main loop.  

## Install

    git clone https://github.com/kahunalu/pwnbin.git
    cd pwnbin
    python3 -m pip install -r requirements.txt


## How to use PwnBin
  
  Basic usage:
  
    python3 pwnbin.py -k <keyword1>,"example substring",<keyword2>..... -o <outputfile>
  
  Main arguments

    -k <keyword1>,<keyword2> Terms to search in pastes. Default "ssh,pass,key,token".
    -o <filepath> Logfile. Default "log.txt"
  
  Email alerts

    -c <filepath>, Mail server configuration file (see mail.conf)
    -e <email1>,<email2>... Mail alerts recipients

  Logfile

  	-a, Append to file instead of overwriting file.
  
  Exit condiftions

  	-t <time in seconds>, Run for time in seconds.
  	-n <integer>, Run for number of pastes.
  	-m <integer>, Run for number of matches.

  Main loop sleep

    -w <time in seconds>, Main loop wait time. Default 30 seconds.
  

    
  Browser emulation options

    -s, Use selenium to emulate web browser to minimize 403.
    -v, Use virtual display. Implies -s. Require Xvbf.

To use selenium `-s`:  
- Download [chromedriver](https://sites.google.com/a/chromium.org/chromedriver/)
- Copy it in your **PATH**.  
- For Raspberry Pi: Download and install armv7l version from https://github.com/electron/electron/releases/.  

To use selenium without screen `-v`, virtual display (Linux only):  
- Install [xvbf](https://howtoinstall.co/en/ubuntu/xenial/xvfb)

## Install PwnBin as a linux service with `systemctl`

Create and configure the service file `/lib/systemd/system/pwnbin.service`
```bash
nano /lib/systemd/system/pwnbin.service
```
Adjust `ExecStart` and `User` in the following template service file. 
Do not use `-t`, `-n` or `-m` flags, the goal is to have the script run for ever.  

```
[Unit]
Description=pwnbin
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=3600
ExecStart=/usr/bin/python3 /path/to/pwnbin/pwnbin.py -k <keyword1>,<keyword2> -o /path/to/pwnbin/log.txt -c /path/to/pwnbin/mail.conf -e me@gmail.com,you@gmail.com
User=user

[Install]
WantedBy=multi-user.target
```

Enable the service to start on boot
```
systemctl daemon-reload
systemctl enable pwnbin.service
```

The service can be started/stopped with the following commands:
```
systemctl start pwnbin
systemctl stop pwnbin
```  

Follow logs
```
journalctl -u pwnbin -f
```
[More infos on systemctl](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-managing_services_with_systemd-unit_files) 


## License

The MIT License (MIT)						 Copyright (c) 2015 Luke Mclaren

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
