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
    while len(in_args) > 0:
        if in_args[0].startswith("--"):
            option = in_args.pop(0)
            if option == "--launcher":
                confply.handle_launcher_arg(in_args)
            elif option == "--config":
                confply.handle_config_arg(in_args)
            elif option == "--help":
                confply.handle_help_arg(in_args)
            continue

        # default assume it's a file to run.
        log.linebreak()
        cmd = confply.command(in_args)
        cmd.run()
    log.linebreak()



