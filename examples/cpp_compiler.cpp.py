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
config.output_file = "hello_confply"
config.link_libraries = ["stdc++"]
config.standard = options.standard.cpp17
config.warnings = options.warnings.all_warnings
config.confply.log_config = True
def post_run():
    import subprocess
    import sys
    subprocess.run("./hello_confply",
                   stdout=sys.stdout,
                   stderr=subprocess.STDOUT,
                   shell=True)
    pass

config.confply.post_run = post_run
