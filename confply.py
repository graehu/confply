#!/usr/bin/env python
import os
import sys
import confply
import confply.log as log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    version = sys.version_info
    version = (version.major, version.minor, version.micro)
    if not "--no_header" in in_args:
        log.confply_header()
        log.linebreak()
        log.normal("python"+str(version))
    if(version[0] < 3 or (version[0] == 3 and version[1] < 6)):
        log.error("python version must be 3.6 or above")
        log.linebreak()
        exit(1)
    log.normal("called with args: "+str(in_args))
    return_code = -999999
    if len(in_args) != 0:
        while len(in_args) > 0:
            if in_args[0].startswith("--"):
                option = in_args.pop(0)
                if option == "--launcher":
                    confply.handle_launcher_arg(in_args)
                elif option == "--gen_config":
                    confply.handle_gen_config_arg(in_args)
                elif option == "--help":
                    confply.handle_help_arg(in_args)
                # #todo: add --config "{'confply':{'tool':'gcc'}, 'warnings':None}"
                elif option == "--config":
                    confply.handle_config_arg(in_args)
                    pass
                continue

            # default assume it's a file to run.
            log.linebreak()
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
        
        with open(os.path.join(confply_dir,"help.md"), "r") as help_file:
            print("\n"+help_file.read())
    log.linebreak()
    if(return_code != -999999):
        exit(abs(return_code))
    else:
        exit(0)
