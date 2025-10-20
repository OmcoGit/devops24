# Examination 10 - Templating

With the installation of the web server earlier in Examination 6, we set up
the `nginx` web server with a static configuration file that listened to all
interfaces on the (virtual) machine.

What we really want is for the webserver to _only_ listen to the external
interface, i.e. the interface with the IP address that we connect to the machine to.

Of course, we can statically enter the IP address into the file and upload it,
but if the IP address of the machine changes, we have to do it again, and if the
playbook is meant to be run against many different web servers, we have to be able
to do this manually.

Make a directory called `templates/` and put the `nginx` configuration file from Examination 6
into that directory, and call it `example.internal.conf.j2`.

If you look at the `nginx` documentation, note that you don't have to enable any IPv6 interfaces
on the web server. Stick to IPv4 for now.

# QUESTION A

Copy the finished playbook from Examination 6 (`06-web.yml`) and call it `10-web-template.yml`.

Make the static configuration file we used earlier into a Jinja template file,
and set the values for the `listen` parameters to include the external IP
address of the virtual machine itself.

Use the `ansible.builtin.template` module to accomplish this task.

***Answer:*** For Question A, I copied the playbook from Examination 6 (06-web.yml) and saved it as 10-web-template.yml.
I converted the static Nginx configuration file (example.internal.conf) into a Jinja2 template (example.internal.conf.j2) and replaced the static listen directives with the variable {{ ansible_default_ipv4.address }}.

The playbook now uses the ansible.builtin.template module to dynamically deploy the configuration file, ensuring that Nginx always listens on the external IP address of the host where the playbook is executed.
All other tasks from the previous playbook — such as creating the web root directory, uploading the index.html, configuring HTTPS, and applying SELinux contexts — were retained.

This makes the configuration portable and adaptable across different servers without requiring manual IP changes.

*Complete playbook (10-web-template.yml):*
```bash
---
- name: Configure HTTPS and virtual host for nginx with SELinux
  hosts: web
  become: true
  tasks:

    # Copy HTTPS configuration
    - name: Copy HTTPS configuration
      ansible.builtin.copy:
        src: files/https.conf
        dest: /etc/nginx/conf.d/https.conf
        owner: root
        group: root
        mode: '0644'
      register: https_result

    # Deploy example.internal.conf from template
    - name: Deploy nginx configuration from template
      ansible.builtin.template:
        src: templates/example.internal.conf.j2
        dest: /etc/nginx/conf.d/example.internal.conf
        owner: root
        group: root
        mode: '0644'
      register: example_result

    # Reload nginx if configuration changed
    - name: Reload nginx if configuration changed
      ansible.builtin.service:
        name: nginx
        state: reloaded
      when: example_result.changed

    # Create web root directory
    - name: Create web root directory structure
      ansible.builtin.file:
        path: /var/www/example.internal/html
        state: directory
        owner: root
        group: root
        mode: '0755'
      register: webroot_result

    # Upload index.html
    - name: Upload index.html to web root
      ansible.builtin.copy:
        src: files/index.html
        dest: /var/www/example.internal/html/index.html
        owner: root
        group: root
      register: index_result

    # Apply SELinux context
    - name: Apply correct SELinux context recursively
      ansible.builtin.command:
        cmd: restorecon -Rv /var/www/example.internal/html
      when: webroot_result.changed or index_result.changed
```

# Resources and Documentation

* https://docs.ansible.com/ansible/latest/collections/ansible/builtin/template_module.html
* https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_variables.html
* https://nginx.org/en/docs/http/ngx_http_core_module.html#listen
