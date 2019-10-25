# -*- coding: utf-8 -*-
import time
import traceback
import json
import uuid
import warnings
import socketio
import sys

from stakion import publishers

class StakionSender(object):
    """Stakion logger.
    
    Parameters
    ----------
    api_key: str
        Api Key as generated in the Stakion dashboard.
    project_id: str
        Project ID as generated in the Stakion dashboard.
    host: str, optional
        Target host. Does not need to be supplied in the majority of cases.
    bufmax: int, optional
        Maximum number of bytes in the message queue before the
        buffer overflow handler is called. This can happen when messages don't
        get acknowledged by Stakion. Default is 1.024MB.
    buffer_overflow_handler: func, optional
        Buffer overflow handler is called when bufmax is exceeded. A list of
        dictionaries is passed.
    method: str, optional
        The method to send the messages. Currently the only supported values
        is POST.
    
    """
    def __init__(self,
                 api_key,
                 project_id,
                 host=None,
                 bufmax=1 * 1024 * 1024,
                 buffer_overflow_handler=None,
                 method='POST'):
        self.api_key = api_key
        self.project_id = project_id
        self.bufmax = bufmax
        self.buffer_overflow_handler = buffer_overflow_handler
        
        self.pendings = {}
        
        # Unsupported method
        if method not in ['POST']:
            raise ValueError("Method is not supported - valid values are: [POST]")
        
        if host is None:
            if method == 'POST':
                auth_url = 'https://mamooh-223220.appspot.com/auth'
                url = 'https://mamooh-223220.appspot.com/log/' + project_id
        else:
            if method == 'POST':
                if host[-1] == '/':
                    url = host + 'log/' + project_id
                    auth_url = host + 'auth'
                else:
                    url = host + '/log/' + project_id
                    auth_url = host + '/auth'
        
        # Initialise the publisher
        if method == 'POST':
            self.publisher = publishers.publisherPost(
                url=url,
                auth_url=auth_url,
                api_key=api_key
            )
    
    def _validate(self, data):
        """Validate data object"""
        if data is not None:
            if isinstance(data, dict):
                for key, val in data.items():
                    if not isinstance(key, str):
                        raise TypeError('Feature names should be strings')
                    if not isinstance(val, (float, int)):
                        raise TypeError('Stakion currently only supports features of type int or float')
            else:
                raise TypeError('data must be a dictionary or None')
        
        return data
    
    def publish(self, correlation_id, event_type, model, data=None):
        """Push log message for analysis.
        
        Parameters
        ----------
        correlation_id: str
            The correlation ID identifies a unique prediction and will be
            used to link mupltiple log messages to a single prediction. This
            is especially useful to link input features to output features.
        event_type: str
            Log type, supported values are: prediction_requested,
            input_features, output_features, crash_logger, error.
        model: str
            Model name
        data: dict, optional
            Log message.
        """
        timestamp = int(round(time.time() * 1000))
        
        # Validate data
        data = self._validate(data)
        
        try:
            msg = self._make_message(
                correlation_id=correlation_id,
                event_type=event_type,
                model=model,
                timestamp=timestamp,
                data=data)
        except Exception:
            data = {
                "level": "CRITICAL",
                "message": "Can't output to log",
                "traceback": traceback.format_exc()
            }
            msg = self._make_message(
                correlation_id=correlation_id,
                event_type="crash_logger",
                model=model,
                timestamp=timestamp,
                data=data)
        
        return self._send(msg)
    
    def _make_message(self, correlation_id, event_type, model, timestamp, data):
        """Create and validate message from log.
        
        Parameters
        ----------
        correlation_id: str
        event_type: str
        model: str
        timestamp: int
        data: dict
        """
        # Create message
        message = {'project_id': self.project_id,
                   'correlation_id': correlation_id,
                   'event_type': event_type,
                   'model': model,
                   'timestamp': timestamp,
                   'data': data}
        
        # Validate message
        self._validate_message(message)
        
        return message
    
    def _validate_message(self, message):
        """Validate a message
        
        This function currently validates the event_type only.
        
        Parameters
        ----------
        message: dict
            Message as generated by _make_message
        """
        # Event types
        supported_event_types = ['prediction_requested', 'info', 'dependencies', 'input_features',
                                 'output_features', 'crash_logger', 'error']
        
        event_type = message['event_type']
        if event_type not in supported_event_types:
            raise warnings.warn(
                'Event type not supported: The event type ' +
                event_type + ' was passed ' +
                'but only the following event types are '+
                'supported ' + ', '.join(supported_event_types) +
                '. As such no aggregation will be performed.'
            )
    
    def _remove_pending(self, id):
        """Remove message from pending list following acknowledgement.
        
        Parameters
        ----------
        id: str
            Message id
        """
        try:
            self.pendings.pop(id)
        except KeyError:
            print('Issue removing pending message')
    
    def _send(self, message):
        """Send formated log message.
        
        Parameters
        ----------
        message: dict
        """
        # clear buffer if it exceeds max buffer size
        if len(self.pendings.keys()) > 0:
            bufsize = len(self.pendings)#sum(len(json.dumps(s).encode('utf-8')) for s in self.pendings.values())
            if (bufsize > self.bufmax):
                messages_in_buffer = self.pendings.values()
                self._call_buffer_overflow_handler(messages_in_buffer)
                self.pendings = {}
        
        # Create unique message id
        message_id = uuid.uuid4().hex
        message['__uuid'] = message_id
        
        self.pendings[message_id] = message
        self.publisher.emit(message=message, callback=self._remove_pending)
    
    def _call_buffer_overflow_handler(self, pending_events):
        """Call buffer overflow handler."""
        try:
            if self.buffer_overflow_handler:
                self.buffer_overflow_handler(pending_events)
        except Exception:
            # User should care any exception in handler
            pass
    