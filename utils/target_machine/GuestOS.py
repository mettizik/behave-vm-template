
OS_TO_PM_MAPPING = {
    'ubuntu': 'apt-get',
    'centos': 'yum'
}

PACKAGE_MANAGER = {
    'apt-get': {
        'name': 'apt-get',
        'update_cmd': 'update -y',
        'install_cmd': 'install -y',
        'uninstall_cmd': 'remove -y'
    },
    'yum': {
        'name': 'yum',
        'update_cmd': 'update -y',
        'install_cmd': 'install -y',
        'uninstall_cmd': 'remove -y'
    }
}


class GuestOS(object):
    def __init__(self, distro, bitness):
        self.distro = distro.lower()
        pm_name = OS_TO_PM_MAPPING[self.distro]
        self.pm = PACKAGE_MANAGER[pm_name]
        self.bitness = int(bitness)

    def pm_update(self):
        return '{name} {update_cmd}'.format(**self.pm)

    def pm_install(self, packages_list):
        return '{name} {install_cmd} {packages}'.format(**self.pm, packages=packages_list)

    def pm_uninstall(self, packages_list):
        return '{name} {uninstall_cmd} {packages}'.format(**self.pm, packages=packages_list)
