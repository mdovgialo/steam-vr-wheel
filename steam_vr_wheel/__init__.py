import json
import os, sys
import threading

import time

if sys.platform == 'win32':
    local = os.getenv('LOCALAPPDATA')
    CONFIG_PATH = os.path.join(local, 'steam-vr-wheel', 'config.json')
else:
    CONFIG_PATH = os.path.expanduser(os.path.join('~', '.steam-vr-wheel', 'config.json'))

DEFAULT_CONFIG = dict(trigger_pre_press_button=True, trigger_press_button=True, multibutton_trackpad=True,
                      multibutton_trackpad_center_haptic=True)


class ConfigException(Exception):
    pass


class PadConfig:
    def _load_default(self):
        self._data = DEFAULT_CONFIG
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        self._write()

    def __init__(self, load_defaults=False):
        if load_defaults:
            self._load_default()
        else:
            try:
                with open(CONFIG_PATH) as f:
                    try:
                        self._data = json.load(f)
                    except json.decoder.JSONDecodeError as e:
                        raise ConfigException(str(e))
                    self.validate_config()
            except FileNotFoundError:
                self._load_default()
        self.mtime = os.path.getmtime(CONFIG_PATH)
        self.check_thr = threading.Thread(target=self._check_config)
        self.check_thr.daemon = True
        self.check_thr.start()
        self.data_lock = threading.Lock()

    def validate_config(self, data=None):
        if data is None:
            data = self._data
        for key, value in DEFAULT_CONFIG.items():
            try:
                assert type(data[key]) == type(value)
            except KeyError:
                raise ConfigException("Missing key: {}".format(key))
            except AssertionError:
                raise ConfigException("Wrong type for key: {}:{}".format(key, data[key]))

    def _check_config(self):
        while True:
            newmtime = os.path.getmtime(CONFIG_PATH)
            try:
                with open(CONFIG_PATH) as f:
                    data_new= json.load(f)
                    self.validate_config(data_new)
                    with self.data_lock:
                        self._data = data_new
                if newmtime != self.mtime:
                    self.mtime = newmtime
            except (ConfigException, json.decoder.JSONDecodeError):
                pass
            time.sleep(0.1)

    def _write(self):
        try:
            with open(CONFIG_PATH, 'x') as f:
                 json.dump(self._data, f)
        except FileExistsError:
            with open(CONFIG_PATH, 'w') as f:
                 json.dump(self._data, f)

    @property
    def trigger_pre_press_button(self):
        with self.data_lock:
            return self._data['trigger_pre_press_button']

    @trigger_pre_press_button.setter
    def trigger_pre_press_button(self, x: bool):
        with self.data_lock:
            self._data['trigger_pre_press_button'] = x
        self._write()

    @property
    def trigger_press_button(self):
        with self.data_lock:
            return self._data['trigger_press_button']

    @trigger_press_button.setter
    def trigger_press_button(self, x: bool):
        with self.data_lock:
            self._data['trigger_press_button'] = x
        self._write()

    @property
    def multibutton_trackpad(self):
        with self.data_lock:
            return self._data['multibutton_trackpad']

    @multibutton_trackpad.setter
    def multibutton_trackpad(self, x: bool):
        with self.data_lock:
            self._data['multibutton_trackpad'] = x
        self._write()

    @property
    def multibutton_trackpad_center_haptic(self):
        with self.data_lock:
            return self._data['multibutton_trackpad_center_haptic']

    @multibutton_trackpad_center_haptic.setter
    def multibutton_trackpad_center_haptic(self, x: bool):
        with self.data_lock:
            self._data['multibutton_trackpad_center_haptic'] = x
        self._write()
