from kivy import platform
from kivy.config import Config

if platform == 'linux':
    ratio = 2.0
    # w = 1920/2
    w = 1400 / 2
    Config.set('graphics', 'width', str(int(w)))
    Config.set('graphics', 'height', str(int(w)))

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.lang import Builder

import numpy as np
from rvit.core import *


class Model(Widget):
    def __init__(self, *args, **kwargs):
        self.w = 32
        self.thing = np.array(np.linspace(0.5, 0.0, self.w * self.w * 4),
                              dtype=np.float32).reshape(self.w, self.w, 4)
        super(Model, self).__init__(**kwargs)

        def iterate(arg):
            self.iterate()

        Clock.schedule_interval(iterate, 1.0 / 60.0)

    def iterate(self):
        self.thing[:] = np.array(np.random.rand(self.w * self.w * 4),
                                 dtype=np.float32).reshape(self.w, self.w, 4)


import pkg_resources


class RvitApp(App):
    def build(self):
        # self.model = Model()
        # return self.model
        sk_kv = pkg_resources.resource_string(__name__, "sk.kv").decode("utf-8")
        return Builder.load_string(sk_kv, filename='sk.kv')

    def on_stop(self):
        disactivate()


if __name__ == '__main__':
    activate()
    RvitApp().run()


def start():
    activate()
    RvitApp().run()
