import pygame
import os


# todo may add music as yield generator queue

class MusicPlayer(object):
    def __init__(self, soundboard):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        self.sound_board = soundboard

        for sound in self.sound_board:
            if type(self.sound_board[sound]) == dict:
                self.sound_board[sound]["FILE"].set_volume(self.sound_board[sound]["VOLUME"])

    @staticmethod
    def play_background_music(song, path="", times=-1, volume=None):
        """
        play a song in background
        :param song: songname
        :param path: path
        :param times: loops -1 = inf
        :param volume: volume
        :return: None
        """
        pygame.mixer_music.load(os.path.join(path, song))
        if volume is not None:
            pygame.mixer_music.set_volume(volume)
        pygame.mixer_music.play(times)

    @staticmethod
    def add_queue(file, path=""):
        """
        adds song to queu
        :param file: filename
        :param path: path
        :return:
        """
        pygame.mixer_music.queue(os.path.join(path, file))

    def play_sound(self, sound):
        """
        play a sound
        :param sound:soundname
        :return: None
        """
        self.sound_board[sound].play()

    @staticmethod
    def fade_out(delay):
        """
        fade out main music
        :param delay: ms
        :return: None
        """
        pygame.mixer_music.fadeout(delay)

    @property
    def volume(self):
        """
        get current music volume
        :return: None
        """
        return pygame.mixer_music.get_volume()

    @volume.setter
    def volume(self, value):
        """
        set current music volume
        :param value: new volume
        :return: None
        """
        pygame.mixer_music.set_volume(value)

    @staticmethod
    def pause_music():
        """
        pause music
        :return: None
        """
        pygame.mixer_music.pause()

    @staticmethod
    def unpause():
        """
        unpause music
        :return: None
        """
        pygame.mixer_music.unpause()

    @staticmethod
    def stop_music():
        """
        stops music
        :return: Nnoe
        """
        pygame.mixer_music.stop()

    @staticmethod
    def rewind_music():
        """
        restart music
        :return: None
        """
        pygame.mixer_music.rewind()

    def queue_music(self, filename):
        """
        queue music
        :param filename: name of song
        :return: None
        """
        pygame.mixer_music.queue(self.music_board[filename])
