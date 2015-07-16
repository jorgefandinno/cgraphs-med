// Copyright 2009 FriendFeed
//
// Licensed under the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License. You may obtain
// a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.

$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#messageform").live("submit", function() {
        newMessage($(this));
        return false;
    });
    $("#messageform").live("keypress", function(e) {
        if (e.keyCode == 13) {
            newMessage($(this));
            return false;
        }
    });

    $("#variables-form").live("submit", function() {
        sendUpdateVariables($(this));
        return false;
    });
    $("#variables-form").live("keypress", function(e) {
        if (e.keyCode == 13) {
            sendUpdateVariables($(this));
            return false;
        }
    });

    $("#message").select();
    updater.start();

});


function sendUpdateVariables(form) {
    var message = {}
    message["call"] = "update_variables"
    fields = form.serializeArray();
    for (var i = 0; i < fields.length; i++) {
        name = fields[i].name
        fields[i].oldValue = form.find("input[type=text][name="+name+"]").attr("oldValue")
    }
    message["parameter"] = fields
    updater.socket.send(JSON.stringify(message));
    form.find("input[type=text]").val("").select();
}

function showUpdateVariables(variables) {
    var form = $("#variables-form")
    for (var i = 0; i < variables.length; i++) {
        var variable = variables[i]
        var input = form.find("input[name=" + variable.name + "]")
        input.attr("value", variable.value )
        input.attr("oldValue", variable.value )
        if (variable.modified)
            input.css("color", "red")
        else
            input.css("color", "black")

    }

    // var message = {}
    // message["action"] = "update_variables"
    // message["parameter"] = form.formToDict();
    // updater.socket.send(JSON.stringify(message));
    // form.find("input[type=text]").val("").select();
}



function newMessage(form) {
    var message = form.formToDict();
    message["call"] = "sendMessage"
    updater.socket.send(JSON.stringify(message));
    form.find("input[type=text]").val("").select();
}



jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function() {
        var url = "ws://" + location.host + "/chatsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            message = JSON.parse(event.data)
            if (message.call == "update_variables")
                showUpdateVariables(message.parameter)
            else
                updater.showMessage(message);
            // updater.showMessage(JSON.parse(event.data));
        }
    },

    showMessage: function(message) {
        var existing = $("#m" + message.id);
        if (existing.length > 0) return;
        var node = $(message.html);
        node.hide();
        $("#inbox").append(node);
        node.slideDown();
    },

    loadVariableRow: function(message) {
        var variable_table = $("#variable-table");
        var variable_row = $(message.html);
        variable_table.append(variable_row);
    }
};
