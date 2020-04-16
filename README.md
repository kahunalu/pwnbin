# PwnBin


## What is PwnBin
  PwnBin is a webcrawler which searches public pastebins for specified keywords.
All pastes are then returned after sending completion signal ctrl+c.


## How to use PwnBin

  Basic command:

    python pwnbin.py -k <keyword1>,"example substring",<keyword2>..... -o <outputfile>

  Both the keyword and outputfile arguments are optional and default to

    -k ssh,pass,key,token
    -o log.txt

  Optional command:

  	-a, Append to file instead of overwriting file.
  	-t <time in seconds>, Run for time in seconds.
  	-n <integer>, Run for number of pastes.
  	-m <integer>, Run for number of matches.

## Support Docker

### Install Docker
For install docs use the oficial docs: [Docs Oficial](https://docs.docker.com/install/)

### Create image docker
```sh
sudo docker build -t "greenmind/pwnbin:1" .
```
> "greenmind/pwnbin:1" is name the image, but create you name. example: pwnbin:1

### Using docker
```sh
sudo docker container run -it --rm -v "${PWD}:/opt/pwnbin/" "greenmind/pwnbin:1" -k "leak,pass" -o teste2.txt
```

- sudo (For root permission)
- docker container run -it --rm (To start the container in interactive mode and remove as soon as it is finished)
- -v "${PWD}:/opt/pwnbin/" (To connect to the container we create a link because it is isolated from the host, a local link is being created for the /opt/pwnbin directory which is where it is installed)
- "greenmind/pwnbin:1" (Is the name of the image)
- -k "leak,pass" (keywords)
- -o teste2.txt (output)


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
