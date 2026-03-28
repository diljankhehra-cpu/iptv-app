import json, os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.config import Config
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserIconView

# ਵੀਡੀਓ ਇੰਜਣ
Config.set('kivy', 'video', 'ffpyplayer')

KV_UI = '''
<IPTV>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

    Video:
        id: player
        size_hint: 1, 1
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        allow_stretch: True

    # --- CUSTOM WATERMARK ---
    Image:
        id: watermark
        source: ""
        size_hint: None, None
        size: "100dp", "50dp"
        pos_hint: {"right": 0.98, "top": 0.95}
        opacity: 0 # ਪਹਿਲਾਂ ਲੁਕਿਆ ਹੋਇਆ

    # Top Bar
    BoxLayout:
        id: topbar
        orientation: 'vertical'
        size_hint: 1, None
        height: "80dp"
        pos_hint: {"top": 1}
        opacity: 0
        canvas.before:
            Color:
                rgba: 0, 0, 0, 0.7
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: ch_name
            text: ""
            font_size: '24sp'
            bold: True

    # Setup / First Run Screen
    BoxLayout:
        id: setup_screen
        orientation: 'vertical'
        size_hint: 0.6, 0.4
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        spacing: 10
        padding: 20
        opacity: 0
        disabled: True
        canvas.before:
            Color:
                rgba: 0.1, 0.1, 0.1, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: "ENTER M3U PLAYLIST URL"
            bold: True
        TextInput:
            id: m3u_input
            multiline: False
            hint_text: "http://example.com"
        Button:
            text: "START STREAMING"
            on_release: root.save_and_load_m3u(root.ids.m3u_input.text)
'''

class IPTV(FloatLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.config_path = os.path.join(App.get_running_app().user_data_dir, "iptv_config.json")
        self.data = self.load_config()
        self.channels = []
        
        Window.bind(on_key_down=self.keys)
        Clock.schedule_once(self.check_first_run, 1)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f: return json.load(f)
        return {"m3u_url": "", "wm_path": ""}

    def check_first_run(self, dt):
        if not self.data["m3u_url"]:
            self.ids.setup_screen.opacity = 1
            self.ids.setup_screen.disabled = False
        else:
            self.load_playlist(self.data["m3u_url"])
            if self.data["wm_path"]:
                self.ids.watermark.source = self.data["wm_path"]
                self.ids.watermark.opacity = 0.6

    def save_and_load_m3u(self, url):
        if url.startswith("http"):
            self.data["m3u_url"] = url
            with open(self.config_path, 'w') as f: json.dump(self.data, f)
            self.ids.setup_screen.opacity = 0
            self.ids.setup_screen.disabled = True
            self.load_playlist(url)

    def load_playlist(self, path):
        self.ids.ch_name.text = "Loading Playlist..."
        UrlRequest(path, on_success=self.on_playlist_success)

    def on_playlist_success(self, request, result):
        lines = result.splitlines()
        self.channels = []
        for i, line in enumerate(lines):
            if line.startswith("#EXTINF"):
                name = line.split(",")[-1].strip()
                url = lines[i+1].strip()
                self.channels.append({"name": name, "url": url})
        
        if self.channels:
            self.play(0)

    def play(self, i):
        ch = self.channels[i]
        self.ids.player.source = ch["url"]
        self.ids.player.state = 'play'
        self.ids.ch_name.text = ch["name"]
        self.show_overlay()

    def show_overlay(self):
        self.ids.topbar.opacity = 1
        Clock.schedule_once(lambda dt: setattr(self.ids.topbar, 'opacity', 0), 4)

    def keys(self, inst, key, scancode, text, mod):
        if text == "s": self.open_settings() # 's' for Settings

    def open_settings(self):
        # ਵਾਟਰਮਾਰਕ ਚੁਣਨ ਲਈ ਫਾਈਲ ਬ੍ਰਾਊਜ਼ਰ
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserIconView(path=".")
        btn = Button(text="Select as Watermark", size_hint_y=0.2)
        
        popup = Popup(title='Select Logo from Gallery', content=content, size_hint=(0.9, 0.9))
        
        def set_wm(instance):
            if file_chooser.selection:
                self.data["wm_path"] = file_chooser.selection[0]
                self.ids.watermark.source = self.data["wm_path"]
                self.ids.watermark.opacity = 0.6
                with open(self.config_path, 'w') as f: json.dump(self.data, f)
                popup.dismiss()

        btn.bind(on_release=set_wm)
        content.add_widget(file_chooser)
        content.add_widget(btn)
        popup.open()

from kivy.uix.boxlayout import BoxLayout
class AppMain(App):
    def build(self):
        Builder.load_string(KV_UI)
        return IPTV()

if __name__ == "__main__":
    AppMain().run()
