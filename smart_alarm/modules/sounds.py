import pygame
import pyttsx
import time
from random import randint
import os
import RPi.GPIO as GPIO
import logging


# set button input pin
button_input_pin = 24
# set pin for amplifier switch
amp_switch_pin = 5

# turn off GPIO warnings
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
# set pin to output
GPIO.setup(amp_switch_pin, GPIO.OUT)

# read environmental variable for project path
project_path = os.environ['smart_alarm_path']


class Sound(object):
    """sound class manages smart alarm audio"""

    def __init__(self):
        """initialize variables"""
        # write to error.log file
        logging.info('sound-module initialized')
        self.sound_active = False
        self.stop_sound = False

    def stopping_sound(self):
        """stops alarm when button is pressed"""
        logging.info('sound is being stopped')
        self.stop_sound = True

    def toggle_amp_pin(self):
        # set pwm audio pin one or zero, depending on the current state
        logging.debug("now changing state of amp pin")
        GPIO.output(amp_switch_pin, not GPIO.input(amp_switch_pin))

    def play_mp3_file(self, mp3_file):
        # set output high in order to turn on amplifier
        logging.info('now playing mp3')

        if self.sound_active:
            return

        self.sound_active = True
        GPIO.output(amp_switch_pin, 1)
        time.sleep(0.3)
        pygame.mixer.init()
        pygame.mixer.music.load(mp3_file)
        logging.debug("now playing file: ", mp3_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
            if self.stop_sound:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                logging.debug('mp3 alarm turned off via button pressed')
                break
            else:
                continue
        time.sleep(0.5)
        # set output low in order to turn off amplifier
        GPIO.output(amp_switch_pin, 0)
        pygame.mixer.quit()
        self.sound_active = False
        self.stop_sound = False

    def say(self, text):
        """synthesizes the given text to speech"""
        logging.info('now saying something')
        if self.sound_active:
            return

        self.sound_active = True
        # set output high in order to turn on amplifier
        GPIO.output(amp_switch_pin, 1)
        time.sleep(0.3)
        engine = pyttsx.init()
        engine.setProperty('rate', 125)
        # remove "pass" and uncomment next line in order to enable this function
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.2)
        # set output low in order to turn off amplifier
        GPIO.output(amp_switch_pin, 0)
        self.sound_active = False

    def adjust_volume(self, value):
        """adjusts the audio volume by the given value (0-100%)"""
        logging.debug('adjusting volume')
        volume_command = str('amixer set PCM -- ' + str(value) + '%')
        os.system(volume_command)
        # self.play_mp3_file(project_path + '/sounds/blop.mp3')

    def play_wakeup_music(self):
        """find all mp3 files in the folder /home/pi/music
        and play one of them at random"""
        list_of_music_files = []
        for track in os.listdir(project_path + '/music'):
            if track.endswith(".mp3"):
                list_of_music_files.append(str(project_path + '/music/' + str(file)))

        # figure out random track of the found mp3 files
        random_track = randint(0, len(list_of_music_files)-1)

        self.play_mp3_file(list_of_music_files[random_track])

    def play_online_stream(self):
        """plays online radio using mpc. Press button to stop. Edit mpc playlist by:
        'mpc add filename', 'mpc playlist', 'mpc clear', 'mpc play', 'mpc stop'."""
        if self.sound_active:
            return

        self.sound_active = True

        logging.debug('now playing internet radio')
        # set output high in order to turn on amplifier
        GPIO.output(amp_switch_pin, 1)
        time.sleep(0.3)
        os.system('mpc play')

        while True:
            if self.stop_sound is False:
                pass
            else:
                break

        os.system('mpc stop')
        time.sleep(0.5)
        # set ouput low in order to turn off amplifier
        GPIO.output(amp_switch_pin, 0)
        logging.debug('internet radio alarm turned off')
        self.sound_active = False
        self.stop_sound = False