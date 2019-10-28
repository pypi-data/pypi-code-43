import winreg


class ExplorerContextManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    def register_entry(name: str, executable: str, icon: str):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\Background\\shell\\{name}')
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\Background\\shell\\{name}', 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, "", 0, winreg.REG_SZ, name)
            winreg.SetValueEx(registry_key, "Icon", 0, winreg.REG_SZ, icon)
            winreg.CloseKey(registry_key)

            winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}\\command')
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}\command', 0, winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, "", 0, winreg.REG_SZ, executable)
            winreg.CloseKey(registry_key)

            return 0
        except WindowsError:
            return 1

    @staticmethod
    def delete_entry(name: str):
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\Background\\shell\\{name}')
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\Background\\shell\\{name}', 0, winreg.KEY_WRITE)
            winreg.DeleteValue(registry_key, "")
            winreg.DeleteValue(registry_key, "Icon")
            winreg.CloseKey(registry_key)

            winreg.CreateKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}\\command')
            registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}\command', 0, winreg.KEY_WRITE)
            winreg.DeleteValue(registry_key, "")

            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}\\command')
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f'SOFTWARE\\Classes\\Directory\\background\\shell\\{name}')

            winreg.CloseKey(registry_key)

            return 0
        except WindowsError:
            return 1


if __name__ == '__main__':
    # Adds "Run CMD" to the Explorer Context Menu
    print(ExplorerContextManager.register_entry("Run CMD", "C:\\Windows\\System32\\cmd.exe", "C:\\Windows\\System32\\cmd.exe"))
