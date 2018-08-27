from vagrant import Vagrant
from utils.target_machine.SSHWrapper import ssh_connect, SSHClient
from utils.target_machine.GuestOS import GuestOS
from time import sleep


class VagrantWrapper(object):
    def __init__(self, root_dir, env):
        self.instance = Vagrant(root=root_dir)
        self.env = env
        self.target = GuestOS(env[:-2], env[-2:])

    def up(self):
        return self.instance.up(vm_name=self.env)

    def destroy(self):
        return self.instance.destroy(vm_name=self.env)

    def reboot(self, timeout=120):
        try:
            with self.ssh() as ssh:
                ssh.execute('sudo reboot', no_stderr_expected=False)
        except:
            # SSH can be broken on reboot - ignore this error
            pass

        # waiting for reboot to take place
        # TODO remove this spleep
        sleep(2)
        self.up()
        wait_for_ssh(self, timeout)

    def __get_ssh_params(self):
        return self.instance.user_hostname_port(vm_name=self.env), self.instance.keyfile(vm_name=self.env)

    def ssh(self) -> SSHClient:
        return ssh_connect(*self.__get_ssh_params())


def wait_for_ssh(vm, timeout):
    seconds_lasted = 0
    while seconds_lasted < timeout:
        try:
            with vm.ssh() as ssh:
                ssh.execute('echo dummy')
                break
        except:
            pass
        sleep(1)
        seconds_lasted += 1

    if seconds_lasted >= timeout:
        raise TimeoutError(
            'Failed to connect to VM after reboot in {} seconds'.format(timeout))
