[app]
# App info
title = IPTV Player
package.name = iptvplayer
package.domain = org.test
version = 1.0

# Source files
source.dir = .
source.include_exts = py,kv,png,jpg

# Requirements
requirements = python3,kivy,cython

# Orientation
orientation = portrait

# Permissions
android.permissions = INTERNET

# Logging
log_level = 2

# Android configuration
[android]
sdk_path = ~/.buildozer/android/platform/android-sdk
ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2
android.accept_sdk_license = True

# Optional: for CI builds or custom storage dirs
#p4a.local_recipes = path/to/recipes
#p4a.branch = master
#android.ndk = 25b
#android.sdk = 33
#android.arch = arm64-v8a, armeabi-v7a
