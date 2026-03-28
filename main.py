import json, os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.config import Config
from kivy.lang import Builder

# Video Engine Setup
Config.set('kivy', 'video', 'ffpyplayer')

# ਪੂਰਾ UI ਡਿਜ਼ਾਈਨ ਇੱਥੇ ਹੈ
KV_UI = '''
<IPTV>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.05, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Video:
        id: player
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        allow_stretch: True

    BoxLayout:
        id: topbar
        orientation: 'vertical'
        size_hint: 1, None
        height: "90dp"
        pos_hint: {"top": 1}
        padding: [20, 10]
        opacity: 1
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0.7
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: ch_name
            text: "Loading Channels..."
            font_size: '26sp'
            bold: True
            color: 1, 1, 1, 1

    BoxLayout:
        id: side_menu
        orientation: 'vertical'
        size_hint: 0.35, 1
        pos_hint: {"x": 0, "y": 0}
        opacity: 0
        disabled: True
        canvas.before:
            Color:
                rgba: 0.08, 0.08, 0.08, 0.95
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "TV CHANNELS"
            size_hint_y: None
            height: "50dp"
            bold: True
            color: 1, 0.2, 0.2, 1

        TextInput:
            id: search_input
            hint_text: "Search..."
            size_hint_y: None
            height: "45dp"
            multiline: False
            background_color: (0.15, 0.15, 0.15, 1)
            foreground_color: (1, 1, 1, 1)
            padding: [10, 10]
            on_text: root.filter_menu(self.text)

        ScrollView:
            GridLayout:
                id: menu_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 2
                padding: 5
'''

class IPTV(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config_path = os.path.join(App.get_running_app().user_data_dir, "config.json")
        self.data = self.load_config()
        self.channels = []
        self.current = self.data.get("default", 0)
        Window.bind(on_key_down=self.keys)
        # ਡਿਫੌਲਟ ਪਲੇਲਿਸਟ ਲੋਡ ਕਰੋ
        Clock.schedule_once(lambda dt: self.load_playlist(self.data["playlists"][self.data["current_playlist"]]), 1)

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f: return json.load(f)
            except: pass
        return {"playlists": ["https://iptv-org.github.io"], "current_playlist": 0, "default": 0}

    def load_playlist(self, path):
        if path.startswith("http"):
            UrlRequest(path, on_success=self.on_playlist_success, on_error=self.on_playlist_error)
        elif os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f: self.parse_playlist(f.readlines())

    def on_playlist_success(self, request, result):
        self.parse_playlist(result.splitlines())

    def on_playlist_error(self, request, error):
        self.ids.ch_name.text = "Playlist Load Failed!"

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
            self.ids.ch_name.text = f"{len(self.channels)} Channels Found"
            self.build_menu()
            Clock.schedule_once(lambda dt: self.play(self.current), 1)

    def build_menu(self, filter_text=""):
        self.ids.menu_list.clear_widgets()
        for i, ch in enumerate(self.channels):
            if filter_text.lower() in ch["name"].lower():
                btn = Button(text=ch["name"], size_hint_y=None, height=50, background_color=(0.1, 0.1, 0.1, 0.6))
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
        if self.ids.search_input.focus: return 
        if key == 273: self.play(self.current - 1)
        elif key == 274: self.play(self.current + 1)
        elif text == "m": self.toggle_menu()
        elif key == 13 or key == 40: self.show_overlay()

    def toggle_menu(self):
        is_hidden = self.ids.side_menu.opacity == 0
        self.ids.side_menu.opacity = 1 if is_hidden else 0
        self.ids.side_menu.disabled = not is_hidden
        if is_hidden: self.ids.search_input.focus = True

    def show_overlay(self, *args):
        self.ids.topbar.opacity = 1
        Clock.unschedule(self.hide_overlay)
        Clock.schedule_once(self.hide_overlay, 5)

    def hide_overlay(self, dt):
        self.ids.topbar.opacity = 0

class AppMain(App):
    def build(self):
        Builder.load_string(KV_UI)
        return IPTV()

if __name__ == "__main__":
    AppMain().run()
