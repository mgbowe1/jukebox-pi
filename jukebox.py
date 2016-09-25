import time,sys
import pygame
import grovepi

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

#Update the display without erasing the display
def setText_norefresh(text):
    textCommand(0x02) # return home
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
		
# example code
if __name__=="__main__":
    isPaused = True
    genre_playlists = ["Top 40", "EDM", "Instr EDM", "Orchestra", "Classical", ""]
    setRGB(255, 128, 0)
    chrPlayPause = ''
    if isPaused == False:
        chrPlayPause = "Pause"
    else:
        chrPlayPause = "Play"
    up = 2
    down = 3
    select = 4
    pcounter = 0
    selectedCounter = 0
    grovepi.pinMode(up, "INPUT")
    grovepi.pinMode(down, "INPUT")
    grovepi.pinMode(select, "INPUT")
    pygame.init()
    pygame.mixer.music.load("test.mp3")
    spaces1 = " " * (16 - len(genre_playlists[pcounter]) - len(chrPlayPause))
            
    spaces2 = " " * (16 - len(genre_playlists[pcounter + 1]) - len(chrPlayPause))
    setText(genre_playlists[pcounter] + spaces1 + chrPlayPause +
            genre_playlists[pcounter + 1] + spaces2 + " ")
    while True:
        if grovepi.digitalRead(up) > 0:
            if pcounter > 0:
                pcounter -= 1
            spaces1 = " " * (16 - len(genre_playlists[pcounter]) - len(chrPlayPause))
            spaces2 = " " * (16 - len(genre_playlists[pcounter + 1]) - len(chrPlayPause))
            setText(genre_playlists[pcounter] + spaces1 + chrPlayPause +
                    genre_playlists[pcounter + 1] + spaces2 + " ")
            print "up"
        if grovepi.digitalRead(down) > 0:
            if pcounter < 4:
                pcounter += 1
            spaces1 = " " * (16 - len(genre_playlists[pcounter]) - len(chrPlayPause))
            spaces2 = " " * (16 - len(genre_playlists[pcounter + 1]) - len(chrPlayPause))
            setText(genre_playlists[pcounter] + spaces1 + chrPlayPause +
                    genre_playlists[pcounter + 1] + spaces2 + " ")
            print "down"
        if grovepi.digitalRead(select) > 0:
            if pcounter == selectedCounter:
                if isPaused:
                    pygame.mixer.music.play()
                    isPaused = False
                    chrPlayPause = "Pause"
                else:
                    pygame.mixer.music.pause()
                    isPaused = True
                    chrPlayPause = "Play"
            else:
                selectedCounter = pcounter
                isPaused = False
                pygame.mixer.music.play()
                chrPlayPause = "Pause"
                
            print "select"
        time.sleep(0.1)

