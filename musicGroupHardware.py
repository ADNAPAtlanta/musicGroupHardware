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
import RPi.GPIO as GPIO
import shelve
from gpiozero import LED, Button
from signal import pause


internal = 0
spotify = 0
itunes = 0
menu = 0
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
    voters = db.child("Rooms").child("00001").("voters").get()
    musicFolder = "/home/pi/Music"
    for files in os.listdir(musicFolder):
        tag = TinyTag.get("/home/pi/Music/" + files)
        artist = tag.artist
        songName = tag.title
        duration = tag.duration
        votes = 0
        Firebase.patch("/Rooms/00001/" + artist + "-" + songName,{"votes":votes})
    firebase.patch("/Rooms/00001/voters",{"placeholder":"voted"})
    for voter in voters.each():
        if song != "placeholder":
            song.remove()
        
    

def startInternal():
    mode = internal(settings.getVoteTimeSetting(),settings.getVoteCycleSetting())
    print("press again to start voting")
        
    internalButton = Button(15,pull_up=False)
    internalButton.wait_for_press()
    internalButton
    playNextSong = input("1.update\n 2.start voting\n")
    if playNextSong == "2" or "start voting":
        print(str(settings.voteTimeSetting) + " " + " seconds to vote!")
        mode.startVoting()
        time.sleep(float(settings.getVoteTimeSetting()))
        print(playSong())
        mode.continueWatching()
    elif playNextSong == "1" or "update":
        mode.updateInternal()
        playSong()
        mode.continueWatching()
    
      
def stream_handler(post):
    print(post["event"]) # put
    print(post["path"]) # /-K7yGTTEp7O549EzTYtI
    print(post["data"]) # {'title': 'Pyrebase', "body": "etc..."}
            
def playSong():
    nextSong = ""
    curentlyPlaying = ""
    songQueue = {}
    songQueueFile = {}
    songQueueDuration = 0
    db = firebasePyre.database()
    songs = db.child("Rooms").child("00001").get()
    highestVote = 0
    
    
    for song in songs.each():
        if song.val().get("votes") > highestVote:
            highestVote = song.val().get("votes")
            songDuration = song.val().get("duration")
            nextSong = song.val().get("title")
            currentlyPlaying = song.val().get("title")
            songQueue.update({nextSong:songDuration})
            print("highest vote is" + str(highestVote))
        else:
            songDuration = song.val().get("duration")
            nextSong = song.val().get("title")
            songQueue.update({nextSong:songDuration})
            
    if highestVote == 0:
        print("all votes are equal")
        #print(songDuration)
    for files in os.listdir(musicFolder):
        if nextSong in files:
            song = "/home/pi/Music/" + files
            subprocess.call(["omxplayer","-o","local",song])
            print("now playing" + " " + nextSong)
            print(resetVotesInternal())
    time.sleep(songDuration)

        
'''Possible Classes'''
class preferences(object):
    def __init__(self,voteTimeSetting,voteCycleSetting):
        self.voteTimeSetting = voteTimeSetting
        self.voteCycleSetting = voteCycleSetting
    def setVoteTimeSetting(self,voteTime):
        voteTime = shelve.open("options")
        self.voteTimeSetting = voteTime
        voteTime["voteTime"] = str(self.voteTimeSetting)
        voteTime.close()
    def setVoteCycleSetting(self,cycle):
        voteCycle = shelve.open("options")
        self.voteCycleSetting = cycle
        voteCycle["voteCycle"] = str(self.voteCycleSetting)
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
        Firebase.patch("/Rooms/00001/voters",{"placeholder":"voted"})

    
        songs = db.child("Rooms").child("00001").get()
        highestVote = 0
    
        for song in songs.each():
            print(song)
            if song.val().get("votes") > highestVote:
                highestVote = song.val().get("votes")
                print("highest vote is" + highestVote)
            else:
                print("no votes")
        
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
        songQueue = {}
        songQueueFile = {}
        songQueueDuration = 0
        db = firebasePyre.database()
        my_stream = db.child("Rooms").child("00001").stream(stream_handler)
        time.sleep(float(self.voteTime))
        songsByScore = db.child("Rooms").child("00001").order_by_child("votes").limit_to_first(15).get()
        for song in songsByScore.each():
            if songQueueDuration >= int(self.voteCycle)*60:
                break
            songQueue.update({song.val().get("title"):song.val().get("duration")})
            songQueueDuration += int(song.val().get("duration"))
            #print(songQueueDuration)
            #print(song.val().get("title"))
            
        for song in songQueue:
            for file in os.listdir(musicFolder):
                if song in file:
                    songQueueFile.update({file:songQueue[song]})
        #print(songQueue)
        if len(songQueueFile) > 1:
            for song in songQueueFile[1:]:
                print("now playing" + " " + songQueueFile[song])
                subprocess.call(["omxplayer","-o","local",song])
        else:
            subprocess.call(["pkill","omx"])
            
        subprocess.call(["pkill","omx"])
        self.startVoting()
            
def mainMenu():
    
    
        
    #mode = input("What is the mode?\n 1.internal update\n 2.internal\n 3.preferences\n")
    print("Select Mode")
    internalButton = Button(15,pull_up=False,bounce_time=None)
    voteButton = Button(21,pull_up=False,bounce_time=None)
    while True:
        if internalButton.is_pressed:
            mode = "internal"

            break
    if mode == "Spotify":
        menu = 0
        print("tet")
        #spotify work
    elif mode == "internal update":
        #print(internal())
        playNextSong = input("Play next song? (y/n)")
        if playNextSong == "y":
            print(playSong())
            print(continueWatching(songDuration))
    elif mode == "preferences":
        getSetting = shelve.open("options")
        cycle = int(input("how often is the voting cycle (0 for after every song; any other number is per minute"))
        settings.setVoteCycleSetting(cycle)
        getSetting["voteCycle"] = cycle
        Time = int(input("How much time is availible to vote?"))
        settings.setVoteTimeSetting(Time)
        getSetting["voteTime"] = Time
        getSetting.close()
        
        mainMenu()
    

    elif mode == "internal":
        mode = internal(settings.getVoteTimeSetting(),settings.getVoteCycleSetting())
        print("1.update\n 2.start voting\n")
        
        while True:
            if voteButton.is_pressed:
                playNextSong = "start voting"
                print("start voting")
                break
            elif internalButton.is_pressed:
                playNextSong = "update"
                print("update")
                break
        if playNextSong == "2" or "start voting":
            print(str(settings.voteTimeSetting) + " " + " seconds to vote!")
            mode.startVoting()
            time.sleep(float(settings.getVoteTimeSetting()))
            print(playSong())
            mode.continueWatching()
        elif playNextSong == "1" or "update":
            mode.updateInternal()
            playSong()
            mode.continueWatching()
    elif mode == "debug":
        debugOption = input("1.")
    else:
        print("Not a valid option")
        mainMenu()
    
getSetting = shelve.open("options")
#options = list(getSetting.keys())
# options[0] is the cycle options[1] is the time
settings = preferences(getSetting["voteTime"],getSetting["voteCycle"])
getSetting.close()
print(settings.getVoteCycleSetting(),settings.getVoteTimeSetting())
mainMenu()


    


        
    
        
            



