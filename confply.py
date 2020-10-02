#!/usr/bin/env python
import os
import sys
import confply
import confply.log as log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    log.confply_header()
    log.linebreak()
    version = sys.version_info
    version = (version.major, version.minor, version.micro)
    log.normal("python"+str(version))
    if(version[0] < 3 or (version[0] == 3 and version[1] < 6)):
        log.error("python version must be 3.6 or above")
        log.linebreak()
        exit(1)
    log.normal("called with args: "+str(in_args))
    return_code = -999999
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
        cmd_return = cmd.run()
        
        if(cmd_return > return_code and cmd_return != 0):
            return_code = cmd_return
        
        # fatal error.
        if return_code == -1:
            log.linebreak()
            # failed to run command
            exit(1)
            

    log.linebreak()
    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)
