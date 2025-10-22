# Examination 16 - Security Compliance Check

The ever-present IT security team were not content with just having us put firewall rules
on our servers. They also want our servers to pass CIS certifications.

# QUESTION A

Implement _at least_ 10 of the checks in the [CIS Security Benchmark](https://www.cisecurity.org/benchmark/almalinuxos_linux) for AlmaLinux 10 and run them on the virtual machines.

These checks should be run by a playbook called `16-compliance-check.yml`.

*Important*: The playbook should only _check_ or _assert_ the compliance status, not perform any changes.

Use Ansible facts, modules, and "safe" commands. Here is an example:

    ---
    - name: Security Compliance Checks
      hosts: all
      tasks:
        - name: check for telnet-server
          ansible.builtin.command:
            cmd: rpm -q telnet-server
            warn: false
          register: result
          changed_when: result.stdout != "package telnet-server is not installed"
          failed_when: result.changed

Again, the playbook should make *no changes* to the servers, only report.

Often, there are more elegant and practical ways to assert compliance. The example above is
taken more or less verbatim from the CIS Security Benchmark suite, but it is often considered
bad practice to run arbitrary commands through [ansible.builtin.command] or [ansible.builtin.shell]
if you can avoid it.

In this case, you _can_ avoid it, by using the [ansible.builtin.package_facts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_facts_module.html).

In conjunction with the [ansible.builtin.assert](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/assert_module.html) module you have a toolset to accomplish the same thing, only more efficiently and in an Ansible-best-practice way.

For instance:

    ---
    - name: Security Compliance Checks
      hosts: all
      tasks:
        - name: Gather the package facts
          ansible.builtin.package_facts:

        - name: check for telnet-server
          ansible.builtin.assert:
            fail_msg: telnet-server package is installed
            success_msg: telnet-server package is not installed
            that: "'telnet-server' not in ansible_facts.packages"

It is up to you to implement the solution you feel works best. 

***Answer:*** 
**Implementation**: I created an Ansible playbook 16-compliance-check.yml that performs 10 CIS Security Benchmark checks for AlmaLinux 10. The playbook uses modules like package_facts, assert, stat, service_facts, and slurp to gather facts and assert compliance. No changes are made to the servers; all checks only report compliance status.
Ensure telnet-server is not installed.

I included ignore_errors: yes for each task because some servers may not currently meet the CIS requirements (e.g., SSH root login is enabled, firewalld is not running). This ensures the playbook continues to run all checks and reports the compliance status for every item, instead of stopping at the first failure. This approach allows a complete overview of the system's CIS compliance.




Ensure telnet-server is not installed.

Ensure rsh-server is not installed.

Ensure ypserv is not installed.

Ensure SSH root login is disabled.

Ensure /tmp directory permissions are 1777.

Ensure firewalld service is running.

Ensure rsyslog service is running.

Ensure /var/log/sudo.log exists.

Ensure systemd-journald service is running.

Ensure any additional necessary CIS services or packages (as applicable).

***Results***
The playbook was run on the virtual machines and reported which checks passed and which did not:

Packages like telnet, rsh, and ypserv were not installed → compliant.

SSH root login is still allowed → not compliant.

/tmp permissions were correct → compliant. etc.

# BONUS QUESTION

If you implement these tasks within one or more roles, you will gain enlightenment and additional karma.


***Answer:***
For the bonus part, I implemented the CIS compliance checks as an Ansible role called compliance. All 10 tasks were moved into the role’s tasks/main.yml file, and optional variables (e.g., package and service names) were defined in vars/main.yml. This structure allows the playbook to remain minimal while the role encapsulates all the compliance logic.

By using a role:

The tasks are modular and reusable across different servers.

It is easier to maintain and extend with additional checks in the future.

The playbook becomes cleaner, improving readability and organization.

The main playbook simply includes the role, which can be executed safely to check CIS compliance on any AlmaLinux 10 host.

# Resources

For inspiration and as an example of an advanced project using Ansible for this, see for instance
https://github.com/ansible-lockdown/RHEL10-CIS. Do *NOT*, however, try to run this compliance check
on your virtual (or physical) machines. It will likely have unintended consequences, and may render
your operating system and/or virtual machine unreachable.
