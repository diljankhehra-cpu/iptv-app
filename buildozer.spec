[app]
# App title jo device te show hovega
title = IPTVPlayer

# Package name (unique identifier, Play Store style)
package.name = diljaniptv

# Reverse domain style
package.domain = diljan

# Source code folder (current folder)
source.dir = .

# Main Python file
source.main = main.py

# File extensions to include in the app
source.include_exts = py,png,jpg,json,kv

# Python libraries / dependencies
requirements = python3,kivy,requests

# App version
version = 0.1

# Screen orientation: portrait / landscape / all
orientation = portrait

# Fullscreen mode: 1 = yes, 0 = no
fullscreen = 1

# Permissions needed by the app
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# Debug log level
log_level = 2

# Enable Kivy bootstrap (do not change)
android.entrypoint = org.kivy.android.PythonActivity

# Additional android-specific settings
[android]
# Minimum Android API version
android.minapi = 21

# Target Android API version
android.api = 33

# NDK version (for C/C++ dependencies, needed by some Kivy modules)
android.ndk = 25b

# App architecture: arm64 for modern phones
android.arch = arm64-v8a

# Whether to use android SDK build tools
android.sdk = 31

# Java VM heap size (optional)
android.maxjavaheap = 512
