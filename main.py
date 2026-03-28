import json, os, requests
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock

CONFIG = "config.json"

class IPTV(FloatLayout):

    def __init__(self, **kw):
        super().__init__(**kw)

        self.data = self.load()
        self.channels = []
        self.current = self.data["default"]

        Window.bind(on_key_down=self.keys)

        # playlist load
        self.load_playlist(self.data["playlists"][self.data["current_playlist"]])

        # direct play on start
        Clock.schedule_once(self.start_play, 1)

    # ---------------- CONFIG ----------------
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

    # ---------------- START ----------------
    def start_play(self, dt):
        if self.channels:
            self.play(self.current)

    # ---------------- PLAYLIST ----------------
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

    # ---------------- PLAY ----------------
    def play(self, i):
        if not self.channels:
            return

        self.current = i
        ch = self.channels[i]

        print("▶", ch["name"])

        self.ids.player.source = ch["url"]
        self.ids.player.state = "play"

        # EPG update
        self.ids.ch_name.text = ch["name"]
        self.ids.program.text = "Now Playing..."

        # WATERMARK
        wm = self.data["wm"]
        if wm["enable"] and wm["path"]:
            self.ids.wm.source = wm["path"]
            self.ids.wm.pos = (wm["x"], wm["y"])
            self.ids.wm.size = (wm["w"], wm["h"])

    # ---------------- KEYS ----------------
    def keys(self, inst, key, scancode, text, mod):

        # CH+
        if key == 166:
            self.play((self.current + 1) % len(self.channels))

        # CH-
        elif key == 167:
            self.play((self.current - 1) % len(self.channels))

        # NUMBER
        elif text and text.isdigit():
            n = int(text)
            if n < len(self.channels):
                self.play(n)

        # OK → overlay
        elif key == 40:
            self.show_overlay()

        # SETTINGS
        elif text == "m":
            self.settings_menu()

    # ---------------- OVERLAY ----------------
    def show_overlay(self):

        self.ids.topbar.opacity = 1
        self.ids.menu.opacity = 1
        self.ids.epg.opacity = 1

        Clock.unschedule(self.hide_overlay)
        Clock.schedule_once(self.hide_overlay, 6)

    def hide_overlay(self, dt):
        self.ids.topbar.opacity = 0
        self.ids.menu.opacity = 0
        self.ids.epg.opacity = 0

    # ---------------- SETTINGS ----------------
    def settings_menu(self):
        print("⚙ SETTINGS (next upgrade full UI)")

# ---------------- APP ----------------
class AppMain(App):
    def build(self):
        Window.fullscreen = True
        return IPTV()

AppMain().run()
