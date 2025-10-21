# Examination 12 - Roles

So far we have been using separate playbooks and ran them whenever we wanted to make
a specific change.

With Ansible [roles](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_reuse_roles.html) we
have the capability to organize tasks into sets, which are called roles.

These roles can then be used in a single playbook to perform the right tasks on each host.

Consider a playbook that looks like this:

    ---
    - name: Configure the web server(s) according to specs
      hosts: web
      roles:
        - webserver

    - name: Configure the database server(s) according to specs
      hosts: db
      roles:
        - dbserver

This playbook has two _plays_, each play utilizing a _role_.

This playbook is also included in this directory as [site.yml](site.yml).

Study the Ansible documentation about roles, and then start work on [QUESTION A](#question-a).

# QUESTION A

Considering the playbook above, create a role structure in your Ansible working directory
that implements the previous examinations as two separate roles; one for `webserver`
and one for `dbserver`.

Copy the `site.yml` playbook to be called `12-roles.yml`.

HINT: You can use

    $ ansible-galaxy role init [name]

to create a skeleton for a role. You won't need ALL the directories created by this,
but it gives you a starting point to fill out in case you don't want to start from scratch.

***Answer:*** I created three Ansible roles to implement previous examinations:

**base role** – installs common software on all hosts (vim, bash-completion, qemu-guest-agent).

**web role** – installs and configures Nginx, sets up HTTPS, deploys templates, creates the web root, uploads index.html, and manages users (alovelace, aturing, edijkstra, ghopper) with correct groups, GECOS, and hashed passwords.

***Example: roles/web/tasks/main.yml — code and explanation***
```yaml
---
# roles/web/tasks/main.yml
# Entry point for the web role: import modular task files in logical order
- import_tasks: webserver.yml        # install & start nginx
- import_tasks: install-cert.yml     # create cert dirs, generate key & self-signed cert
- import_tasks: 10-web-template.yml  # copy https.conf, deploy virtualhost template, reload if changed
- import_tasks: 11-users.yml         # create users, groups, GECOS and hashed passwords
```

**db role** – installs and starts MariaDB, creates the webappdb database and webappuser, installs PyMySQL, and copies all *.md files to the deploy user’s home directory.

***Example:***
```yaml
---
# DB: install database, create schema/users, copy deploy files
- import_tasks: 09-mariadb-password.yml   # install mariadb, create DB, user (uses db_password)
- import_tasks: 11-copy-md-files.yml     # copy *.md files from roles/db/files -> /home/deploy/
```

I organized each role with its own tasks, files, templates, and vars directories to make them self-contained and reusable. Task files from previous playbooks were moved into the tasks directories, while configuration files and .md files were placed in files, and Jinja2 templates in templates. Variables, including user credentials and passwords, were stored in vars (with sensitive ones encrypted using Ansible Vault).


When converting previous playbooks into role tasks, I removed top-level directives like hosts, tasks, and become: from the .yml files. This was necessary because these task files are imported by main.yml within the roles, and the execution context (hosts and privilege escalation) is controlled by the top-level playbook (12-roles.yml). This ensures idempotency and maintainability, allowing the top-level playbook to orchestrate all roles on the correct hosts with proper privilege escalation.

Finally, the top-level playbook references the roles and their respective vars files, enabling a single execution to configure web and database servers with all previous examination tasks integrated. This approach keeps the playbooks modular, easy to maintain, and secure.

***Corresponding top-level playbook (12-roles.yml)***
```yaml
---
- name: Configure all hosts with base software
  hosts: all
  become: true
  roles:
    - base

- name: Configure the web server(s)
  hosts: web
  become: true
  vars_files:
    - roles/web/vars/users.yml
  roles:
    - web

- name: Configure the database server(s)
  hosts: db
  become: true
  vars_files:
    - roles/db/vars/secrets.yml
  roles:
    - db
```

Why the top-level playbook looks like this

Hosts and privileges are declared here: the playbook decides where each role runs and whether become is used — roles remain agnostic to those decisions.

Vars are injected centrally: vars_files loads role-specific variables (and vault files) for the appropriate play, so sensitive data is controlled at execution time and not hard-coded inside roles.

Orchestration point: this single playbook allows you to configure multiple role types (base, web, db) in a single run, keeping orchestration simple and readable.

