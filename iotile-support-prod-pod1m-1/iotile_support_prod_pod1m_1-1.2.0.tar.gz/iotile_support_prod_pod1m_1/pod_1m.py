"""Reference meulator for POD-1M."""

from iotile.emulate.reference import ReferenceDevice
from iotile.emulate import EmulatedPeripheralTile
from iotile.core.dev import ComponentRegistry


class POD1MReferenceDevice(ReferenceDevice):
    """Emulator for POD-1M device with an accelerometer and environmental tile.

    Args:
        args (dict): A dictionary of optional creation arguments.  Currently
            supported are:
                iotile_id (int or hex string): The id of this device. This
                    defaults to 1 if not specified.
    """

    STATE_NAME = "pod_1m_ref_device"
    STATE_VERSION = "0.1.0"

    def __init__(self, args):
        super(POD1MReferenceDevice, self).__init__(args)

        reg = ComponentRegistry()
        _name, accel_factory = reg.load_extensions(group="iotile.emulated_tile", product_name="emulated_tile", name_filter='accel1_1',
                                                   class_filter=EmulatedPeripheralTile, unique=True)
        _name, env_factory = reg.load_extensions(group="iotile.emulated_tile", product_name="emulated_tile", name_filter='envbsl_1',
                                                 class_filter=EmulatedPeripheralTile, unique=True)

        self.add_tile(12, accel_factory(12, {}, self))
        self.add_tile(14, env_factory(14, {}, self))

        self.controller.name = b'NRF52 '
        self.controller.load_sgf(SGF_FILE)


SGF_FILE = """
meta app_tag = 2049;
meta app_version = "1.1";

config controller
{
    set 0x2001 to 0 as uint32_t;        # Disable temperature logging in the controller
    set 0x2002 to 900 as uint32_t;      # Default to having tick_1 trigger every 15 minutes
    set 0x2005 to 1 as uint8_t;         # Enable fill-stop mode on output data
}

config slot 2
{
    set 0x8000 to 20 as uint16_t;       # Set the default shock threshold to 1G (20 * 0.049)
    set 0x8005 to 2 as uint8_t;         # Report only the unique id of each shock rather than a summary
    set 0x8006 to 1 as uint8_t;         # Save raw waveforms to flash
    set 0x8009 to 3 as uint32_t;        # Set the minimum shock time to 3 ms
    set 0x8008 to 0 as uint8_t;         # Don't autostart recording, we start on reset automatically
}

# Copy only the unique id of each shock rather than its complete summary data.
# Since the raw waveform is stored in flash on the accelerometer itself, we just need a pointer 
# telling us when it happened, we don't need to duplicate the actual data.
# We store the pointers in output 32, which is the same stream where the waveforms
# will be stored when uploaded by a phone or logistics_app
on input 1
{
    copy => output 32;
}

# Sending system input 1538 pauses/resumes recording
# 1: resume recording
# 0: pause recording
on value(system input 1538) == 0 
{
    copy => constant 1;
    call 0x8035 on slot 2;
    call 0x200e on controller;
}

on value(system input 1538) == 1
{
    copy => constant 1;
    call 0x8036 on slot 2;
    call 0x200e on controller;
}

# When we turn on start recording if we're in recording mode
# This makes sure that we remember whether or not the accelerometer tile
# is sleeping even after a reset
on system input 1024 and value(constant 1) == 1
{
    call 0x8036 on slot 2;
}

# Only save environmental data when we are currently recording
when value(constant 1) == 1
{
    # We use user tick 1 to configure our environmental logging rate
    # The default tick interval is 15 minutes (900 seconds)
    every 1 tick_1
    {
        call 0x8000 on slot 4;
        call 0x8003 on slot 4 => output 34;
        call 0x8002 on slot 4 => output 33;
        call 0x8001 on slot 4 => output 35;
    }
}

# When a user is connected to the controller, enable highspeed,
# realtime data to be streamed to the user's phone every 1 second.
when connected to controller
{
    every 1 second
    {
        call 0x8003 on slot 2 => unbuffered 18;

        call 0x8000 on slot 4;
        call 0x8003 on slot 4 => unbuffered 15;
        call 0x8002 on slot 4 => unbuffered 22;
        call 0x8001 on slot 4 => unbuffered 25;
    }
}


# Create all of our streamers that send data out of the device to 
# a connected user over bluetooth.
manual streamer on all outputs;
manual streamer on all system outputs with streamer 0;
manual streamer on all system buffered with streamer 0;

realtime streamer on unbuffered 18; 
realtime streamer on unbuffered 15;
realtime streamer on unbuffered 22;
realtime streamer on unbuffered 25;
"""
