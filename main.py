import json, os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.config import Config

# Use ffpyplayer for better video stability
Config.set('kivy', 'video', 'ffpyplayer')

CONFIG_NAME = "config.json"

class IPTV(FloatLayout):

    def __init__(self, **kw):
        super().__init__(**kw)

        # Config file in app user directory
        self.config_path = os.path.join(App.get_running_app().user_data_dir, CONFIG_NAME)
        self.data = self.load_config()

        self.channels = []
        self.current = self.data["default"]

        Window.bind(on_key_down=self.keys)

        # Delay playlist load slightly to ensure KV widgets ready
        Clock.schedule_once(lambda dt: self.load_playlist(self.data["playlists"][self.data["current_playlist"]]), 0.2)

    # ---------------- CONFIG ----------------
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                return json.load(open(self.config_path))
            except:
                pass
        return {
            "playlists": ["https://iptv-org.github.io/iptv/index.m3u"],
            "current_playlist": 0,
            "default": 0,
            "wm": {"enable": False, "path": "", "x": 10, "y": 10, "w":120, "h":60}
        }

    def save_config(self):
        try:
            json.dump(self.data, open(self.config_path, "w"))
        except Exception as e:
            print("Error saving config:", e)

    # ---------------- PLAYLIST ----------------
    def load_playlist(self, path):
        self.channels = []

        if path.startswith("http"):
            UrlRequest(
                url=path,
                on_success=self.on_playlist_success,
                on_error=self.on_playlist_error,
                on_failure=self.on_playlist_error
            )
        else:
            try:
                lines = open(path).readlines()
                self.parse_playlist(lines)
            except Exception as e:
                print("Playlist error:", e)

    def on_playlist_success(self, request, result):
        lines = result.splitlines()
        self.parse_playlist(lines)

    def on_playlist_error(self, request, error):
        print("Playlist error:", error)

    def parse_playlist(self, lines):
        self.channels = []
        for i in range(len(lines)):
            if lines[i].startswith("#EXTINF"):
                try:
                    name = lines[i].split(",")[-1].strip()
                    url = lines[i+1].strip()
                    self.channels.append({"name": name, "url": url})
                except:
                    pass
        print("Channels loaded:", len(self.channels))
        # Delay start_play to ensure Video widget ready
        Clock.schedule_once(self.start_play, 0.5)

    # ---------------- START ----------------
    def start_play(self, dt):
        if self.channels and hasattr(self.ids, "player"):
            self.play(self.current)

    # ---------------- PLAY ----------------
    def play(self, i):
        if not self.channels or not hasattr(self.ids, "player"):
            return

        self.current = i
        ch = self.channels[i]

        print("▶", ch["name"], ch["url"])
        try:
            self.ids.player.state = "stop"  # stop before load
            self.ids.player.source = ch["url"]
            self.ids.player.state = "play"
        except Exception as e:
            print("Video load error:", e)

        # EPG update
        if hasattr(self.ids, "ch_name") and hasattr(self.ids, "program"):
            self.ids.ch_name.text = ch["name"]
            self.ids.program.text = "Now Playing..."

        # WATERMARK
        wm = self.data["wm"]
        if wm["enable"] and wm["path"]:
            try:
                self.ids.wm.source = wm["path"]
                self.ids.wm.pos = (wm["x"], wm["y"])
                self.ids.wm.size = (wm["w"], wm["h"])
            except:
                pass

    # ---------------- KEYS ----------------
    def keys(self, inst, key, scancode, text, mod):
        if not self.channels:
            return

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
        if hasattr(self.ids, "topbar"):
            self.ids.topbar.opacity = 1
        if hasattr(self.ids, "menu"):
            self.ids.menu.opacity = 1
        if hasattr(self.ids, "epg"):
            self.ids.epg.opacity = 1

        Clock.unschedule(self.hide_overlay)
        Clock.schedule_once(self.hide_overlay, 6)

    def hide_overlay(self, dt):
        if hasattr(self.ids, "topbar"):
            self.ids.topbar.opacity = 0
        if hasattr(self.ids, "menu"):
            self.ids.menu.opacity = 0
        if hasattr(self.ids, "epg"):
            self.ids.epg.opacity = 0

    # ---------------- SETTINGS ----------------
    def settings_menu(self):
        print("⚙ SETTINGS (next upgrade full UI)")

# ---------------- APP ----------------
class AppMain(App):
    def build(self):
        Window.fullscreen = True
        return IPTV()

if __name__ == "__main__":
    AppMain().run()
