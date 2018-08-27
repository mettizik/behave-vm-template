from behave import given, when, then
from utils.target_machine import VagrantWrapper
from time import sleep


def get_vagrant_instance(context) -> VagrantWrapper:
    return context.vagrant


@given(u'Agent installation archive is extracted to guests {extraction_path}')
def given_agent_is_extracted(context, extraction_path):
    vm = get_vagrant_instance(context)
    with vm.ssh() as ssh:
        output = ssh.execute('mkdir -p {}'.format(extraction_path))
        agent_installer_filename = 'agent_x86.tar.gz'
        if vm.target.bitness == 64:
            agent_installer_filename = 'agent_x64.tar.gz'

        output = ssh.execute(
            'gzip -cd /vagrant/{agent_installer_filename} | tar -x --directory {extraction_path}'.format(
                extraction_path=extraction_path,
                agent_installer_filename=agent_installer_filename))
        output = ssh.execute(
            'ls -l {}/ | grep -w install.sh | wc -l'.format(extraction_path))
        assert output[-1].strip() == '1', 'Failed to find install.sh script under target directory {}'.format(extraction_path)


@when(u'"{command}" is executed by root')
def when_command_is_sudo_executed(context, command):
    vm = get_vagrant_instance(context)
    with vm.ssh() as ssh:
        ssh.execute(
            'sudo {}'.format(command), no_stderr_expected=False)


@when(u'target is rebooted')
def when_target_is_rebooted(context):
    vm = get_vagrant_instance(context)
    vm.reboot()


@then(u'{count} {process_name} processes are started less than in {timeout} seconds')
def then_processes_are_started(context, count, process_name, timeout):
    vm = get_vagrant_instance(context)
    seconds_lasted = 0
    count_of_running_processes = 0
    with vm.ssh() as ssh:
        while seconds_lasted < int(timeout):
            output = ssh.execute(
                'ps -A | grep -w {} | wc -l'.format(process_name), no_stderr_expected=False)
            count_of_running_processes = output[-1].strip() if len(
                output) > 0 else '0'
            if count_of_running_processes == str(count):
                break
            sleep(1)
            seconds_lasted += 1

    if count_of_running_processes != str(count):
        raise TimeoutError('{} processes of {} not started in {} seconds'.format(
            count, process_name, timeout))
