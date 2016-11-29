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
import subprocess
import shlex
#import RPi.GPIO as GPIO
import shelve


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


def resetVotesInternal():
    db = firebasePyre.database()
    songs = db.child("Rooms").child("00001").get()
    musicFolder = "/home/pi/Music"
    for files in os.listdir(musicFolder):
        tag = TinyTag.get("/home/pi/Music/" + files)
        artist = tag.artist
        songName = tag.title
        duration = tag.duration
        votes = 0
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"votes":votes})

       
      
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
        if song.val().get("votes") > highestVote:
            highestVote = song.val().get("votes")
            songDuration = song.val().get("duration")
            nextSongTitle = song.val().get("title")
            print("highest vote is" + str(highestVote))
        print(songDuration)
    for files in os.listdir(musicFolder):
        if nextSongTitle in files:
            print(files)
            song = "/home/pi/Music/" + files
            subprocess.call(["omxplayer","-o","local",song])
            print(resetVotesInternal())
    
            
         
        
        
def continueWatching(duration):
    db = firebasePyre.database()
    my_stream = db.child("Rooms").child("00001").stream(stream_handler)
    time.sleep(duration)
    songsByScore = db.child("Rooms").child("00001").order_by_child("votes").limit_to_first(1).get()
    print(songsByScore)
    #subprocess.call(["omxplayer","-o","local","01 Good Morning.mp3"])

        
'''Possible Classes'''



class preferences(object):
    def __init__(self,voteTimeSetting,voteCycleSetting):
        self.voteTimeSetting = voteTimeSetting
        self.voteCycleSetting = voteCycleSetting
    def setVoteTimeSetting(self,time):
        voteTime = shelve.open("options.db")
        voteTime.write("Vote Time: %s" % time)
        self.voteTimeSetting = time
        voteTime["voteTime"] = self.voteTimeSetting
        voteTime.close()
    def setVoteCycleSetting(self,cycle):
        voteCycle = shelve.open("options.db")
        voteCycle.write("Vote Cycle: %s" % cycle)
        self.voteCycleSetting = cycle
        voteCycle["voteCycle"] = self.voteCycleSetting
    def getVoteTimeSetting(self):
        return self.voteTimeSetting
    def getVoteCycleSetting(self):
        return self.voteCycleSetting



class internal(object):
    def __init__(self,voteTime,voteCycle):
        #niitialize values
        self.voteTime = voteTime
        self.voteCycle = voteCycle

        
    def updateInternal(self):
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
        
    def startVoting(self):
        #reset votes
        db = firebasePyre.database()
        songs = db.child("Rooms").child("00001").get()
        musicFolder = "/home/pi/Music"
        for files in os.listdir(musicFolder):
            tag = TinyTag.get("/home/pi/Music/" + files)
            artist = tag.artist
            songName = tag.title
            duration = tag.duration
            votes = 0
            Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"votes":votes})
    def continueWatching(self):
        print("continue")


getSetting = shelve.open("options.db")
settings = preferences(getSetting["voteTIme"],getSetting["voteCycle"])
print(settings.getVoteCycleSetting(),settings.getVoteTimeSetting())

mode = input("What is the mode?\n 1.internal update\n 2.internal\n")

if mode == "Spotify":
    print("test")
    #spotify work
elif mode == "internal update":
    #print(internal())
    playNextSong = input("Play nexr song? (y/n)")
    if playNextSong == "y":
        print(playSong())
        print(continueWatching(songDuration))

elif mode == "internal":
    #mode = internal()

    internal = 1
    playNextSong = input("Play next song? (y/n)")
    if playNextSong == "y":
        print(playSong())
        print(continueWatching(songDuration))
    
    
        
            



