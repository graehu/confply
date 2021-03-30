#!/usr/bin/env python
import os
import sys
import confply
import confply.log as log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    version = sys.version_info
    version = (version.major, version.minor, version.micro)
    if "--no_header" not in in_args:
        log.confply_header()
        log.linebreak()
        log.normal("python"+str(version))
        log.normal("date: "+str(confply.datetime.now()))
    if(version[0] < 3 or (version[0] == 3 and version[1] < 8)):
        log.error("python version must be 3.8 or above")
        log.linebreak()
        exit(1)

    log.normal("called with args: "+str(in_args))
    return_code = -999999
    if len(in_args) != 0:
        while len(in_args) > 0:
            cmd_return = confply.run_config(in_args)

            if(cmd_return > return_code and cmd_return != 0):
                return_code = cmd_return

            # fatal error.
            if return_code == -1:
                log.linebreak()
                # failed to run command
                exit(1)
    else:
        log.error("no arguements supplied.")
        confply_dir = os.path.relpath(__file__)
        confply_dir = os.path.dirname(confply_dir)
        return_code = -1

        with open(os.path.join(confply_dir, "help.md")) as help_file:
            print("\n"+help_file.read())
    log.linebreak()
    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)
