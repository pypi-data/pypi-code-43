# Time constants
Second                          = 1.
Minute                          = 60 * Second
Hour                            = 60 * Minute
Day                             = 24 * Hour
Week                            = 7 * Day
Year                            = 365.25 * Day

# CoreClasses constants
MAX_FIFO                        = 100000

# StoreGateSvc constants
relative_save_dir               = 'saves/'

# Watchdog constants
DEFAULT_METHOD_ENABLE           = True
DEFAULT_METHOD_TIMEOUT          = 10 * Second
DEFAULT_METHOD_ACTION           = 'reset'
WDT_WRITE_ATTEMPTS              = 5
WDT_FILENAME                    = '/dev/watchdog'
WDT_FILE_OPTIONS                = 'wb+'
WDT_WRITE_FAIL_REBOOT_TIMEOUT   = 5

# NTPSyncService constants
REF_TIME_1970                   = 2208988800
DEFAULT_UPDATE_DELAY            = 1 * Hour