import os
import importlib

tools = {}

# todo: valid tools exist, have a dependency checker in clang.py, cl.py, gcc.py etc.
def generate(config):
    if len(tools) == 0:
        command = "confply."+config["confply_command"]+"."
        dir = os.path.dirname(__file__)
        print(dir.split("confply")[-1])
        files = os.listdir(dir)
        
        for py in files:
            if py.endswith(".py") and not (py == "config.py" or py == "command.py"):
                tool = py[0:-3]
                tools[tool] = importlib.import_module(command+tool)
                
    if config["confply_tool"] in tools:
        return tools[config["confply_tool"]].generate(config)

    return None

