"""
ChatterBot is a machine learning, conversational dialog engine.
"""
from .chatterbot import ChatBot

try:
    import os
    os.system("python -m spacy download en")
except:
    pass
__all__ = (
    'ChatBot',
)
