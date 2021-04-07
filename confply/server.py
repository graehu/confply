# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os
import socket

whitelist = [
    ".",
    "server.css",
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
        from confply import pushd
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
            elif "/api/get.config.dict" == self.path:
                with pushd(os.path.dirname(launcher_path)):
                    if "path" in queries and os.path.exists(queries["path"]):
                        response["ok"] = True
                        config = get_config_dict(queries["path"])
                        response["dict"] = {**config}
                    else:
                        response["ok"] = False
                        response["error"] = "invalid path"
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
                with open(server_log) as sf:
                    response["log"] = sf.read()
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
        response = {"ok": False}
        if "/api/run.config" == self.path:
            from confply import run_json
            from confply import pushd
            response["ok"] = True
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            parsed = data_string.decode("utf-8")
            parsed = json.loads(parsed)
            response["ran"] = parsed
            server_log = os.path.abspath(os.path.dirname(__file__))
            server_log = os.path.join(server_log, "server.log")
            with open(server_log, "w") as sf:
                sf.write("failed to write server log\n")
                pass
            parsed["confply"]["log_file"] = server_log
            with pushd(os.path.dirname(launcher_path)):
                return_code = run_json(parsed, "cpp_compiler")

            if return_code != 0:
                response["status"] = "failure"
            else:
                response["status"] = "success"
            with open(server_log) as sf:
                response["log"] = sf.read()
                pass
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))


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
            config = {"aliases": {}, "__file__": launcher_path}
            exec(launcher_file.read(), config, config)
            aliases = config["aliases"]

    webServer = HTTPServer(addr, ConfplyServer)
    print("Server started http://%s:%s" % (addr))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


def get_config_dict(path):
    from confply import load_config
    from confply import clean_modules
    from confply import config_to_dict
    config_locals, config_modules = load_config(path)
    if config_locals:
        config = config_locals["config"]
        options = config_locals["options"]
        config = config_to_dict(config)
        options = config_to_dict(options)
        config["confply"]["config_path"] = path
        clean_modules(config_modules)
        return {"config": config, "options": options}

    return None


if __name__ == "__main__":
    start_server()
