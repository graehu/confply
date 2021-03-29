# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
import re
import ast
import json
import os
import socket

whitelist = [
    ".",
    "server.css",
    "server.log"
]
launcher_path = None
aliases = {}
__all__ = [
    "launcher_path",
    "start_server",
    "aliases",
]


class ConfplyServer(SimpleHTTPRequestHandler):
    """
    List files that are allowed to be sent
    """
    whitelist = []

    def do_GET(self):
        query_list = None

        # split the query out if need be
        if "?" in self.path:
            self.path, query_list = self.path.split("?")
            if "&" in query_list:
                query_list = query_list.split("&")
            else:
                query_list = [query_list]

        # put the queries into a dict
        queries = {}
        if query_list is not None:
            for q in query_list:
                k, v = q.split("=")
                queries[k] = v
        if self.path.startswith("/api/") and launcher_path is not None:
            response = {"ok": False}
            headers = {}
            headers["Content-Type"] = "text/json"
            if "/api/get.aliases" == self.path:
                response["ok"] = True
                response["aliases"] = aliases
                pass

            elif "/api/get.launcher" == self.path:
                response["ok"] = True
                response["path"] = launcher_path
                pass
            elif "/api/get.config.form" == self.path:
                response["ok"] = True
                response["html"] = get_form_html()
                pass
            elif "/api/run.alias" == self.path:
                response["ok"] = True
                headers["Cache-Control"] = "no-store, must-revalidate"
                server_log = os.path.abspath(os.path.dirname(__file__))
                server_log = os.path.join(server_log, "server.log")
                with open(server_log, "w") as sf:
                    sf.write("failed to write server log\n")
                    cmd = "python "
                    cmd += launcher_path + " "
                    cmd += queries["alias"]
                    cmd += " --config.confply.log_file "
                    cmd += server_log
                if os.name == 'nt':
                    system_code = os.system(cmd)
                else:
                    system_code = os.WEXITSTATUS(os.system(cmd))

                if system_code != 0:
                    response["status"] = "failure"
                else:
                    response["status"] = "success"
            else:
                self.send_response(404)
                for k, v in headers.items():
                    self.send_header(k, v)
                response["error"] = "api call not found "+self.path
                self.end_headers()
                self.wfile.write(bytes(json.dumps(response), "utf-8"))
                return

            self.send_response(200)
            for k, v in headers.items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
            # print("sending response: "+json.dumps(response, indent=4))
            return

        in_path = self.translate_path(self.path)
        in_path = os.path.relpath(in_path, self.directory)
        if in_path in whitelist:
            SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_response(404)
            self.end_headers()
        pass

    def do_POST(self):
        if "/api/run.config" == self.path:
            from confply import get_config_dictionary
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            parsed = data_string.decode("utf-8")
            parsed = re.sub(u'[\u201c\u201d]', '"', parsed)
            parsed = re.sub(u'[\u2019\u2018]', "'", parsed)
            parsed = json.loads(parsed)
            print("=====")
            print(parsed)
            print("=====")
            config = get_config_dictionary("cpp_compiler")
            print(config)
            for k, v in config.items():
                if k == "confply":
                    continue
                type_name = type(v).__name__
                if k in parsed:
                    print(k+": "+parsed[k])
                    if type_name == "str":
                        parsed[k] = parsed[k]
                    else:
                        parsed[k] = ast.literal_eval(parsed[k])
                else:
                    parsed[k] = eval(type_name+"()")

            print("running:")
            print(json.dumps(parsed, indent=4))
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()


def _get_best_family(*address):
    infos = socket.getaddrinfo(
        *address,
        type=socket.SOCK_STREAM,
        flags=socket.AI_PASSIVE,
    )
    family, type, proto, canonname, sockaddr = next(iter(infos))
    return family, sockaddr


def start_server(port=8000, launcher=None):
    global launcher_path
    global aliases
    # this is required to work with safari for some reason.
    HTTPServer.address_family, addr = _get_best_family(None, port)
    if launcher is not None:
        launcher_path = os.path.abspath(launcher)
        with open(launcher_path) as launcher_file:
            # #todo: this is dangerous af, need to redesign launcher files
            old_dir = os.path.abspath(os.path.curdir)
            config = {"aliases": {}, "__file__": launcher_path}
            exec(launcher_file.read(), config, config)
            aliases = config["aliases"]
            os.chdir(old_dir)

    webServer = HTTPServer(addr, ConfplyServer)
    print("Server started http://%s:%s" % (addr))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


def get_config_dict():
    import confply.cpp_compiler.config as config
    out = {}
    for k in dir(config):
        if k.startswith("__") or k == "confply":
            continue
        out[k] = getattr(config, k)
    return out


def get_form_html():
    import confply.cpp_compiler.config as config
    import confply.cpp_compiler.options as options
    lines = []
    lines.append("<form id=\"config_form\">") # action=\"/api/run.form\" method=\"post\"
    lines.append("<fieldset>")
    option_map = {}
    num = 0
    for k in dir(config):
        if k.startswith("__") or k == "confply":
            continue
        num += 1
        default = getattr(config, k)
        line = "<label for=\"id_"+k+"\">"+k+":</label>"
        if k in dir(options):
            mod = getattr(options, k)
            mod_dir = [x for x in dir(mod) if not x.startswith("__")]
            option_map[k] = {
                "keys": mod_dir,
                "values": [getattr(mod, x) for x in mod_dir]
                }
            if isinstance(default, list):
                line += "\n<select multiple id=\"id_"+k+"\" name=\""+k+"\">"
            else:
                line += "\n<select id=\"id_"+k+"\" name=\""+k+"\">"
            for key, value in zip(option_map[k]["keys"], option_map[k]["values"]):
                line += "\n\t<option value=\""+str(value)+"\">"+str(key)+"</option>"
            line += "\n</select>"
            line += "\n<br>"
            lines.append(line)
        else:
            if isinstance(default, bool):
                if default:
                    line += "<input type=\"checkbox\" id=\"id_"+k+"\" name=\""+k+"\" value=\"True\" checked/>"
                else:
                    line += "<input type=\"checkbox\" id=\"id_"+k+"\" name=\""+k+"\"/>"
            # elif isinstance(default, list):
            #     line += "<input type=\"text\" id=\"id_"+k+"\" name=\""+k+"[]\" value=\""+str(default)+"\"/>"
            #     pass
            else:
                line += "<input type=\"text\" id=\"id_"+k+"\" name=\""+k+"\" value=\""+str(default)+"\"/>"
            line += "\n<br>"
            lines.append(line)
            option_map[k] = default
    # lines.append("<input type=\"submit\" value=\"run_config\"/>")
    lines.append("</fieldset>")
    lines.append("</form>")
    return "\r\n".join(lines)


if __name__ == "__main__":
    start_server()
