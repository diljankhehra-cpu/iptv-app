[app]

# App info
title = IPTV Player
package.name = iptvplayer
package.domain = org.test

# Source files
source.dir = .
source.include_exts = py,kv,png,jpg

version = 1.0

requirements = python3,kivy

orientation = portrait

# Android configuration (stable versions, no AIDL error)
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.build_tools_version = 33.0.2

# Auto accept licenses
android.accept_sdk_license = True

# Logging
log_level = 2

# Permissions
android.permissions = INTERNET
