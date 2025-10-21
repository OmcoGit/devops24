# Examination 13 - Handlers

In [Examination 5](../05/) we asked the question what the disadvantage is of restarting
a service every time a task is run, whether or not it's actually needed.

In order to minimize the amount of restarts and to enable a complex configuration to run
through all its steps before reloading or restarting anything, we can trigger a _handler_
to be run once when there is a notification of change.

Read up on [Ansible handlers](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_handlers.html)

In the previous examination ([Examination 12](../12/)), we changed the structure of the project to two separate
roles, `webserver` and `dbserver`.

# QUESTION A

Make the necessary changes to the `webserver` role, so that `nginx` only reloads when it's configuration
has changed in a task, such as when we have changed a `server` stanza.

Also note the difference between `restarted` and `reloaded` in the [ansible.builtin.service](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/service_module.html) module.

In order for `nginx` to pick up any configuration changes, it's enough to do a `reload` instead of
a full `restart`.

***Answer:***
I modified the webserver role to use Ansible handlers for reloading nginx. Instead of restarting nginx every time a task runs, I created a handler that reloads the service only when a configuration file changes.

Steps I followed:

Created a handler

File: roles/webserver/handlers/main.yml

Content:
```yaml
---
- name: reload nginx
  ansible.builtin.service:
    name: nginx
    state: reloaded
```
This defines a handler named reload nginx which reloads the service without stopping it, preventing unnecessary downtime.

Modified the nginx configuration task

Instead of reloading nginx directly, the task now notifies the handler if the configuration changes:
```yaml
- name: Deploy nginx configuration
  ansible.builtin.template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
  notify:
    - reload nginx
```
his ensures the handler is triggered only if the file actually changes.

Kept other tasks separate

Tasks for creating the web root and uploading index.html remain in 10-web-template.yml.

These tasks do not notify the handler, because changes in HTML files or directories do not require nginx to reload.

**Result:**

When the playbook runs, nginx reloads only when the configuration template changes.

If no changes are detected in the configuration, nginx is left running without any reload.

Multiple configuration changes in one run will trigger the handler only once, improving efficiency.

**Conclusion**:
Using a handler ensures that nginx is only reloaded when needed, minimizing unnecessary service interruptions and optimizing the playbook execution.
