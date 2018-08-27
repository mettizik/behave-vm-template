Feature: Agent installation
Let's assume we have a product that contains an agent - service that must be installed on target system.
Since agent is installed it starts SampleAgent process. SampleAgent process is than started automatically after system
is booted.
Since this is a simple and time consuming operation we want it to be verified automatically on different environments.

  @fixture.vagrant
  Scenario: Install the agent on the fresh system
    Given Agent installation archive is extracted to guests "/tmp/agent"
    When "/tmp/agent/install.sh" is executed by root
    Then 1 SampleAgent processes are started less than in 120 seconds

    When target is rebooted
    Then 1 SampleAgent processes are started less than in 20 seconds
