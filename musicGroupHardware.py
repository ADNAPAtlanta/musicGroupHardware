import serial
import sys
import os
from glob import glob
from firebase import firebase
import requests
from mutagen.easyid3 import EasyID3
import spotipy
from tinytag import TinyTag
import eyed3
import time
import pyrebase
import pygame


internal = 0
spotify = 0
itunes = 0
musicFolder = "/home/pi/Music"
Firebase = firebase.FirebaseApplication("https://musicgroup-99932.firebaseio.com/")

config = {
  "apiKey": "AIzaSyAXDMY7c7KD0zwF4g57CzfullP5JpElU5o",
  "authDomain": "musicgroup-99932.firebaseapp.com",
  "databaseURL": "https://musicgroup-99932.firebaseio.com/",
  "storageBucket": "gs://musicgroup-99932.appspot.com",
 
}

firebasePyre= pyrebase.initialize_app(config)

songDuration = 0
nextSongTitle = ""



def internal():
    db = firebasePyre.database()
    internal = 1
    for files in os.listdir(musicFolder):
        #print(files)
        tag = TinyTag.get("/home/pi/Music/" + files)
        artist = tag.artist
        songName = tag.title
        duration = tag.duration
        votes = 0

        Firebase.patch("/Rooms/00001",{artist + "-" +songName:duration})
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"votes":votes})
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"title":songName})
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"artist":artist})
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"playNext":"false"})
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"duration":duration})

    
    songs = db.child("Rooms").child("00001").get()
    highestVote = 0
    
    for song in songs.each():
        print(song)
        print(song.val().get("votes"))
        if song.val().get("votes") > highestVote:
            highestVote = song.val().get("votes")
            print("highest vote is" + highestVote)
       
      
def stream_handler(post):
    print(post["event"]) # put
    print(post["path"]) # /-K7yGTTEp7O549EzTYtI
    print(post["data"]) # {'title': 'Pyrebase', "body": "etc..."}
            
def playSong():
    global songDuration
    global nextSongTitle
    db = firebasePyre.database()
    songs = db.child("Rooms").child("00001").get()
    highestVote = 0
    
    
    for song in songs.each():
        print(song)
        print(song.val().get("votes"))
        if song.val().get("votes") > highestVote:
            highestVote = song.val().get("votes")
            songDuration = song.val().get("duration")
            nextSongTitle = song.val().get("title")
            print("highest vote is" + str(highestVote))
        print(songDuration)
    for files in os.listdir(musicFolder):
        if nextSongTitle in files:
            os.system("/home/pi/Music/" +files)
         
        
        
def continueWatching(duration):
    db = firebasePyre.database()
    my_stream = db.child("Rooms").child("00001").stream(stream_handler)
    time.sleep(duration)
    songsByScore = db.child("Rooms").child("00001").order_by_child("votes").limit_to_first(3).get("votes")
    print(songsByScore)
    



mode = input("What is the mode?\n 1.internal update\n 2.internal\n")


if mode == "Spotify":
    print(setting)
    #spotify work
elif mode == "internal update":
    print(internal())
    playNextSong = input("Play nexr song? (y/n)")
    if playNextSong == "y":
        print(playSong())
        print(continueWatching(songDuration))

elif mode == "internal":
    playNextSong = input("Play next song? (y/n)")
    if playNextSong == "y":
        print(playSong())
        print(continueWatching(songDuration))
    

    
        
        

    
    
        
            



