[app]
title = IPTV Player
package.name = iptvplayer
package.domain = org.test
version = 1.0

source.dir = .
source.include_exts = py,kv,png,jpg

# 🔥 IMPORTANT
requirements = python3,kivy,requests,cython==0.29.36

orientation = landscape
fullscreen = 1

android.permissions = INTERNET

log_level = 2


[buildozer]

# 🔥 FIX ALL ERRORS
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.sdk = 33
android.build_tools = 33.0.0

# ✅ VERY IMPORTANT (duplicate na hove)
android.accept_sdk_license = True

# 🔥 ARCH (TV support best)
android.arch = arm64-v8a, armeabi-v7a

# 🔥 DISABLE PROBLEM FEATURES
android.enable_androidx = True
android.gradle_dependencies =

# 🔥 SPEED + STABILITY
warn_on_root = 0
