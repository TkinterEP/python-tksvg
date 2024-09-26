"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2021 RedFantom
"""
import tkinter as tk
import os


def load(window: tk.Tk):
    """Load tksvg into a Tk interpreter"""
    local = os.path.abspath(os.path.dirname(__file__))
    window.tk.setvar("dir", local)
    window.tk.eval("source [file join $dir pkgIndex.tcl]")
    window.tk.eval("package require tksvg")
    window.tk.unsetvar("dir")
    window._tksvg_loaded = True


class SvgImage(tk.PhotoImage):
    """
    Sub-class of tk.PhotoImage with support for SVG image options

    tksvg provides some options to control the rastering of SVG images.
    These are accessible when the images is created with this class.

    This implementation is inspired by GitHub @j4321:
    <https://stackoverflow.com/a/64829808>
    """
    __svg_options = {"scale": float, "scaletowidth": int, "scaletoheight": int}

    def __init__(self, name=None, cnf={}, master=None, **kwargs):
        # Load TkSVG package if not yet loaded
        master = master or tk._default_root
        if master is None:
            raise tk.TclError("No Tk instance available to get interpreter from")
        if not getattr(master, "_tksvg_loaded", False):
            load(master)

        # Pop SvgImage keyword arguments
        svg_options = {key: kwargs.pop(key) for key in self.__svg_options if key in kwargs}

        tk.PhotoImage.__init__(self, name, cnf, master, **kwargs)
        self.configure(**svg_options)

    def configure(self, **kwargs):
        """Configure the image with SVG options and pass to PhotoImage.configure"""
        svg_options = {key: kwargs.pop(key) for key in self.__svg_options if key in kwargs}
        if kwargs:
            tk.PhotoImage.configure(self, **kwargs)

        options = ""
        for key, value in svg_options.items():
            if value is not None:
                options += f"-{key} {value}"

        self.tk.eval("%s configure -format {svg %s}" % (self.name, options))

    config = configure

    def cget(self, option):
        """Return the option set for an SVG property or pass to PhotoImage.cget"""
        if option not in self.__svg_options:
            return tk.PhotoImage.cget(self, option)

        type = self.__svg_options[option]
        format_list = tk.PhotoImage.cget(self, "format")

        for index, item in enumerate(format_list):
            if str(item)[1:] == option:
                return type(format_list[index+1])

        return None

    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        return self.configure(**{key: value})
