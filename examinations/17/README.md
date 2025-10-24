# Examination 17 - sudo rules

In real life, passwordless sudo rules is a security concern. Most of the time, we want
to protect the switching of user identity through a password.

# QUESTION A

Create an Ansible role or playbook to remove the passwordless `sudo` rule for the `deploy`
user on your machines, but create a `sudo` rule to still be able to use `sudo` for everything,
but be required to enter a password.

On each virtual machine, the `deploy` user got its passwordless `sudo` rule from the Vagrant
bootstrap script, which placed it in `/etc/sudoers.d/deploy`.

Your solution should be able to have `deploy` connect to the host, make the change, and afterwards
be able to `sudo`, only this time with a password.

To be clear; we want to make sure that at no point should the `deploy` user be completely without
the ability to use `sudo`, since then we're pretty much locked out of our machines (save for using
Vagrant to connect to he machine and fix the problem).

*Tip*: Check out _validate_ in [ansible.builtin.lineinfile](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html) to ensure a file can be parsed correctly (such as running `visudo --check`)
before being changed.

No password is set for the `deploy` user, so begin by setting the password to `hunter12`.

HINT: To construct a password hash (such as one for use in [ansible.builtin.user](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html), you can use the following command:

    $ openssl passwd -6 hunter12

This will give you a SHA512 password hash that you can use in the `password:` field.

You can verify this by trying to login to any of the nodes without the SSH key, but using the password
provided instead.

To be able to use the password when running the playbooks later, you must use the `--ask-become-pass`
option to `ansible` and `ansible-playbook` to provide the password. You can also place the password
in a file, like with `ansible-vault`, or have it encrypted via `ansible-vault`.

***Answer:***
Steps Taken:

Set a password for the deploy user:

Created a SHA512 hash of the password oms using openssl passwd -6 oms.

Updated the deploy user password via the Ansible module ansible.builtin.user.

Verified login with the new password.

Update sudoers file:

The original /etc/sudoers.d/deploy contained:
```sql
%deploy ALL=(ALL) NOPASSWD:ALL
```
Using Ansible’s lineinfile module, the file was updated with:
```yaml
regexp: '^%?deploy'
line: 'deploy ALL=(ALL) ALL'
validate: 'visudo -cf %s'
```
This replaced any passwordless sudo rules for both the deploy user and %deploy group, enforcing a password requirement.

File permissions were maintained correctly (0440).

Verification:

Logged in as deploy on the virtual machines.

Tested sudo commands with:
```bash
sudo -k
sudo whoami
```
Confirmed that sudo now requires the password and functions correctly.

###### Outcome:

Passwordless sudo rules were successfully removed for both the user and the group.

The deploy user retains full sudo privileges but must now authenticate with a password.

The solution is idempotent; the playbook can be run multiple times without further changes.

###### Notes: 
Always validate /etc/sudoers.d changes using visudo to avoid locking out users.

The regex ^%?deploy ensures that both user and group NOPASSWD entries are handled.

Using ansible.builtin.user with password_hash allows secure automated password management.