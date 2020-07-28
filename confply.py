#!/usr/bin/env python
import sys
import confply.log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    
    confply.log.normal("called with args: "+str(in_args))
    for arg in in_args:
        confply.log.linebreak()
        cmd = confply.command(arg)
        cmd.run()
    confply.log.linebreak()
