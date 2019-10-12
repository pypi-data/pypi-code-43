import os
import SCons.Script as scons


# toolchains options
CROSS_TOOL_PATH   = '/opt/gcc-csky-abiv2/bin'

class Builder(object):
    def __init__(self):
        self.PREFIX  = 'csky-elfabiv2-'
        self.CC      = self.PREFIX + 'gcc'
        self.CXX     = self.PREFIX + 'g++'
        self.AS      = self.PREFIX + 'gcc'
        self.AR      = self.PREFIX + 'ar'
        self.LINK    = self.PREFIX + 'g++'
        self.SIZE    = self.PREFIX + 'size'
        self.OBJDUMP = self.PREFIX + 'objdump'
        self.OBJCPY  = self.PREFIX + 'objcopy'
        self.STRIP   = self.PREFIX + 'strip'

        self.AFLAGS  = ''
        self.CCFLAGS  = ''
        self.CXXFLAGS  = ''
        self.LDFLAGS  = ''

        self.DEBUG   = 'release'
        self.INSTALL_PATH = ''
        self.lib_path = ''

        self.env = scons.Environment(tools = ['default'],
            AS   = self.AS,
            CC   = self.CC,
            CXX  = self.CXX,
            AR   = self.AR, ARFLAGS = '-rc',
            LINK = self.LINK,
        )
        # self.env.Decider('timestamp-newer')
        self.env.Decider('make')
        # self.env.Decider('MD5')

        self.env.PrependENVPath('TERM', "xterm-256color")
        self.env.PrependENVPath('PATH', os.getenv('PATH'))

        if scons.GetOption('verbose'):
            self.env.Replace(
                ARCOMSTR = 'AR $TARGET',
                ASCOMSTR = 'AS $TARGET',
                ASPPCOMSTR = 'AS $TARGET',
                CCCOMSTR = 'CC $TARGET',
                CXXCOMSTR = 'CXX $TARGET',
                # LINKCOMSTR = 'LINK $TARGET',
                INSTALLSTR = 'INSTALL $TARGET'
            )

        self.yoc_compile_flags = \
            ' -ffunction-sections -fdata-sections' + \
            ' -g -Wpointer-arith -Wundef -Wall -Wl,-EL' + \
            ' -fno-inline-functions -nostdlib -fno-builtin -mistack' + \
            ' -fno-strict-aliasing -fno-strength-reduce'


    def SetInstallPath(self, path):
        self.INSTALL_PATH = path
        self.lib_path = os.path.join(path, "lib")

    def set_cpu(self, cpu):
        self.CPU = cpu.lower()
        if self.CPU in ['ck801', 'ck802', 'ck803', 'ck805', 'ck803f', 'ck803ef', 'ck803efr1', 'ck803efr2', 'ck803efr3', 'ck804ef', 'ck805f']:
            DEVICE = '-mcpu=' + self.CPU
            if 'f' in self.CPU:
                DEVICE += ' -mhard-float'

            if self.CPU == 'ck803ef':
                DEVICE += ' -mhigh-registers -mdsp'
        else:
            print ('Please make sure your cpu mode')
            exit(0)


        self.CCFLAGS  = ' -MP -MMD ' + DEVICE
        self.AFLAGS  = ' -c ' + DEVICE
        self.LDFLAGS  = DEVICE

        if self.DEBUG == 'debug':
            self.CCFLAGS += ' -O0 -g'
        else:
            self.CCFLAGS += ' -Os'

        self.CCFLAGS  += self.yoc_compile_flags
        self.CXXFLAGS = self.CCFLAGS