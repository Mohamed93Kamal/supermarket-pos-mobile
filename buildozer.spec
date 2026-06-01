[app]
title = نظام كاشير سوبر ماركت
package.name = supermarketpos
package.domain = org.supermarket

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db
source.main = app_final.py

version = 3.0.0

requirements = python3,kivy,kivymd

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
