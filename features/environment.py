from behave import fixture, use_fixture
from os import path
import sys
from utils.target_machine import VagrantWrapper


class UserDataKeys(object):
    VAGRANT_VM = 'VAGRANT_ENV'

    @staticmethod
    def ensureDefined(key, context, message='{key} user parameter is required!'):
        if not key in context.config.userdata:
            raise RuntimeError(message.format(key=key))

        return context.config.userdata[key]


def setup_vagrant_vm(context):
    env = UserDataKeys.ensureDefined(UserDataKeys.VAGRANT_VM, context)
    vagrant_root = path.abspath(path.join(path.dirname(
        path.dirname(__file__)), 'vagrant_environments'))
    vagrant = VagrantWrapper(vagrant_root, env)
    vagrant.up()
    return vagrant


def teardown_vagrant_vm(context):
    if context.vagrant:
        context.vagrant.destroy()


@fixture(name="fixture.vagrant")
def vargant_vm(context, timeout=300, **kwargs):
    # setup VM
    context.vagrant = setup_vagrant_vm(context)
    yield True
    teardown_vagrant_vm(context)
    del context.vagrant


def before_tag(context, tag):
    if tag == "fixture.vagrant":
        use_fixture(vargant_vm, context)
