#!/usr/bin/env python
import os
import sys
import stat
import confply
import confply.log as log

if __name__ == "__main__":
    in_args = sys.argv[1:]
    log.confply_header()
    log.linebreak()    
    log.normal("called with args: "+str(in_args))
    
    for i, arg in enumerate(in_args):
        if arg.startswith("--"):

            option = in_args.pop(i)
            arguement = in_args.pop(i)
            if option == "--launcher":
                confply_dir = os.path.relpath(__file__)
                confply_dir = os.path.dirname(confply_dir)
                launcher_path = os.path.abspath(os.path.curdir)+"/"+arguement
                if not os.path.exists(launcher_path):
                    with open(launcher_path, "w") as launcher_file:
                        launcher_str = confply.launcher_str.format_map(
                            {
                                "confply_dir":confply_dir,
                                "launcher":arguement,
                                "comment":"{\n    #'mycommand':'path/to/command.py'\n}"
                            })
                        launcher_file.write(launcher_str)
                    st = os.stat(launcher_path)
                    os.chmod(launcher_path, st.st_mode | stat.S_IEXEC)
                    log.success("wrote: "+launcher_path)
                else:
                    log.error(launcher_path+" already exists!")
    
    for arg in in_args:
        log.linebreak()
        cmd = confply.command(arg)
        cmd.run()
    log.linebreak()
