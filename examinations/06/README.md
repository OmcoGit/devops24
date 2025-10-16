# Examination 6 - Handling Web Server Content

The default web pages for any web server are not very interesting to look at.

If we open a web browser and point it towards the address of our web server,
you will likely get the default content of an unconfigured and unmanaged
web server:

Open Firefox or Chrome and enter the IP address of the web server, either
with http:// or http://

You should se a super snazzy web page from Alma Linux telling the visitor
that the administrator of this server needs to get their act together.

Also note that if you use https:// for secure HTTP, you will get a warning
telling you that you should be very careful accepting non-validating
certificates (such as the one we created earlier). This is normal, and
since we were the ones creating the certificate, we can just add an
exception for accepted certs, or simply use the http:// URL.

We will create a _virtual host_ on our web server, that serves different
content depending on which address it is called by via web browsers.

## Configure the nginx virtual host

The virtual host we will create will be called "example.internal", so that when we
go to http://example.ínternal or https://example.internal, our own web page
will be displayed instead. Obviously, this is a fake address, so we need
to do some black magic on our own machines first.

We will edit the file `/etc/hosts` on our host machine (i.e. the computer
you are working on).

Add the following line to this file, WITHOUT removing any of the other stuff
in this file:

    192.168.121.10  example.internal

Note that you need to be `root` to be able to edit this file, and that the address
given above is just an example. The actual IP of your `webserver` machine is
what we are interested in.

See if you now can resolve the name `example.internal`:

    $ ping -c 1 example.internal
    PING example.internal (192.168.121.10) 56(84) bytes of data.
    64 bytes from example.internal (192.168.121.10): icmp_seq=1 ttl=64 time=0.446 ms
    
    --- example.internal ping statistics ---
    1 packets transmitted, 1 received, 0% packet loss, time 0ms
    rtt min/avg/max/mdev = 0.446/0.446/0.446/0.000 ms

Again, the actual IP address it resolves to may be different on your machine.

If you have come this far, we can now move on to the next step.

## Upload our web page to the virtual host directory

Let's make a web page and upload to the web server so we can display our
own content instead.

Make a web page that looks something like this:

```xml
<?xml version="1.0"?>
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Hello Nackademin!</title>
  </head>
  <body>
    <h1>Hello Nackademin!</h1>
    <p>This is a totally awesome web page</p>
    <p>This page has been uploaded with <a href="https://www.ansible.com">Ansible</a>!</p>
  </body>
</html>
```
Note that this web page follows the HTML standards from W3C, in case you are
interested in why it looks the ways it does: https://html.spec.whatwg.org/multipage/

There is a copy of this file in the [files/index.html](files/index.html) directory adjacent to where
you are reading this file. Make sure this file exists in the directory `files/` in your
Ansible working directory too by copying it.

We will create the directory from where the web server will serve the pages under `example.internal`
in `/var/www/example.internal/html`.

Before we do that, we need to configure `nginx` to find the web pages in the new directory.

In the [files/](files/) directory, there is an `nginx` configuration file for `example.internal` called
[files/example.internal.conf](files/example.internal.conf). Copy this file into `files/` in your Ansible
working directory.

Before we do anything else, we will use Ansible to copy this file to `/etc/nginx/conf.d/example.internal.conf`
and then restart the web server.

Begin by copying the `05-web.yml` playbook to `06-web.yml`.

Add a task to the `06-web.yml` playbook BEFORE the web server is restarted that looks like this:

    - name: Ensure the nginx configuration is updated for example.internal
      ansible.builtin.copy:
        src: files/example.internal.conf
        dest: /etc/nginx/conf.d/example.internal.conf

You may now rerun the example playbook and see what happens.

# QUESTION A

In the `06-web.yml` playbook, add a couple of tasks:

* One task to create the directory structure under `/var/www/example.internal/html/`.
* One task to upload our `files/index.html` file to `/var/www/example.internal/html/index.html`.

HINTS:
* The module for creating a directory is, somewhat counterintuitively, called
[ansible.builtin.file](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/file_module.html)
* If you want to serve files under a non-standard directory (such as the one we create above), we must
  also set the correct SELinux security context type on the directory and files. The context in question
  in this case should be `httpd_sys_content_t` for the `/var/www/example.internal/html/` directory.


***Answer:*** 
```bash
---
- name: Configure HTTPS and virtual host for nginx
  hosts: web
  become: true
  tasks:

    - name: Copy HTTPS configuration
      ansible.builtin.copy:
        src: files/https.conf
        dest: /etc/nginx/conf.d/https.conf
        owner: root
        group: root
        mode: '0644'

    - name: Ensure the nginx configuration is updated for example.internal
      ansible.builtin.copy:
        src: files/example.internal.conf
        dest: /etc/nginx/conf.d/example.internal.conf
        owner: root
        group: root
        mode: '0644'

    - name: Create web root directory structure
      ansible.builtin.file:
        path: /var/www/example.internal/html
        state: directory
        owner: root
        group: root
        mode: '0755'

    - name: Upload index.html to web root
      ansible.builtin.copy:
        src: files/index.html
        dest: /var/www/example.internal/html/index.html
        owner: root
        group: root
        mode: '0644'

    - name: Restart nginx
      ansible.builtin.service:
        name: nginx
        state: restarted
```
The playbook first copies the HTTPS configuration to the server so that nginx can serve secure traffic. Then it copies the virtual host configuration for example.internal, setting the server name, root directory, and SSL settings.

 Next, it creates the directory structure /var/www/example.internal/html/ for the website, and uploads the index.html file into that directory. Finally, nginx is restarted to apply the new configuration.


# QUESTION B

To each of the tasks that change configuration files in the webserver, add a `register: [variable_name]`.

As an example:

    - name: Set up configuration for HTTPS
      ansible.builtin.copy:
        src: files/https.conf
        dest: /etc/nginx/conf.d/https.conf
      register: result

When the task is run, the result of the task is saved into the variable `result`, which is a dictionary.
This result can be compared in a conditional with the keyword `changed`, such as

    when: result is changed

or

    when: result.changed is true

or

    when: result["changed"] is true

or, more succinctly:

    when: result.changed

or even

    when: result["changed"]

You can check what the variable contains after each task with adding

    - name: Print the value of result
      ansible.builtin.debug:
        var: result

With the use of the `when:` keyword, make a conditional that only restarts the web server if either of
the tasks has had any change.

See https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html#basic-conditionals-with-when

There are several ways to accomplish this, and there is no _best_ way to do this with what we've done so far.

Is this a good way to handle these types of conditionals? What do you think?

***Answer:*** In the playbook, register is used to capture the result of tasks that modify configuration files, and when: result.changed is used to conditionally restart nginx only if a change occurred. This ensures that nginx is not restarted unnecessarily, saving resources and avoiding downtime.

My opinion:
I think this is a good approach for handling conditionals. It makes the playbook idempotent, meaning it can be run multiple times without causing unintended changes. It also reduces unnecessary service restarts, which is especially important in environments where uptime matters. Using register together with when allows tasks to respond dynamically to changes, which makes the automation more intelligent and efficient.

Overall, I would continue using this method because it balances safety, efficiency, and clarity in the playbook.

# BONUS QUESTION

Imagine you had a playbook with hundreds of tasks to be done on several hosts, and each one of these tasks
might require a restart or reload of a service.

Let's say the goal is to avoid restarts as much as possible to minimize downtime and interruptions; how
would you like the flow to work?

Describe in simple terms what your preferred task flow would look like, not necessarily implemented in
Ansible, but in general terms.


***Answer:*** The best way to handle a playbook with hundreds of tasks that might require service restarts is to separate configuration changes from restarts. Here’s how I would structure it, including what Ansible functionality I’d use:

Apply all configuration changes first

Use modules like copy, template, or file to update configuration files and directories.

This stage only changes configurations — no restarts yet.

Track which tasks actually made changes

Use the register keyword to save the result of each task.

Each result can be checked with .changed to see if a change really happened.

Restart or reload services only when needed

Use the when condition with the service module so that restarts only happen if something actually changed.

This avoids unnecessary downtime.

Restart services in small groups instead of all at once

In multi-host environments, use serial in Ansible to restart only a few hosts at a time.

This way, some servers keep running while others restart, which helps prevent downtime.

Verify that services are running after changes

Use modules like systemd or command to check service status or test configurations after restart.

This ensures that everything is working properly.

**Summary:** This approach separates configuration changes from restarts, checks whether updates really happened, and restarts only when needed — and in small batches if multiple servers are involved.