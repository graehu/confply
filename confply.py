#!/usr/bin/env python
import os
import sys
import confply
import confply.log as log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    log.confply_header()
    log.linebreak()    
    log.normal("called with args: "+str(in_args))
    for arg in in_args:
        if arg.startswith("--"):
            option = in_args.pop(0)
            if option == "--launcher":
                confply.handle_launcher_arg(in_args)
            elif option == "--config":
                confply.handle_config_arg(in_args)
            continue

        # default assume it's a file to run.
        log.linebreak()
        cmd = confply.command(arg)
        cmd.run()
        in_args.pop(0)
    log.linebreak()



