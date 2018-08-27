# Template of Behave autotests with Vagrant VMs
## Table of contents
1. [ Environment setup ](#env)
2. [ Project layout ](#layout)
3. [ Running tests ](#run)
4. [ Adding new Vagrant environment ](#new_env)
5. [ Adding scenario ](#new_scenario)
6. [ Implementing steps ](#new_impl)

## Abstract
Autotests are written using [behave](https://behave.readthedocs.io/en/latest/tutorial.html) framework in Python3.
Under the hood [Vagrant](https://vagrantup.com) VM manager is used to run instances of target environment.

If you are new to behave - start with [official tutorial](https://behave.readthedocs.io/en/latest/tutorial.html) and [examples](http://behave.github.io/behave.example/)

<a name="env"></a>

## Environment setup
To run these tests you need to install:
* [Python3](https://www.python.org/downloads/) interpreter
* [Vagrant](https://www.vagrantup.com/downloads.html)

Python dependencies are listed in `requirements.txt` and can be installed via
```bash
$ pip install -r requirements.txt
```

<a name="layout"></a>

## Project layout
Project is splitted into several root directories:
* `features` - common behave-features-structured directory with features and testing scenarios description
* `vagrant_environments` - root folder of Vagrant project, used as synced folder with target VMs and storing Vagrantfile, which describes environments
* `utils` - different python modules shared between steps implementations


## Running tests
_Assuming you have passed `Environment setup` instructions_.

### Setup
To run tests copy all artifacts, you need, into the vagrant_environments folder. 

### Execution

Running tests for Vagrant-provided VM is simple as it can be:
```bash
$ behave -D VAGRNAT_ENV=ubuntu32
```

Here `VAGRNAT_ENV` is a user configuration flag passed to the tests, describing what environment to test, in example below it is `ubuntu32`.

All environments available are listed in `vagrant_environments/Vagrantfile`.

### Reporting 

To enable JUnit reports in bahave, just add an option `--junit` to the tests launch commandline, reports will be stored in `reports` folder as *.xml files. If you want to specify another directory name for reports saving - just pass it with `--junit-directory` option:

```bash
$ behave -D VAGRNAT_ENV=ubuntu32 --junit --junit-directory=reports/ubuntu32
```

<a name="new_env"></a>

## Adding new Vagrant environment

Adding new test environment in Vagrant requires several actions to be done:
* Add new vm config in Vagrantfile
* Specify OS specific parameters in GuestOS (for example - package manager)

Let's assume the following scenario - adding Arch Linux environment with pacman as a pacakage manager. 

### Adding new vm config in Vagrantfile

So we took an Arch x64 as a target. First we need to add it into Vagrantfile. The naming convention for vms is ${DISTRIBUTIVE}{32|64} where DISTRIBUTIVE is a distro name and 32|64 describes OS bitness. Let's add it:

1 - [Find a box](https://app.vagrantup.com/boxes/search) for Vagrant

2 - Add it to Vagrantfile

For example we will take a generic/arch box. To add it we need to simply define it in Vagrantfile with following snippet:

```
  config.vm.define "arch64" do |arch64|
    arch64.vm.box = "generic/arch"
  end
```

Now Vagrant environment is ready to use. Let's configure params for pacman

### Specify OS specific parameters in GuestOS

In `utils/target_machine/GuestOS.py` you will find a OS specific incapsulating class. What we need to do here is define pacman commands for update, install and remove and bind arch to it.

Adding a PM definistion is done in `PACKAGE_MANAGER` dict:
```
PACKAGE_MANAGER = {
# ...
    'pacman': {
        'name': 'pacman',
        'update_cmd': '-S --noconfirm',
        'install_cmd': '-S --noconfirm',
        'uninstall_cmd': '-R --noconfirm'
    }
}
```

Binding OS to Package manager is done via `OS_TO_PM_MAPPING` dict:
```
OS_TO_PM_MAPPING = {
    'ubuntu': 'apt-get',
    'centos': 'yum',
    'arch': 'pacman'
}
```

### Summary

Overall patch of the above:
```diff
index 58c052a..4135af2 100644
--- a/LinuxAutotests/utils/target_machine/GuestOS.py
+++ b/LinuxAutotests/utils/target_machine/GuestOS.py
@@ -1,7 +1,8 @@

 OS_TO_PM_MAPPING = {
     'ubuntu': 'apt-get',
-    'centos': 'yum'
+    'centos': 'yum',
+    'arch': 'pacman'
 }

 PACKAGE_MANAGER = {
@@ -16,6 +17,12 @@ PACKAGE_MANAGER = {
         'update_cmd': 'update -y',
         'install_cmd': 'install -y',
         'uninstall_cmd': 'remove -y'
+    },
+    'pacman': {
+        'name': 'pacman',
+        'update_cmd': '-S --noconfirm',
+        'install_cmd': '-S --noconfirm',
+        'uninstall_cmd': '-R --noconfirm'
     }
 }

diff --git a/LinuxAutotests/vagrant_environments/Vagrantfile b/LinuxAutotests/vagrant_environments/Vagrantfile
index c51c215..d7244e0 100644
--- a/LinuxAutotests/vagrant_environments/Vagrantfile
+++ b/LinuxAutotests/vagrant_environments/Vagrantfile
@@ -16,4 +16,8 @@ Vagrant.configure("2") do |config|
   config.vm.define "centos64" do |centos64|
     centos64.vm.box = "centos/7"
   end
+
+  config.vm.define "arch64" do |arch64|
+    arch64.vm.box = "generic/arch"
+  end
 end

```


<a name="new_scenario"></a>

## Adding new scenarios

Defining new scenarios for autotests should be done either by QA engineer or by BA specialist. Scenario description in general cases sould not be specific for some target (for example - avoid of cases like 'run apt-get update', since the package managers can differ on different platforms).

Still scenarios should contain enough information to make it clear for the developer **what** should be tested and what the expectations are. It is a good practice to include some parameters in scenario description, though the same implementation could be used for different purposes. For example:
```
  then 2 instances of bash are running
```
implementation for this scenario can be used also for similar scenarios, like:
```
  then 5 instances of nc are running
```

### Create feature file or take existing

Specifying scenario starts from feature file selection. It is a general `behave`'s recomendation to store features description in feature files. For example `login`, `logout`, `dashboard` instead of `user_interaction`, `reporting`, etc..

It is all about test design - what structure and naming conventions to use.

All `*.feature` files should be stored in `features` folder. You can find more information in [Behave's tutorials](https://behave.readthedocs.io/en/latest/tutorial.html#features).

### Write scenario

Read the [docs](https://behave.readthedocs.io/en/latest/tutorial.html#feature-files) and Gherkin syntax tutorials to know more about language used for specifying features.

### Add tags and fixtures

Some scenarios can require some setup and teardown of environment (VM start/stop, temp folders creation/removal, etc.). All this staff is done via [@fixtures](https://behave.readthedocs.io/en/latest/tutorial.html#fixtures). This is just a tag in general, but for developer it is a possibility to define what should be done before and after feature/scenario/step.

Specifiying fixtures is done this way:
```
  @fixture.vagrant
  Scenario: Install the agent on the fresh system
    Given Agent installation archive is extracted to guests "/tmp/agent"
    When "/tmp/agent/install.sh" is executed by root
    Then 1 SampleAgent processes are started less than in 120 seconds

```

Here **@fixture.vagrant** is a tag that enables fixture called vagrant, which starts and destroys VM environment for this scenario. Fixtures can be applied to whole feature or scenario or step, depending on what it does.

Adding other tags like @slow, @fast and so on, is also useful to control tests execution. For example you can separate regression, smoke and acceptance tests this way.

Note that Behave also provides a possibility to setup some common environment for all the scenarios in feature with [Background](http://behave.github.io/behave.example/tutorials/tutorial09.html) feature.


<a name="new_impl"></a>

## Implementing steps

When some steps are defined and have no implementation behave will raise a meaningful error to you with sample step definition. All the rest is known with documentation and guides.

### Working with context

It is not a secret that some data is shared between steps or scenarios. This is easily done via **context** positional argument of steps. But, please, put all the logic of context managing in some specific place and reuse it in different steps. Avoid hardcoding keys and constants all around the implementation - it always is a bad practice.

### Logging

Behave out of the box supports logging and stdout capturing. It is recommended to use [logging](https://docs.python.org/3/howto/logging.html) module to log data in tests. [More information about logging handling in behave](https://behave.readthedocs.io/en/latest/tutorial.html#works-in-progress)

### Fixtures implementation

All the environment setup and fixtures definition is done in `features/environment.py` file. Please see it to find examples of features or refer to [Behave by example](http://behave.github.io/behave.example)
