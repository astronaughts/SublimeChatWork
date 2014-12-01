#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import urllib.request
import json

BASE = "https://api.chatwork.com/v1"
ROOMS = BASE + "/rooms"
MESSAGES = ROOMS + "/%d/messages"


class CwSendContentCommand(sublime_plugin.WindowCommand):
    def run(self):
        window = sublime.active_window()
        view = window.active_view()
        settings = sublime.load_settings("ChatWork.sublime-settings")
        private_settings = view.settings()
        self.token = private_settings.get("token", settings.get("token"))
        if self.token is None:
            sublime.error_message("Prease set your token.")
            return

        req = self.request(url=ROOMS)

        try:
            response = urllib.request.urlopen(req)
            body = response.read().decode()
            self.rooms = json.loads(body)
            room_list = []
            for room in self.rooms:
                room_list.append(room["name"])
            window.show_quick_panel(room_list, self.on_done, selected_index=90)

        except urllib.error.URLError as e:
            sublime.error_message(e.reason)

    def on_done(self, index):
        window = sublime.active_window()
        view = window.active_view()
        row, _ = view.rowcol(view.size())
        contents = []
        for row_num in range(0, row):
            point = view.text_point(row_num, 0)
            line = view.line(point)
            contents.append(view.substr(line))

        selected_room = self.rooms[index]
        data = {
            "body": "\n".join(contents),
        }
        endpoint = MESSAGES % selected_room["room_id"]
        params = urllib.parse.urlencode(data).encode("utf-8")
        req = self.request(url=endpoint, params=params)

        try:
            urllib.request.urlopen(req)
            sublime.status_message("This file sent to the chat.")

        except urllib.error.HTTPError as e:
            sublime.error_message(e.reason)

    def request(self, **kwargs):
        headers = {
            "X-ChatWorkToken": self.token
        }
        url = kwargs["url"]
        data = kwargs.get("params", None)
        req = urllib.request.Request(url, data=data, headers=headers)
        return req
