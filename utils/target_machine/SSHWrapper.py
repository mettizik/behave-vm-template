import re
import paramiko
import logging


class SSHClient(object):
    def __init__(self, impl: paramiko.SSHClient, *connection_args, **connection_kwargs):
        self.__impl = impl
        self.__args = connection_args
        self.__kwargs = connection_kwargs

    def execute(self, command, no_stderr_expected=True, check_exit_code=True):
        logging.info('executing command "{}"'.format(command))
        channel = self.__impl.get_transport().open_session()
        channel.exec_command(command)
        stdout = channel.makefile('r', -1)
        stderr = channel.makefile_stderr('r', -1)
        exit_code = channel.recv_exit_status()
        stderr = stderr.readlines()
        stdout = stdout.readlines()
        logging.info('output: {}'.format(''.join(stdout)))
        logging.info('error: {}'.format(''.join(stderr)))
        logging.info('exit code: {}'.format(exit_code))
        if exit_code != 0:
            raise RuntimeError(
                '{} code returned for ssh command "{}"'.format(exit_code, command))
        if no_stderr_expected and len(stderr) > 0:
            raise RuntimeError(
                'Errors reported, while not expected to be: \n{}'.format(''.join(stderr)))
        return stdout

    def close(self):
        return self.__impl.close()

    def __enter__(self):
        self.__impl.connect(*self.__args, **self.__kwargs)
        return self

    def __exit__(self, *args):
        self.__impl.close()


def ssh_connect(connection_params, keyfile) -> SSHClient:
    opts = re.split("[@:]", connection_params)
    user = opts[0]
    address = opts[1]
    port = int(opts[2])
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    return SSHClient(client, address, port=port,
                     username=user, key_filename=keyfile)
