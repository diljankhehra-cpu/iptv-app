import json, os
import requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.video import Video
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

CONFIG = "config.json"

class IPTV(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.data = self.load()
        self.channels = []
        self.current = self.data["default"]

        # VIDEO
        self.video = Video(source="", state="stop")
        self.video.allow_stretch = True
        self.add_widget(self.video)

        # WATERMARK
        self.wm = Image(size_hint=(None, None))
        self.add_widget(self.wm)

        # EPG TEXT
        self.epg = Label(text="", size_hint=(1,None), height=50, pos_hint={"y":0})
        self.add_widget(self.epg)

        # OVERLAY
        self.overlay = Label(text="", pos_hint={"top":1})
        self.add_widget(self.overlay)

        Window.bind(on_key_down=self.keys)

        self.load_playlist(self.data["playlists"][self.data["current_playlist"]])
        Clock.schedule_once(lambda dt: self.play(self.current), 1)

    def load(self):
        if os.path.exists(CONFIG):
            return json.load(open(CONFIG))
        return {
            "playlists": ["https://iptv-org.github.io/iptv/index.m3u"],
            "current_playlist": 0,
            "default": 0,
            "wm": {"enable": False, "path": "", "x": 10, "y": 10, "w":120, "h":60}
        }

    def save(self):
        json.dump(self.data, open(CONFIG,"w"))

    def load_playlist(self, path):
        self.channels = []
        try:
            if path.startswith("http"):
                res = requests.get(path, timeout=10)
                lines = res.text.splitlines()
            else:
                lines = open(path).readlines()
        except:
            print("Playlist error")
            return

        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                try:
                    name = lines[i].split(",")[-1].strip()
                    url = lines[i+1].strip()
                    self.channels.append({"name": name, "url": url})
                except:
                    pass
        print("Channels:", len(self.channels))

    def play(self, i):
        if not self.channels:
            return
        self.current = i
        ch = self.channels[i]
        self.video.source = ch["url"]
        self.video.state = "play"

        if self.data["wm"]["enable"]:
            self.wm.source = self.data["wm"]["path"]
            self.wm.pos = (self.data["wm"]["x"], self.data["wm"]["y"])
            self.wm.size = (self.data["wm"]["w"], self.data["wm"]["h"])
        self.epg.text = "📺 " + ch["name"]

    def keys(self, inst, key, scancode, text, mod):
        if key == 166:
            self.play((self.current + 1) % len(self.channels))
        elif key == 167:
            self.play((self.current - 1) % len(self.channels))
        elif key == 40:
            self.overlay.text = "⚙ SETTINGS (Press M)"
            Clock.schedule_once(lambda dt: self.clear_overlay(), 3)
        elif text == "m":
            self.settings_menu()

    def clear_overlay(self):
        self.overlay.text = ""

    # SETTINGS MENU
    def settings_menu(self):
        box = BoxLayout(orientation="vertical")
        b1 = Button(text="Add Playlist")
        b2 = Button(text="Switch Playlist")
        b3 = Button(text="Set Startup Channel")
        b4 = Button(text="Watermark Settings")
        for b in [b1,b2,b3,b4]:
            box.add_widget(b)
        Popup(title="Settings", content=box, size_hint=(0.6,0.6)).open()
        b1.bind(on_press=lambda x: self.add_playlist())
        b2.bind(on_press=lambda x: self.switch_playlist())
        b3.bind(on_press=lambda x: self.set_startup())
        b4.bind(on_press=lambda x: self.watermark_menu())

    def add_playlist(self):
        box = BoxLayout(orientation="vertical")
        inp = TextInput(hint_text="Enter URL")
        btn = Button(text="Save")
        box.add_widget(inp)
        box.add_widget(btn)
        popup = Popup(title="Add Playlist", content=box, size_hint=(0.7,0.5))

        def save_playlist(instance):
            self.data["playlists"].append(inp.text)
            self.save()
            popup.dismiss()

        btn.bind(on_press=save_playlist)
        popup.open()

    def switch_playlist(self):
        box = BoxLayout(orientation="vertical")
        for i, p in enumerate(self.data["playlists"]):
            btn = Button(text=f"Playlist {i}")
            btn.bind(on_press=lambda x, idx=i: self.select_playlist(idx))
            box.add_widget(btn)
        Popup(title="Select Playlist", content=box, size_hint=(0.7,0.7)).open()

    def select_playlist(self, idx):
        self.data["current_playlist"] = idx
        self.save()
        self.load_playlist(self.data["playlists"][idx])

    def set_startup(self):
        self.data["default"] = self.current
        self.save()

    def watermark_menu(self):
        box = BoxLayout(orientation="vertical")
        b1 = Button(text="Select Image")
        b2 = Button(text="Set Position & Size")
        box.add_widget(b1)
        box.add_widget(b2)
        Popup(title="Watermark", content=box, size_hint=(0.6,0.5)).open()
        b1.bind(on_press=lambda x: self.choose_wm())
        b2.bind(on_press=lambda x: self.set_wm())

    def choose_wm(self):
        fc = FileChooserIconView()
        btn = Button(text="Use")
        box = BoxLayout(orientation="vertical")
        box.add_widget(fc)
        box.add_widget(btn)
        popup = Popup(title="Select Image", content=box, size_hint=(0.9,0.9))

        def set_img(instance):
            if fc.selection:
                self.data["wm"]["enable"] = True
                self.data["wm"]["path"] = fc.selection[0]
                self.save()
                popup.dismiss()

        btn.bind(on_press=set_img)
        popup.open()

    def set_wm(self):
        box = BoxLayout(orientation="vertical")
        x = TextInput(hint_text="X")
        y = TextInput(hint_text="Y")
        w = TextInput(hint_text="Width")
        h = TextInput(hint_text="Height")
        btn = Button(text="Apply")
        for i in [x,y,w,h,btn]:
            box.add_widget(i)
        popup = Popup(title="Watermark Settings", content=box, size_hint=(0.6,0.7))

        def apply(instance):
            self.data["wm"]["x"] = int(x.text)
            self.data["wm"]["y"] = int(y.text)
            self.data["wm"]["w"] = int(w.text)
            self.data["wm"]["h"] = int(h.text)
            self.save()
            popup.dismiss()

        btn.bind(on_press=apply)
        popup.open()

class AppMain(App):
    def build(self):
        Window.fullscreen = True
        return IPTV()

AppMain().run()
