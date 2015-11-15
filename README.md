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
