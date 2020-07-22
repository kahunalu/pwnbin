# PwnBin


## What is PwnBin
PwnBin is a webcrawler which searches public pastebins for specified keywords.  
All pastes are then wrote to file after program finished with predefined condition or sending completion signal Ctrl+C.  
Email alerts can be configured and are sent when finishing program main loop.  


## How to use PwnBin
  
  Basic usage:
  
    python3 pwnbin.py -k <keyword1>,"example substring",<keyword2>..... -o <outputfile>
  
  Both the keyword and outputfile arguments are optional and default to 

    -k ssh,pass,key,token
    -o log.txt

  Optional command:

  	-a, Append to file instead of overwriting file.
  	-t <time in seconds>, Run for time in seconds.
  	-n <integer>, Run for number of pastes.
  	-m <integer>, Run for number of matches.
    -c <filepath>, Mail server configuration file (see mail.conf)
    -e <email1>,<email2>... Mail alerts recipients
    -w <time in seconds>, Main loop wait time
    -s, Use selenium to emulate web browser and avoid 403. chromedriver must be in your PATH, see https://sites.google.com/a/chromium.org/chromedriver/. For Raspberry Pi: Download and install armv7l version from https://github.com/electron/electron/releases/.
    -v, Use virtual display. Implies -s. Require Xvbf, see https://stackoverflow.com/questions/21665914/installing-and-configuring-xvfb.


## Install PwnBin as a linux service (systemctl)

Still need some tweaks to be 403 proof...

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
RestartSec=300
ExecStart=/usr/bin/python3 /path/to/pwnbin/pwnbin.py -k <keyword1>,<keyword2> -c /path/to/pwnbin/mail.conf -e me@gmail.com,you@gmail.com
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
