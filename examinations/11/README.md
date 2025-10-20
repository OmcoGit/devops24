# Examination 11 - Loops

Imagine that on the web server(s), the IT department wants a number of users accounts set up:

    alovelace
    aturing
    edijkstra
    ghopper

These requirements are also requests:

* `alovelace` and `ghopper` should be added to the `wheel` group.
* `aturing` should be added to the `tape` group
* `edijkstra` should be added to the `tcpdump` group.
* `alovelace` should be added to the `audio` and `video` groups.
* `ghopper` should be in the `audio` group, but not in the `video` group.

Also, the IT department, for some unknown reason, wants to copy a number of '\*.md' files
to the 'deploy' user's home directory on the `db` machine(s).

I recommend you use two different playbooks for these two tasks. Prefix them both with `11-` to
make it easy to see which examination it belongs to.

# QUESTION A

Write a playbook that uses loops to add these users, and adds them to their respective groups.

When your playbook is run, one should be able to do this on the webserver:

    [deploy@webserver ~]$ groups alovelace
    alovelace : alovelace wheel video audio
    [deploy@webserver ~]$ groups aturing
    aturing : aturing tape
    [deploy@webserver ~]$ groups edijkstra
    edijkstra : edijkstra tcpdump
    [deploy@webserver ~]$ groups ghopper
    ghopper : ghopper wheel audio

There are multiple ways to accomplish this, but keep in mind _idempotency_ and _maintainability_.

***Answer:*** 
The playbook creates user accounts on the web server with the required groups, real names (GECOS field), and hashed passwords.

**Details**:

Users created: alovelace, aturing, edijkstra, ghopper.

Group assignments follow the requirements (e.g., alovelace → wheel, video, audio).

Passwords are hashed using password_hash('sha512') in the variables file (users.yml).

The no_log: true option is used to prevent passwords from appearing in the playbook output.

The playbook is idempotent; re-running it does not duplicate users or change group assignments unnecessarily.

**The Playbook:**
```yaml
---
- name: Create users and manage group membership
  hosts: web
  become: true
  vars_files:
    - vars/users.yml
  tasks:
    - name: Ensure users exist with correct groups, GECOS, and password
      ansible.builtin.user:
        name: "{{ item.name }}"
        groups: "{{ item.groups | join(',') }}"
        comment: "{{ item.comment | default(omit) }}"
        password: "{{ item.password }}"
        append: true
        state: present
      loop: "{{ users }}"
      no_log: true
```


# QUESTION B

Write a playbook that uses

    with_fileglob: 'files/*.md5'

to copy all `\*.md` files in the `files/` directory to the `deploy` user's directory on the `db` server(s).

For now you can create empty files in the `files/` directory called anything as long as the suffix is `.md`:

    $ touch files/foo.md files/bar.md files/baz.md

***Answer:*** This playbook copies all .md files from the files/ directory on the control machine to the deploy user's home directory on all servers in the db group. It ensures correct ownership and permissions, and is idempotent.

```yaml
---
- name: Copy all .md files to deploy user's home directory
  hosts: db
  become: true
  tasks:
    - name: Copy .md files to deploy's home directory
      ansible.builtin.copy:
        src: "{{ item }}"
        dest: "/home/deploy/"
        owner: deploy
        group: deploy
        mode: '0644'
      with_fileglob:
        - "files/*.md"
```
After creating the playbook, I tested it by adding content to foo.md with echo "Hello World" > files/foo.md and then re-running the playbook. On the DB server, using cat /home/deploy/foo.md confirmed that the file was copied correctly and contained the updated text.

# BONUS QUESTION

Add a password to each user added to the playbook that creates the users. Do not write passwords in plain
text in the playbook, but use the password hash, or encrypt the passwords using `ansible-vault`.

There are various utilities that can output hashed passwords, check the FAQ for some pointers.

***Answer:*** Passwords for all users (alovelace, aturing, edijkstra, ghopper) are stored in the variables file vars/users.yml.

Instead of storing passwords in plain text in the playbook, the Jinja2 function password_hash('sha512') is used directly in the variable:

```yaml
password: "{{ 'AdaSecure123!' | password_hash('sha512') }}"
```
This ensures that passwords are hashed when the playbook runs.

The task also uses no_log: true to prevent passwords from appearing in the playbook output.

The variable file is encrypted with Ansible Vault, so it can safely be stored in the GitHub repository without exposing passwords.
# BONUS BONUS QUESTION

Add the real names of the users we added earlier to the GECOS field of each account. Google is your friend.

***Answer:*** For each user, the playbook sets the GECOS field (the comment parameter) with the user’s real name, e.g.:
```yaml
comment: "Ada Lovelace"
```
This ensures that commands like getent passwd alovelace or finger alovelace will show the user’s full name, making it easier to identify the account owner.

The playbook uses:
```yaml
comment: "{{ item.comment | default(omit) }}"
```
to dynamically assign the GECOS field for each user from the vars/users.yml file.

This approach keeps the playbook idempotent and maintainable: re-running it does not overwrite other account settings unnecessarily.

**Practical Purpose:**

The GECOS field provides system administrators with a readable way to associate user accounts with real people.

Although it doesn’t affect system functionality, it improves account management, especially on servers with multiple users.

# Resources and Documentation

* [loops](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_loops.html)
* [ansible.builtin.user](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/user_module.html)
* [ansible.builtin.fileglob](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/fileglob_lookup.html)
* https://docs.ansible.com/ansible/latest/reference_appendices/faq.html#how-do-i-generate-encrypted-passwords-for-the-user-module

