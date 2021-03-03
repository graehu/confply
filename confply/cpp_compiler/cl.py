import os
import subprocess
import json
import confply.log as log
import confply.cpp_compiler as cpp_compiler
import confply.cpp_compiler.config as config

def generate():
    def __parse_deps(deps_string):
        deps_json = json.loads(deps_string)
        if "Data" in deps_json:
            deps_json = deps_json["Data"]
            out_deps = deps_json["Includes"]
            out_deps.append(deps_json["Source"])
            return out_deps
        pass

    try:
        config.link_libraries.remove("stdc++")
        log.warning("removing stdc++ from link_libraries, it's not valid when using cl.exe")
    except:
        pass
    try:
        config.warnings.remove("pedantic")
        log.warning("removing pedantic from warnings, it's not valid when using cl.exe")
    except:
        pass
    try:
        config.warnings.remove("extra")
        log.warning("removing extra from warnings, it's not valid when using cl.exe")
    except:
        pass
        

    if config.confply.platform == "windows":
        cpp_compiler.tool = "cl"
        cpp_compiler.output_obj = "-Fo"
        cpp_compiler.output_exe = "-Fe"
        cpp_compiler.standard = "-std:"
        cpp_compiler.dependencies = ""
        cpp_compiler.link = ""
        cpp_compiler.library = "-LIBPATH:"
        cpp_compiler.dependencies_output = "-sourceDependencies"
        cpp_compiler.exception_handling = "-EHsc"
        cpp_compiler.pass_to_linker = "-link"
        cpp_compiler.object_ext = ".obj"
        cpp_compiler.parse_deps = __parse_deps
        cpp_compiler.debug = "-Zi"
        return cpp_compiler.generate()
    else:
        log.error("cl only supports windows platforms")
        return None

_vswhere = '%PROGRAMFILES(X86)%/Microsoft Visual Studio/Installer'
_vswhere = os.path.expandvars(_vswhere).replace("/", "\\")
_vswhere_exe = _vswhere+"\\vswhere.exe"
_vs_tools = ""
_cl_found = False
_cl_path = ""

if os.path.exists(_vswhere_exe):
    envs = os.environ.copy()
    envs["PATH"] += ";"+_vswhere
    cmd = "vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath"
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, env=envs)
    installation_path = proc.stdout.read().decode("utf-8").rstrip()
    installation_path = installation_path.replace("/", "\\")
    if not installation_path == "":
        _vs_tools = (installation_path+"/Common7/Tools/").replace("/", "\\")
        version_path = "/VC/Auxiliary/Build/Microsoft.VCToolsVersion.default.txt"
        version_path = (installation_path+version_path).replace("/", "\\")
        if os.path.exists(version_path):
            with open(version_path, "r") as version_file:
                version = version_file.read().rstrip()
                _cl_path = installation_path+"/VC/Tools/MSVC/"+version+"/bin/HostX64/x64/cl.exe"
                _cl_path.replace("/", "\\")
                _cl_found = os.path.exists(_cl_path)
    else:
        log.error("VisualStudio.Component.VC.Tools.x86.x64 not installed")

def get_environ():
    global _vs_tools
    if _cl_found:
        cl_envs = os.environ.copy()
        cl_envs["PATH"] += ";"+_vs_tools
        # #fixme: I think this is a hack, I feel like it should be passed like -arch
        cl_envs["VSCMD_DEBUG"] = "3"
        # #todo: add a way to set the architecture from the configs
        vsdevcmd = 'cmd.exe /s /c "call vsdevcmd.bat -arch=x64 -host_arch=x64 && set"'
        proc = subprocess.Popen(
            vsdevcmd, stdout=subprocess.PIPE, shell=True, env=cl_envs)
        lines = proc.stdout.readlines()
        for line in lines:
            line = line.decode("utf-8").rstrip()
            if "=" in line:
                key, value = line.split("=", maxsplit=1)
                cl_envs[key] = value
        return cl_envs
    else:
        return os.environ


def handle_args():
    cpp_compiler.handle_args()


def is_found():
    if _cl_found:
        log.success("cl found: "+_cl_path)
    return _cl_found



