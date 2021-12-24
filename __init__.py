import os

import sublime
import sublime_plugin
from subprocess import PIPE, Popen

# TODO: move to settings
BIN_PATH = "$HOME/.bun/bin"

class BunPreviewLockbCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        filepath = self.view.file_name()
        if not filepath:
            return
        [dirname, filename] = os.path.split(filepath)

        if filename.endswith(".lockb"):
            region = sublime.Region(0, self.view.size())
            
            command = ["sh", "-c", "./%s" % filename]

            env = os.environ
            env_path = BIN_PATH.replace("$HOME", env["HOME"])
            if env_path not in env["PATH"]:
                env["PATH"] = env_path + ":" + env["PATH"]

            with Popen(command, cwd=dirname, stdout=PIPE, stderr=PIPE, shell=False, env=env) as process:
                res = process.communicate()
                if process.returncode != 0:
                    print('ERROR (%s): %s' % (process.returncode, res[1].decode("utf-8")))
                    return
                output = res[0].decode("utf-8")

            self.view.replace(edit, region, output)
            self.view.assign_syntax("scope:text.yarnlock")
            self.view.set_read_only(True)
            self.view.set_scratch(True)


class BunLockbViewEventListener(sublime_plugin.ViewEventListener):
    def on_load(self):
        if self.view.file_name().endswith(".lockb"):
            self.view.window().run_command("bun_preview_lockb")
