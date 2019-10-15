from ddcmaker import LSC_Client

lsc = LSC_Client.LSC_Client()
class showlib(object):
    def hiphop(self):
        print("机器人给大家表演街舞！")
        lsc.RunActionGroup(16, 1)
        lsc.WaitForFinish(60000)
        # print("机器人给大家表演街舞！")
    def jiangnanstyle(self):
        print("机器人给大家表演江南style！")
        lsc.RunActionGroup(17, 1)
        lsc.WaitForFinish(60000)
        # print("机器人给大家表演江南style！")
    def smallapple(self):
        print("机器人给大家表演小苹果！")
        lsc.RunActionGroup(18, 1)
        lsc.WaitForFinish(60000)
        # print("机器人给大家表演小苹果！")
    def lasong(self):
        print("机器人给大家表演LASONG！")
        lsc.RunActionGroup(19, 1)
        lsc.WaitForFinish(60000)
        # print("机器人给大家表演LASONG！")
    def feelgood(self):
        print("机器人给大家表演倍儿爽！")
        lsc.RunActionGroup(20, 1)
        lsc.WaitForFinish(60000)
        # print("机器人给大家表演倍儿爽！")

