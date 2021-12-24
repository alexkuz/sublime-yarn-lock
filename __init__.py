import os

import sublime
import sublime_plugin

class BunPreviewLockbCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        filepath = self.view.file_name()
        [dirname, filename] = os.path.split(filepath)

        if filename.endswith(".lockb"):
            region = sublime.Region(0, self.view.size())

            stream = os.popen("cd %s && ./%s" % (dirname, filename))
            output = stream.read()

            self.view.replace(edit, region, output)
            self.view.assign_syntax("scope:text.yarnlock")
            self.view.set_read_only(True)
            self.view.set_scratch(True)


class BunLockbViewEventListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        if self.view.file_name().endswith(".lockb"):
            self.view.window().run_command("bun_preview_lockb")
