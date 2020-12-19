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

_vswhere = '%PROGRAMFILES(X86)%/Microsoft Visual Studio/Installer'
_vswhere = os.path.expandvars(_vswhere)
_vswhere_exe = _vswhere+"/vswhere.exe"
_vs_tools = ""
_cl_found = False
if os.path.exists(_vswhere_exe):
    envs = {"PATH": _vswhere}
    cmd = "vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath"
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, shell=True, env=envs)
    installation_path = proc.stdout.read().decode("utf-8").rstrip()
    installation_path = installation_path.replace("/", "\\")
    _vs_tools = (installation_path+"/Common7/Tools/").replace("/", "\\")
    version_path = "/VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt"
    version_path = (installation_path+version_path).replace("/", "\\")
    if os.path.exists(version_path):
        with open(version_path, "r") as version_file:
            version = version_file.read().rstrip()
            cl_path = installation_path+"/VC/Tools/MSVC/"+version+"/bin/HostX64/x64/cl.exe"
            cl_path.replace("/", "\\")
            _cl_found = os.path.exists(cl_path)


def get_environ(config):
    global _vs_tools
    cl_envs = os.environ.copy()
    cl_envs["PATH"] += ";"+_vs_tools
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


def is_found(config):
    return _cl_found


