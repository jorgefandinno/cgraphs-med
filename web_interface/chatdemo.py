#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Simplified chat demo for websockets.

Authentication, error handling, etc are left as an exercise for the reader :)
"""

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)



def dict2list(dictionary, key_name="name", value_name="value"):
    l = []
    for name in dictionary.keys():
        value = dictionary[ name ]
        pair = pair2dict(name, value)
    l.append(pair)

def pair2dict(key, value, key_name="name", value_name="value"):
    return { key_name  : key , value_name : value }


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/chatsocket", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    
    variables = {
        "height" : 174,
        "weight" :  72
    }

    def get(self):
        variable_list = []
        for (key, value) in self.variables.items():
            variable_list.append( pair2dict(key, value))
        self.render("index.html", messages=ChatSocketHandler.cache, variables= variable_list)







class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200


    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    @classmethod
    def call(cls, fname, parameter):
        message = {
            "call"      : fname,
            "parameter" : parameter
        }
        logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            try:
                waiter.write_message(message)
            except:
                logging.error("Error sending message", exc_info=True)


    def on_message(self, message):
        logging.info("got message %r", message)
        parsed = tornado.escape.json_decode(message)
        
        print parsed

        if parsed["call"] == "update_variables":
            self.update_variables(parsed["parameter"])
            return

        chat = {
            "id": str(uuid.uuid4()),
            "body": parsed["body"],
            }
        chat["call"] = "chat"
        chat["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=chat))

        ChatSocketHandler.update_cache(chat)
        ChatSocketHandler.send_updates(chat)





    def update_variables(self, variables):
        print variables
        send_variables = []
        for variable in variables:
            send_variable = {
                "name"      : variable["name"],
                "value"     : variable["value"],
                "modified"  : variable["value"] != variable["oldValue"]
            }
            send_variables.append(send_variable)

        ChatSocketHandler.call("update_variables", send_variables)
        # for var_name in variables_dict.keys():
        #     if var_name.startswith("variable"):
        #         print var_name + " = " + variables_dict[var_name]



    def load_variabls_list(self):
        print "load_variabls_list"
        variables = {
            "height" : 174,
            "weight" :  72
        }
        for variable_name in variables.keys():
            variable_value = variables[ varaible_name ]
            variable = {
                "name"  : variable_name,
                "value" : variable_value
            }
            message["action"] = "load_variable_list"
            message["html"] = tornado.escape.to_basestring(
                self.render_string("variable-row.html", variable=variable))

            ChatSocketHandler.update_cache(chat)
            ChatSocketHandler.send_updates(chat)






def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
