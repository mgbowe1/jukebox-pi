import time,sys
import pygame
import grovepi

# BEGIN GrovePi code

if sys.platform == 'uwp':
    import winrt_smbus as smbus
    bus = smbus.SMBus(1)
else:
    import smbus
    import RPi.GPIO as GPIO
    rev = GPIO.RPI_REVISION
    if rev == 2 or rev == 3:
        bus = smbus.SMBus(1)
    else:
        bus = smbus.SMBus(0)

# this device has two I2C addresses
DISPLAY_RGB_ADDR = 0x62
DISPLAY_TEXT_ADDR = 0x3e

# set backlight to (R,G,B) (values from 0..255 for each)
def setRGB(r,g,b):
    bus.write_byte_data(DISPLAY_RGB_ADDR,0,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,1,0)
    bus.write_byte_data(DISPLAY_RGB_ADDR,0x08,0xaa)
    bus.write_byte_data(DISPLAY_RGB_ADDR,4,r)
    bus.write_byte_data(DISPLAY_RGB_ADDR,3,g)
    bus.write_byte_data(DISPLAY_RGB_ADDR,2,b)

# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)

# set display text \n for second line(or auto wrap)     
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))

# END GrovePi code
	
playlists = ["EDM", "Acoustic", "Orchestra", "Upbeat", "Jazz"]


def run():
    jukebox     = Jukebox(playlists)
    up, down, select, pcounter, selectedCounter = 2, 3, 4, 0, None
    grovepi.pinMode(up, "INPUT")
    grovepi.pinMode(down, "INPUT")
    grovepi.pinMode(select, "INPUT")
    
    while True:
        if grovepi.digitalRead(up) > 0:
            if pcounter > 0:
                pcounter -= 1
            else:
                pcounter = jukebox.getSize() - 1
            jukebox.display_text(pcounter)
            print "up" 
                
        elif grovepi.digitalRead(down) > 0:
            if pcounter < jukebox.getSize() - 1:
                pcounter += 1
            else:
                pcounter = 0;
            print "down" 
            jukebox.display_text(pcounter)
            
        elif grovepi.digitalRead(select) > 0:
            print "pcounter = ", pcounter, " selectedcounter = ",
            print selectedCounter
            if pcounter == selectedCounter:
                print "pausing playlist", jukebox.playlists[pcounter]
                selectedCounter = None
                jukebox.pauseIt()
            else:
                print "playing playlist", jukebox.playlists[pcounter]
                selectedCounter = pcounter
                jukebox.playmusic(pcounter)
            jukebox.display_text(pcounter)
            

            
        time.sleep(0.1)


class Jukebox:
    def __init__(self, playlists):
        self.playlists      = playlists
        self.playing        = False
        self.playingCounter = None
        setRGB(255, 128, 0)
        self.display_text(0)
    def getSize(self):
        return len(self.playlists)
    def isPlaying(self):
        return self.playing
    def playmusic(self, pcounter):
        if self.playingCounter == pcounter:
            pygame.mixer.music.unpause()
        else:
            self.playingCounter = pcounter
            pygame.init()
            pygame.mixer.music.load(self.playlists[pcounter] + "/song.mp3")
            pygame.mixer.music.play()
        self.playing = True
    def pauseIt(self):
        self.playing = False
        pygame.mixer.music.pause()
    def display_text(self, pcounter):
        '''
        Display text on to the Grove LCD in the following format:
            ----------------------
            |Top 40          PLAY|
            |EDM                 |
            ----------------------
        Takes two paramters. pcounter points to the playlist the user is
        currently looking at.
        '''
        # "PAUSE" if user navigated to a track that is currently being played.
        # "PLAY" otherwise.
        if self.isPlaying() and pcounter == self.playingCounter:
            playOrPause = "PAUSE"
        else:
            playOrPause = "PLAY"
        # The display of playlists wraps around.
        if pcounter == self.getSize() - 1:
            nextpcounter = 0
        else:
            nextpcounter = pcounter + 1
        spaces1 = " " * (16 - len(playlists[pcounter]) - len(playOrPause))

        
        setText(playlists[pcounter] + spaces1 + playOrPause +
                playlists[nextpcounter])
        


if __name__ == "__main__":
    run()
