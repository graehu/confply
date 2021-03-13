# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
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

        wfile_content = None
        if "r" in queries:
            print("recieved run request");
            if launcher_path is not None:
                print("attmpting to run: "+queries["r"])
                cmd = "python "
                cmd += launcher_path + " "
                cmd += queries["r"]
                # #todo: put the server log into the final html
                cmd += " > server.log"
                os.system(cmd)
        if "g" in queries:
            if launcher_path is not None:
                print("attempting to get "+queries["g"])
                if queries["g"] == "aliases":
                    wfile_content = bytes(json.dumps(aliases), "utf-8")
                    pass
            pass

        in_path = self.translate_path(self.path)
        in_path = os.path.relpath(in_path, self.directory)
        if in_path in whitelist:

            if wfile_content is not None:
                self.send_response(200)
                self.send_header("Content-Type", "text/json")
                self.end_headers()
                self.wfile.write(wfile_content)
            else:
                SimpleHTTPRequestHandler.do_GET(self)

        else:
            self.send_response(404)
            self.end_headers()
        pass

    def do_POST(self):
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        print(data_string)
        self.send_response(200)
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
        launcher_path = launcher
        print(launcher_path)
        with open(launcher_path) as launcher_file:
            # #todo: this is dangerous af, need to redesign launcher files
            old_dir = os.path.abspath(os.path.curdir)
            config = {"aliases": {}, "__file__": launcher_path}
            exec(launcher_file.read(), config, config)
            aliases = config["aliases"]
            os.chdir(old_dir)
            # print("current working dir "+os.path.curdir)

    webServer = HTTPServer(addr, ConfplyServer)
    print("Server started http://%s:%s" % (addr))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")


if __name__ == "__main__":
    start_server()
