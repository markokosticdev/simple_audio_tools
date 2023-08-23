import sys

import wx

from tools.remove_noise.cli import RemoveNoiseCLI


class RemoveNoiseApp(wx.App):
    def OnInit(self):
        frame = RemoveNoiseFrame(None, "Remove Noise from Audio")
        frame.Show()
        return True


class RedirectText:
    def __init__(self, text_ctrl):
        self.output = text_ctrl

    def write(self, string):
        self.output.WriteText(string)

    def flush(self):
        pass
class RemoveNoiseFrame(wx.Frame):
    def __init__(self, parent, title):
        super(RemoveNoiseFrame, self).__init__(parent, title=title, size=(400, 300))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Input folder
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.input_folder_ctrl = wx.DirPickerCtrl(panel)
        hbox1.Add(wx.StaticText(panel, label="Input Folder:"), flag=wx.RIGHT, border=8)
        hbox1.Add(self.input_folder_ctrl, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Output folder
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.output_folder_ctrl = wx.DirPickerCtrl(panel)
        hbox2.Add(wx.StaticText(panel, label="Output Folder:"), flag=wx.RIGHT, border=8)
        hbox2.Add(self.output_folder_ctrl, proportion=1)
        vbox.Add(hbox2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Other parameters
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.silence_thresh_ctrl = wx.SpinCtrl(panel, value='-30', min=-100, max=100)
        self.keep_silence_ctrl = wx.SpinCtrl(panel, value='500', min=-0, max=5000)
        hbox3.Add(wx.StaticText(panel, label="Silence Threshold:"), flag=wx.RIGHT, border=8)
        hbox3.Add(self.silence_thresh_ctrl, flag=wx.RIGHT, border=10)
        hbox3.Add(wx.StaticText(panel, label="Keep Silence:"), flag=wx.RIGHT, border=8)
        hbox3.Add(self.keep_silence_ctrl)
        vbox.Add(hbox3, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        # Button to start processing
        self.process_btn = wx.Button(panel, label="Start Processing")
        self.process_btn.Bind(wx.EVT_BUTTON, self.on_process)
        vbox.Add(self.process_btn, flag=wx.ALIGN_CENTER | wx.TOP, border=10)

        # Add a TextCtrl for terminal output
        self.console_output = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        vbox.Add(self.console_output, proportion=1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=10)

        # Redirect output
        output_text = RedirectText(self.console_output)
        sys.stdout = output_text
        sys.stderr = output_text

        panel.SetSizer(vbox)

    def on_process(self, event):
        # Get all the input values
        input_folder = self.input_folder_ctrl.GetPath()
        output_folder = self.output_folder_ctrl.GetPath()

        # Check if input_folder and output_folder have been provided
        if not input_folder or not output_folder:
            wx.MessageBox("Please select both the input and output folders.", "Error", wx.OK | wx.ICON_ERROR)
            return

        silence_thresh = self.silence_thresh_ctrl.GetValue()
        keep_silence = self.keep_silence_ctrl.GetValue()

        # Create the CLI object and invoke it
        print(input_folder, output_folder, silence_thresh, keep_silence)
        cli = RemoveNoiseCLI(input_folder=input_folder, output_folder=output_folder, silence_thresh=silence_thresh, keep_silence=keep_silence)
        cli.main()

        wx.MessageBox("All audio files processed successfully.", "Info", wx.OK | wx.ICON_INFORMATION)


if __name__ == "__main__":
    app = RemoveNoiseApp()
    app.MainLoop()
