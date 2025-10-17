# Examination 9 - Use Ansible Vault for sensitive information

In the previous examination we set a password for the `webappuser`. To keep this password
in plain text in a playbook, or otherwise, is a huge security hole, especially
if we publish it to a public place like GitHub.

There is a way to keep sensitive information encrypted and unlocked at runtime with the
`ansible-vault` tool that comes with Ansible.

https://docs.ansible.com/ansible/latest/vault_guide/index.html

*IMPORTANT*: Keep a copy of the password for _unlocking_ the vault in plain text, so that
I can run the playbook without having to ask you for the password.

# QUESTION A

Make a copy of the playbook from the previous examination, call it `09-mariadb-password.yml`
and modify it so that the task that sets the password is injected via an Ansible variable,
instead of as a plain text string in the playbook.

***Answer:*** For Question A, I copied the previous playbook from Examination 8 and introduced a variable called db_password instead of hardcoding the password directly in the playbook.
The password for the database user webappuser is now referenced using {{ db_password }} in the playbook, while the actual value is stored in a separate file secrets.yml.'

This approach allows the password to be changed in a single place without modifying the playbook itself, improving flexibility and preparing the setup for secure encryption in Question B.

```bash
# 09-mariadb-password.yml for Question A
---
- hosts: db
  become: true
  vars_files:
    - secrets.yml
  tasks:
    - name: Ensure MariaDB-server is installed
      ansible.builtin.package:
        name: mariadb-server
        state: present

    - name: Ensure mariadb is enabled and started
      ansible.builtin.service:
        name: mariadb
        enabled: true
        state: started

    - name: Ensure PyMySQL is installed for Ansible MySQL modules
      ansible.builtin.package:
        name: python3-PyMySQL
        state: present

    - name: Create a database named webappdb
      community.mysql.mysql_db:
        name: webappdb
        state: present
        login_unix_socket: /var/lib/mysql/mysql.sock

    - name: Create a database user for the web application
      community.mysql.mysql_user:
        name: webappuser
        password: "{{ db_password }}"
        priv: 'webappdb.*:ALL'
        state: present
        login_unix_socket: /var/lib/mysql/mysql.sock
```
How to run: Make sure secrets.yml exists with db_password: "your_password". Then run:
ansible-playbook 09-mariadb-password.yml

# QUESTION B

When the [QUESTION A](#question-a) is solved, use `ansible-vault` to store the password in encrypted
form, and make it possible to run the playbook as before, but with the password as an
Ansible Vault secret instead.

***Answer:*** For Question B, I encrypted the secrets.yml file using Ansible Vault with the command: 
```bash
ansible-vault encrypt secrets.yml
```
The playbook remains the same and still reads the password using vars_files. When running the playbook, the Vault password must be provided with:
```bash
ansible-playbook 09-mariadb-password.yml --ask-vault-pass
```

Files:
secrets.yml – Contains the db_password variable in plain text for Question A.

vault.yml – (Encrypted) version of secrets.yml for Question B using Ansible Vault.