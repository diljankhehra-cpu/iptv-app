[app]

title = IPTV Player
package.name = iptvplayer
package.domain = org.test
version = 1.0

source.dir = .
source.include_exts = py,kv,png,jpg

requirements = python3,kivy,cython

orientation = portrait

# Android configuration
android.api = 33
android.minapi = 21
android.build_tools_version = 33.0.2

# Explicit paths for CI (optional)
[android]
sdk_path = ~/.buildozer/android/platform/android-sdk
ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# Auto accept licenses
android.accept_sdk_license = True

log_level = 2

android.permissions = INTERNET
