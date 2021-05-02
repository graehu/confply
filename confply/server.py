# Python 3 server example
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import time
import threading
import json
import os
import socket
import shlex

whitelist = [
    ".",
    "server.css",
]
launcher_path = None
aliases = {}
configs = set()
__all__ = [
    "launcher_path",
    "start_server",
    "aliases",
]

run_lock = threading.Lock()


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
                        # #todo: deal with functions.
                        response["dict"] = {**config}
                    else:
                        response["ok"] = False
                        response["error"] = "invalid path"
            elif "/api/get.configs" == self.path:
                response["ok"] = True
                response["configs"] = list(configs)
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
        from confply import run_dict
        from confply import pushd
        response = {"ok": False}
        if "/api/run.config" == self.path:
            # #todo: check that the passed config is in the valid configs passed by get.configs
            try:
                run_lock.acquire()
                response["ok"] = True
                data_string = self.rfile.read(int(self.headers['Content-Length']))
                parsed = data_string.decode("utf-8")
                parsed = json.loads(parsed)
                response["ran"] = parsed
                log_path = os.path.abspath(os.path.dirname(__file__))
                log_path = "/".join(log_path.split("/")[0:-1])+"/logs/"
                os.makedirs(log_path, exist_ok=True)
                log_name = parsed["confply"]["config_path"]
                log_name = os.path.basename(log_name).split(".")[0]
                log_name += "_"+time.strftime("%Y%m%d-%H%M%S")
                log_name += "-"+threading.currentThread().name.split("-")[1]
                log_name += ".log"
                log_path = os.path.join(log_path, log_name)
                with open(log_path, "w") as sf:
                    sf.write("failed to write server log\n")
                    pass
                parsed["confply"]["log_file"] = log_path
                with pushd(os.path.dirname(launcher_path)):
                    return_code = run_dict(parsed)

                if return_code != 0:
                    response["status"] = "failure"
                else:
                    response["status"] = "success"
                with open(log_path) as sf:
                    response["log"] = sf.read()
                    pass
            finally:
                run_lock.release()
                pass
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
            pass
        elif "/api/run.alias" == self.path:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            parsed = data_string.decode("utf-8")
            parsed = json.loads(parsed)
            if "alias" in parsed:
                response["ok"] = True
                try:
                    run_lock.acquire()
                    log_path = os.path.abspath(os.path.dirname(__file__))
                    log_path = "/".join(log_path.split("/")[0:-1])+"/logs/"
                    os.makedirs(log_path, exist_ok=True)
                    log_name = parsed["alias"]
                    log_name += "_"+time.strftime("%Y%m%d-%H%M%S")
                    log_name += "-"+threading.currentThread().name.split("-")[1]
                    log_name += ".log"
                    log_path = os.path.join(log_path, log_name)
                    with open(log_path, "w") as sf:
                        sf.write("failed to write server log\n")
                        pass
                    with pushd(os.path.dirname(launcher_path)):
                        cmd = "python "
                        cmd += os.path.basename(launcher_path) + " "
                        cmd += parsed["alias"]
                        cmd += " --config.confply.log_file "
                        cmd += log_path
                        if os.name == 'nt':
                            system_code = os.system(cmd)
                        else:
                            system_code = os.WEXITSTATUS(os.system(cmd))

                        if system_code != 0:
                            response["status"] = "failure"
                        else:
                            response["status"] = "success"
                        with open(log_path) as sf:
                            response["log"] = sf.read()
                finally:
                    run_lock.release()
                pass
            else:
                response["ok"] = False
                response["error"] = "alias not in post request: "+self.path
            self.send_response(200)
            self.end_headers()
            self.wfile.write(bytes(json.dumps(response), "utf-8"))
            pass
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
    from confply import pushd
    global launcher_path
    global aliases
    global configs
    # this is required to work with safari for some reason.
    ThreadingHTTPServer.address_family, addr = _get_best_family(None, port)
    if launcher is not None:
        launcher_path = os.path.abspath(launcher)
        with pushd(os.path.dirname(launcher_path)):
            with open(os.path.basename(launcher_path)) as launcher_file:
                config = {"aliases": {}, "__file__": launcher_path}
                exec(launcher_file.read(), config, config)
                aliases = config["aliases"]
                for k, v in aliases.items():
                    for elem in shlex.split(v):
                        if elem.endswith(".py"):
                            configs.add(elem)

    webServer = ThreadingHTTPServer(addr, ConfplyServer)
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
    config_locals = load_config(path)
    if config_locals:
        config = config_locals["config"]
        config = config_to_dict(config)
        config["confply"]["config_path"] = path
        options = {}
        if "options" in config_locals:
            options = config_locals["options"]
            options = config_to_dict(options, False)
        clean_modules()
        return {"config": config, "options": options}

    return None


if __name__ == "__main__":
    start_server()
