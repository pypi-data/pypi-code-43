import clr
clr.AddReference("System.Windows.Forms")
import System.Windows.Forms as WinForms


class MessageFilter(WinForms.IMessageFilter):
    __namespace__ = 'System.Windows.Forms'

    def PreFilterMessage(self, msg):
        # print('filter', msg)
        return False


class HelloApp(WinForms.Form):
    def __init__(self):
        self.textbox = WinForms.TextBox()
        self.textbox.Text = "Hello World"
        self.Controls.Add(self.textbox)


def main():
    form = HelloApp()
    app = WinForms.Application
    f = MessageFilter()
    app.AddMessageFilter(f)
    app.Run(form)


if __name__ == '__main__':
    main()
