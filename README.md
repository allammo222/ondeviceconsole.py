# ondeviceconsole.py
iOS on-device Console written in Python.

- Allows you to live-view the syslog
- Filter by Process Name (e.g "SpringBoard") **or** PID (e.g 123)
  - even a combination of both works e.g SpringBoard,123
- Highlight certain words in syslog

## Usage:

```
-h, --help            show this help message and exit

-p PROCESS, --process=PROCESS
                        filter out this process name
                        
--highlight=HIGHLIGHT
                        highlight certain classes
```
                        
## More Cool Stuff

Check out [eswick's Objective-C implementation](https://github.com/eswick/ondeviceconsole) from which this code makes use of.
