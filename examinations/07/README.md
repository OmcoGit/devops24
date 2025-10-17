# Examination 7 - MariaDB installation

To make a dynamic web site, many use an SQL server to store the data for the web site.

[MariaDB](https://mariadb.org/) is an open-source relational SQL database that is good
to use for our purposes.

We can use a similar strategy as with the _nginx_ web server to install this
software onto the correct host(s). Create the playbook `07-mariadb.yml` with this content:

    ---
    - hosts: db
      become: true
      tasks:
        - name: Ensure MariaDB-server is installed.
          ansible.builtin.package:
            name: mariadb-server
            state: present

# QUESTION A

Make similar changes to this playbook that we did for the _nginx_ server, so that
the `mariadb` service starts automatically at boot, and is started when the playbook
is run.

***Answer:*** I modified the 07-mariadb.yml playbook to make sure that the MariaDB service starts automatically at boot and is running after the playbook has been executed.
Here is the final version of my playbook:
```bash
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
```
# QUESTION B

When you have run the playbook above successfully, how can you verify that the `mariadb`
service is started and is running?

***Answer:*** After running the playbook successfully, I can verify that the MariaDB service with 
```bash
sudo systemctl status mariadb
```



# BONUS QUESTION

How many different ways can use come up with to verify that the `mariadb` service is running?

***Answer:*** There are many ways to verify that the MariaDB service is running. Here are some examples:
```bash
systemctl status mariadb or systemctl is-active mariadb
```

```bash
Process check:
ps aux | grep mariadbd
```
```bash
Log check:
journalctl -u mariadb -n 20 to view recent log entries
```