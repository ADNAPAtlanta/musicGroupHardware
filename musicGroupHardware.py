import serial
import sys
import os
from glob import glob
from firebase import firebase
import requests
from mutagen.easyid3 import EasyID3
import spotipy





musicFolder = "/home/pi/Music"
Firebase = firebase.FirebaseApplication("https://musicgroup-99932.firebaseio.com/")
setting = Firebase.get("/Rooms/00001","setting")
if setting == "Spotify":
    print(setting)
    #spotify work
elif setting == "Internal":
    print(setting)
    '''for song in glob("/home/pi/Music"):
        mp3Info = EasyID3(song)
        print(mp3Info.items())
    quit = input("test")
    '''
    for root, dirs, files in os.walk(musicFolder):
        print(files)



