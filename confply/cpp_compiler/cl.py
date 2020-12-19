import os
import subprocess
import confply.config
import confply.log as log
import confply.cpp_compiler.common as common


def generate(config):
    if confply.config.confply_platform == "windows":
        common.tool = "cl"
        return common.generate(config)
    else:
        log.error("cl only supports windows platforms")
        return None


def get_environ(config):
    def find_tools():
        vswhere = '%PROGRAMFILES(X86)%/Microsoft Visual Studio/Installer'
        vswhere_exe = os.path.expandvars(vswhere)+"/vswhere.exe"
        print(vswhere_exe)
        if os.path.exists(vswhere_exe):
            envs = {"PATH": os.path.expandvars(vswhere)}
            cmd = "vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath"
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, shell=True, env=envs)
            installation_path = proc.stdout.read().decode("utf-8").rstrip()
            installation_path = installation_path.replace("/", "\\")
            vs_tools = (installation_path+"/Common7/Tools/").replace("/", "\\")
            print(vs_tools)
            return vs_tools
        else:
            print("ruh roh")
            return None
    cl_envs = os.environ.copy()
    cl_envs["PATH"] += ";"+find_tools()
    cl_envs["VSCMD_DEBUG"] = "3"
    vsdevcmd = 'cmd.exe /s /c "call vsdevcmd.bat && set"'
    proc = subprocess.Popen(
        vsdevcmd, stdout=subprocess.PIPE, shell=True, env=cl_envs)
    lines = proc.stdout.readlines()
    for line in lines:
        line = line.decode("utf-8").rstrip()
        if "=" in line:
            key, value = line.split("=", maxsplit=1)
            cl_envs[key] = value
    return cl_envs





