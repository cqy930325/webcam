# -*- coding: utf-8 -*-
__author__ = 'gjerryfe'

import settings
import logging
import logging.handlers


handler = logging.handlers.RotatingFileHandler(settings.LOG_FILE, maxBytes = 1024*1024, backupCount = 5) # 实例化handler
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

logger = logging.getLogger('bb8')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

#logger.debug('first debug message')
