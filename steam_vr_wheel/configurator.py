import sys
import wx

from steam_vr_wheel import PadConfig, ConfigException


class ConfiguratorApp:
    def __init__(self):

        self.app = wx.App()
        self.window = wx.Frame(None, title="Steam Vr Wheel Configuration")
        self.pnl = wx.Panel(self.window)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.trigger_pre_btn_box = wx.CheckBox(self.pnl, label='Triggers pre press button')
        self.trigger_btn_box = wx.CheckBox(self.pnl, label='Triggers press button')
        self.multibutton_trackpad_box = wx.CheckBox(self.pnl, label='5 Button touchpad')
        self.multibutton_trackpad_center_haptic_box = wx.CheckBox(self.pnl,
                                                                  label='Haptic feedback for trackpad button zones')
        self.touchpad_always_updates_box = wx.CheckBox(self.pnl, label='Touchpad mapping to axis while untouched (axis move to center when released)')
        self.vertical_wheel_box = wx.CheckBox(self.pnl, label='Steering wheel is vertical')

        self.trigger_pre_btn_box.Bind(wx.EVT_CHECKBOX, self.config_change)
        self.trigger_btn_box.Bind(wx.EVT_CHECKBOX, self.config_change)
        self.multibutton_trackpad_box.Bind(wx.EVT_CHECKBOX, self.config_change)
        self.multibutton_trackpad_center_haptic_box.Bind(wx.EVT_CHECKBOX, self.config_change)
        self.touchpad_always_updates_box.Bind(wx.EVT_CHECKBOX, self.config_change)
        self.vertical_wheel_box.Bind(wx.EVT_CHECKBOX, self.config_change)

        self._config_map = dict(trigger_pre_press_button=self.trigger_pre_btn_box,
                                trigger_press_button=self.trigger_btn_box,
                                multibutton_trackpad=self.multibutton_trackpad_box,
                                multibutton_trackpad_center_haptic=self.multibutton_trackpad_center_haptic_box,
                                touchpad_always_updates=self.touchpad_always_updates_box,
                                vertical_wheel=self.vertical_wheel_box,)

        self.vbox.Add(self.trigger_pre_btn_box)
        self.vbox.Add(self.trigger_btn_box)
        self.vbox.Add(self.multibutton_trackpad_box)
        self.vbox.Add(self.multibutton_trackpad_center_haptic_box)
        self.vbox.Add(self.touchpad_always_updates_box)
        self.vbox.Add(self.vertical_wheel_box)

        self.pnl.SetSizer(self.vbox)
        self.read_config()
        self.window.Show(True)

    def read_config(self):
        try:
            self.config = PadConfig()
        except ConfigException as e:
            msg = "Config error: {}. Load defaults?".format(e)
            dlg = wx.MessageDialog(self.pnl, msg, "Config Error", wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal() == wx.ID_YES
            dlg.Destroy()
            if result:
                self.config = PadConfig(load_defaults=True)
            else:
                sys.exit(1)
        for key, item in self._config_map.items():
            item.Set3StateValue(getattr(self.config, key))


    def config_change(self, event):
        for key, item in self._config_map.items():
            setattr(self.config, key, item.IsChecked())



    def run(self):
        self.app.MainLoop()


def run():
    ConfiguratorApp().run()

if __name__ == '__main__':
    run()