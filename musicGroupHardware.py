import serial
import sys
from glob import glob
from firebase import firebase
import requests






Firebase = firebase.FirebaseApplication("https://musicgroup-99932.firebaseio.com/")
setting = Firebase.get("/Rooms/00001","setting")
if setting == "Spotify":
    print(setting)
    #spotify work
elif setting == "Internal":
    print(setting)

