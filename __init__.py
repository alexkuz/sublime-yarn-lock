import os

import sublime
import sublime_plugin
from subprocess import PIPE, Popen

def get_setting(view, key, default_value=None):
    plugin_name = "YarnLock Syntax Highlighting"
    settings_filename = '{0}.sublime-settings'.format(plugin_name)

    settings = view.settings().get(plugin_name)
    if settings is None or settings.get(key) is None:
        settings = sublime.load_settings(settings_filename)

    value = settings.get(key, default_value)

    return value

def expand_var(window, var_to_expand):
    if var_to_expand:
        expanded = os.path.expanduser(var_to_expand)
        expanded = os.path.expandvars(expanded)
        if window:
            window_variables = window.extract_variables()
            expanded = sublime.expand_variables(expanded, window_variables)
        return expanded

    return var_to_expand

class BunPreviewLockbCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        filepath = self.view.file_name()
        if not filepath:
            return
        [dirname, filename] = os.path.split(filepath)

        if filename.endswith(".lockb"):
            region = sublime.Region(0, self.view.size())
            
            command = ["./%s" % filename]

            bun_path = expand_var(self.view.window(), get_setting(self.view, "bun_path"))

            print(bun_path)

            env = os.environ
            if bun_path + ":" not in env["PATH"]:
                env["PATH"] = bun_path + ":" + env["PATH"]

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
