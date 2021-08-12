import logging
import os
from datetime import datetime
import time
from django.conf import settings

# Get an instance of a logger
logger = logging.getLogger(__name__)


class LogMe():
    log_setting = str(settings.LOGGING['root']['level'])
    go_ahead = False
    if log_setting == 'INFO' or log_setting == 'DEBUG':
        go_ahead = True
    elif log_setting == 'CRITICAL':
        go_ahead = False
    if not go_ahead:
        pass

    fd          = ''
    starttime   = 0
    startmem    = 0
    filename    = 'logbucket'
    off_csv     = True
    full_debug  = False

    def __init__(self, modulename = 'view'):
        self.filename = os.path.join(self.filename, modulename+'.csv')
        self.fd = open(self.filename, 'w')
        self.fd.write("TIMESTAMP, COMMENT, TIMEDELTA, MEMDELTA\n")
        self.fd.close()
        if self.log_setting == 'DEBUG':
            self.turn_on_csv_writing()
            self.turn_on_full_debug()

    def turn_on_csv_writing(self):
        self.off_csv = False

    def turn_off_csv_writing(self):
        self.off_csv = True

    def turn_on_full_debug(self):
        self.full_debug = True

    def turn_off_full_debug(self):
        self.full_debug = False

    def one_string(self, array):
        return ' '.join([str(elem) for elem in array])

    def fullbari(self, *comment):
        if self.full_debug:
            this_comment = self.one_string(comment)
            logger.info(this_comment)

    def bari(self, comment, starttime = 'c', startmem = 'c'):
        timedelta = ''
        memdelta  = ''
        ts        = str(datetime.now())
        if starttime == 's':
            self.off_csv = False
            self.starttime = time.process_time()
        elif starttime == 'e':
            self.off_csv = False
            timedelta = str(time.process_time() - self.starttime)
            self.starttime = 0
        logger.info(comment+ " "+"("+starttime+")"+ timedelta+"("+startmem+")"+ memdelta)
        if not self.off_csv:
            self.fd = open(self.filename, 'a')
            self.fd.write(ts+','+str(comment)+','+timedelta+','+memdelta+'\n')
            self.fd.close()
