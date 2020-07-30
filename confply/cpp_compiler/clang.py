import confply.log as log

def generate(config):
    command = "clang "

    if config["include_paths"]:
        for include in config["include_paths"]:
            command += "-I" + include + " "

    if config["debug_info"]:
        command += "-g "
        
    if config["standard"] != None:
        command += "-std="+str(config["standard"]) + " "

    if config["warnings"] != None:
        for w in config["warnings"]:
            command += "-W"+w+" "

    if config["source_files"]:
        for source in config["source_files"]:
            command += source + " "

    if config["output_file"]:
        command += "-o "+config["output_file"] + " "
    else:
        command += "-o app.exe"

    if config["link_libraries"]:
        for link in config["link_libraries"]:
            command += "-l" + link + " "

    if config["library_paths"]:
        for library in config["library_paths"]:
            command += library + " "

    return command
