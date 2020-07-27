#!/usr/bin/env python
import sys
import confply

if __name__ == "__main__":
    in_args = sys.argv[1:]
    
    confply.log.normal("called with args: "+str(in_args))
    for arg in in_args:
        cmd = confply.command(arg)
        cmd.print_config()
        cmd.run()
