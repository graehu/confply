#!../confply.py --in
# generated using:
# python ../confply.py --config cpp_compiler cpp_compiler.cpp.py
import sys
sys.path.append('..')
import confply.cpp_compiler.config as config
import confply.cpp_compiler.options as options
import confply.log as log
############# modify_below ################

config.confply.log_topic = "cpp_compiler"
log.normal("loading cpp_compiler with confply_args: "+str(config.confply.args))

config.source_files = ["main.cpp"]
if config.confply.platform == "windows":
    config.output_file = "hello_confply.exe"
else:
    config.output_file = "hello_confply"
config.link_libraries = ["stdc++"]
config.standard = options.standard.cpp17
config.warnings = options.warnings.all_warnings
config.confply.log_config = True
config.position_independent = True
def post_run():
    import subprocess
    import sys
    if config.confply.platform == "windows":
        cmd = ["hello_confply.exe"]
    else:
        cmd = ["./hello_confply"]
    subprocess.run(cmd,
                   stdout=sys.stdout,
                   stderr=subprocess.STDOUT)
    pass

config.confply.post_run = post_run
