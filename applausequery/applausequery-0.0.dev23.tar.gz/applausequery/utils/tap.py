# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Module providing access to APPLAUSE TAP service, uses PyVO
"""

import time
import pyvo as vo 

class ApplauseTAP(vo.dal.TAPService):
    """
    Represents APPLAUSE TAP service
    """

    def __init__(self, token=None):
        """
        Instantiate APPLAUSE TAP session

        Parameters
        ----------
        token : str, optional
            Authentication token for personal access to APPLAUSE
        """
        self.__token = token
        if vo.version.major < 1:
            self.__session = vo.utils.http.session
            super().__init__("https://www.plate-archive.org/tap")
        else:
            self.__session = vo.utils.http.create_session()
            super().__init__("https://www.plate-archive.org/tap", session=self.__session)
        if token is not None:
            self.__session.headers['Authorization'] = 'Token ' + token
    

    def set_token(self, token):
        """
        Set authentication token for APPLAUSE

        Parameters
        ----------
        token: str or None
            Authentication token for personal access to APPLAUSE, set to None to unset token
        """
        self.__token = token
        if token is not None:
            self.__session.headers['Authorization'] = 'Token ' + token
        elif token is None:
            try:
                self.__session.headers.pop('Authorization')
            except KeyError:
                pass
    
    def get_token(self):
        """
        Get current authentication token

        Returns
        -------
        token : str
            Authentication token for personal access to APPLAUSE, None means: no token set
        """
        return self.__token
    


