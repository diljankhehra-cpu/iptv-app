import json, os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.config import Config

Config.set('kivy', 'video', 'ffpyplayer')

class IPTV(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config_path = os.path.join(App.get_running_app().user_data_dir, "config.json")
        self.data = self.load_config()
        self.channels = []
        self.current = self.data.get("default", 0)
        Window.bind(on_key_down=self.keys)
        Clock.schedule_once(lambda dt: self.load_playlist(self.data["playlists"][self.data["current_playlist"]]), 1)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f: return json.load(f)
            except: pass
        return {"playlists": ["https://iptv-org.github.io"], "current_playlist": 0, "default": 0}

    def load_playlist(self, path):
        if path.startswith("http"):
            UrlRequest(path, on_success=self.on_playlist_success)
        elif os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: self.parse_playlist(f.readlines())

    def on_playlist_success(self, request, result):
        self.parse_playlist(result.splitlines())

    def parse_playlist(self, lines):
        self.channels = []
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1].strip()
                try:
                    url = lines[i+1].strip()
                    if url.startswith("http"): self.channels.append({"name": name, "url": url})
                except: pass
        if self.channels:
            self.build_menu()
            Clock.schedule_once(lambda dt: self.play(self.current), 1)

    def build_menu(self, filter_text=""):
        self.ids.menu_list.clear_widgets()
        for i, ch in enumerate(self.channels):
            if filter_text.lower() in ch["name"].lower():
                btn = Button(text=ch["name"], size_hint_y=None, height=50, background_color=(0,0,0,0.5))
                btn.bind(on_release=lambda x, index=i: self.play_from_menu(index))
                self.ids.menu_list.add_widget(btn)

    def filter_menu(self, text):
        self.build_menu(text)

    def play_from_menu(self, index):
        self.play(index)
        self.toggle_menu()

    def play(self, i):
        if not self.channels: return
        self.current = i % len(self.channels)
        ch = self.channels[self.current]
        self.ids.player.state = 'stop'
        self.ids.player.source = ch["url"]
        self.ids.player.state = 'play'
        self.ids.ch_name.text = ch["name"]
        self.show_overlay()

    def keys(self, inst, key, scancode, text, mod):
        if self.ids.search_input.focus: return # ਜੇ ਟਾਈਪ ਕਰ ਰਹੇ ਹੋ ਤਾਂ ਕੀਬੋਰਡ ਸ਼ਾਰਟਕੱਟ ਬੰਦ ਰਹਿਣਗੇ
        if key == 273: self.play(self.current - 1)
        elif key == 274: self.play(self.current + 1)
        elif text == "m": self.toggle_menu()

    def toggle_menu(self):
        is_hidden = self.ids.side_menu.opacity == 0
        self.ids.side_menu.opacity = 1 if is_hidden else 0
        self.ids.side_menu.disabled = not is_hidden
        if is_hidden: self.ids.search_input.focus = True # ਮੀਨੂ ਖੁੱਲ੍ਹਦੇ ਹੀ ਸਰਚ ਬਾਰ ਐਕਟਿਵ ਹੋ ਜਾਵੇਗੀ

    def show_overlay(self, *args):
        self.ids.topbar.opacity = 1
        Clock.unschedule(self.hide_overlay)
        Clock.schedule_once(self.hide_overlay, 4)

    def hide_overlay(self, dt):
        self.ids.topbar.opacity = 0

class AppMain(App):
    def build(self): return IPTV()

if __name__ == "__main__":
    AppMain().run()
