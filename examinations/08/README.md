# Examination 8 - MariaDB configuration

MariaDB and MySQL have the same origin (MariaDB is a fork of MySQL, because of... Oracle...
it's a long story.) They both work the same way, which makes it possible to use Ansible
collections that handle `mysql` to work with `mariadb`.

To be able to manage MariaDB/MySQL through the `community.mysql` collection, you also
need to make sure the requirements for the collections are installed on the database VM.

See https://docs.ansible.com/ansible/latest/collections/community/mysql/mysql_db_module.html#ansible-collections-community-mysql-mysql-db-module-requirements

HINT: In AlmaLinux, the correct package to install on the VM host is called `python3-PyMySQL`.

# QUESTION A

Copy the playbook from examination 7 to `08-mariadb-config.yml`.

Use the `community.mysql` module in this playbook so that it also creates a database instance
called `webappdb` and a database user called `webappuser`.

Make the `webappuser` have the password "secretpassword" to access the database.

HINT: The `community.mysql` collection modules has many different ways to authenticate
users to the MariaDB/MySQL instance. Since we've just installed `mariadb` without setting
any root password, or securing the server in other ways, we can use the UNIX socket
to authenticate as root:

* The socket is located in `/var/lib/mysql/mysql.sock`
* Since we're authenticating through a socket, we should ignore the requirement for a `~/.my.cnf` file.
* For simplicity's sake, let's grant `ALL` privileges on `webapp.*` to `webappuser`

***Answer:***
```yaml
---
- hosts: db
  become: true
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
        password: secretpassword
        priv: 'webappdb.*:ALL'
        state: present
        login_unix_socket: /var/lib/mysql/mysql.sock
```
*Explanation*:
I copied the playbook from Examination 7 to 08-mariadb-config.yml and extended it to configure MariaDB for our web application.
The playbook ensures that MariaDB is installed, enabled, and running, and also installs python3-PyMySQL so that Ansible can communicate with the database.

It then creates a database named webappdb and a user webappuser with the password secretpassword.
All privileges are granted to webappuser on the webappdb database.

I use login_unix_socket: /var/lib/mysql/mysql.sock so Ansible can connect to MariaDB as root without a password. The socket is a special file that allows local programs, like PyMySQL, to communicate directly with the database using the operating system’s user credentials.


# Documentation and Examples
https://docs.ansible.com/ansible/latest/collections/community/mysql/index.html
