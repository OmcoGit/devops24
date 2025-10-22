# Examination 15 - Metrics (VG)

[Prometheus](https://prometheus.io/) is a powerful application used for event monitoring and alerting.

[Node Exporter](https://prometheus.io/docs/guides/node-exporter/) collects metrics for Prometheus from
the hardware and the kernel on a machine (virtual or not).

Start by running the Prometheus server and a Node Exporter in containers on your Ansible controller
(the you're running Ansible playbooks from). This can be accomplished with the [prometheus.yml](prometheus.yml)
playbook.

You may need to install [podman](https://podman.io/docs/installation) first.

If everything worked correctly, you should see the data exported from Node Exporter on http://localhost:9090/,
and you can browse this page in a web browser.

# QUESTION A

Make an Ansible playbook, `15-node_exporter.yml` that installs [Node Exporter](https://prometheus.io/download/#node_exporter)
on each of the VMs to export/expose metrics to Prometheus.

Node exporter should be running as a `systemd` service on each of the virtual machines, and
start automatically at boot.

You can find `systemd` unit files that you can use [here](https://github.com/prometheus/node_exporter/tree/master/examples/systemd), along with the requirements regarding users and permissions.

Consider the requirements carefully, and use Ansible modules to create the user, directories, copy files,
etc.

Also, consider the firewall configuration we implemented earlier, and make sure we can talk to the node
exporter port.

HINT: To get the `firewalld` service names available in `firewalld`, you can use

    $ firewall-cmd --get-services

on the `firewalld`-enabled hosts.

Note also that while running the `podman` containers on your host, you may sometimes need to stop and
start them.

    $ podman pod stop prometheus

and

    $ podman pod start prometheus

will get you on the right track, for instance if you've changed any of the Prometheus configuration.

# Resources and Information

* https://github.com/prometheus/node_exporter/tree/master/examples/systemd
* https://prometheus.io/docs/guides/node-exporter/

### ANSWER:
Before installing Node Exporter on the VMs, I started by running Prometheus and a Node Exporter container on my Ansible controller. Podman was installed first if it wasn’t already:
```bash
sudo apt install podman
```
I configured Prometheus scrape targets for the local Node Exporter container and the VMs:
```yaml
- targets:
    - 'node-exporter:9100'      # Node Exporter container on the controller
    - '192.168.121.206:9100'    # Webserver VM
    - '192.168.121.217:9100'    # DBserver VM
```
Running the playbook:
```bash
ansible-playbook prometheus.yml
```
Accessing http://localhost:9090/ showed that Prometheus was running correctly.

The local scrape target (controller) returned “Up”, but the VM targets were down because Node Exporter had not yet been installed on them.

Next, I focused on installing Node Exporter on each of the virtual machines. This step ensures that Prometheus can scrape hardware and kernel metrics from the VMs, allowing full monitoring of the infrastructure.

The goal was to create 15-node_exporter.yml, which installs Node Exporter 1.9.1 on each VM and configures it as a systemd service.

The playbook performs the following tasks:

***Create System User and Group:***
```yaml
- name: Ensure node_exporter group exists
  ansible.builtin.group:
    name: node_exporter
    system: true

- name: Ensure node_exporter user exists
  ansible.builtin.user:
    name: node_exporter
    group: node_exporter
    shell: /sbin/nologin
    system: true
    create_home: false
```
Explanation:
A dedicated system user node_exporter is created to run the service securely. Interactive login is disabled using /sbin/nologin.

***Download and Extract Node Exporter:***
```yaml
- name: Download Node Exporter archive to temporary folder
  ansible.builtin.get_url:
    url: "https://github.com/prometheus/node_exporter/releases/download/v{{ node_exporter_version }}/node_exporter-{{ node_exporter_version }}.linux-amd64.tar.gz"
    dest: /tmp/node_exporter.tar.gz
    mode: "0644"

- name: Extract Node Exporter binary
  ansible.builtin.unarchive:
    src: /tmp/node_exporter.tar.gz
    dest: /tmp/
    remote_src: true
```
Explanation:
The official Node Exporter tarball is downloaded and extracted on the VM.

***Copy Binary to /usr/sbin:***
```yaml
- name: Copy Node Exporter binary to /usr/sbin
  ansible.builtin.copy:
    src: "/tmp/node_exporter-{{ node_exporter_version }}.linux-amd64/node_exporter"
    dest: /usr/sbin/node_exporter
    owner: node_exporter
    group: node_exporter
    mode: "0755"
    remote_src: true
```
Explanation:
The binary is copied to /usr/sbin with proper ownership and permissions.

***Prepare Directories and Unit Files:***
```yaml
- name: Create textfile collector directory
  ansible.builtin.file:
    path: /var/lib/node_exporter/textfile_collector
    state: directory
    owner: node_exporter
    group: node_exporter
    mode: '0755'

- name: Copy Node Exporter systemd service and socket files
  ansible.builtin.copy:
    src: "files/{{ item }}"
    dest: /etc/systemd/system/
    mode: "0644"
  loop:
    - node_exporter.service
    - node_exporter.socket
  notify: Reload systemd

- name: Copy sysconfig file
  ansible.builtin.copy:
    src: files/sysconfig.node_exporter
    dest: /etc/sysconfig/node_exporter
    mode: "0644"
```
Explanation:

The textfile collector directory is used for custom metrics.

Systemd unit files define service and socket behavior.

Sysconfig allows configuring startup flags.

***Start Socket-Activated Service:***
```yaml
- name: Start and enable Node Exporter socket
  ansible.builtin.systemd:
    name: node_exporter.socket
    enabled: true
    state: started
```
Explanation:
Node Exporter uses socket activation. Starting the socket ensures the service runs on demand.

***Configure Firewall:***
```yaml
- name: Enable Node Exporter service in firewalld
  ansible.posix.firewalld:
    service: prometheus-node-exporter
    permanent: true
    state: enabled
    immediate: true
```
Explanation:
TCP port 9100 is opened so Prometheus can scrape metrics from the VMs.

***Verify Node Exporter:***
```yaml
- name: Wait for Node Exporter to start
  ansible.builtin.wait_for:
    port: 9100
    timeout: 30

- name: Verify Node Exporter is reachable
  ansible.builtin.uri:
    url: "http://{{ ansible_host }}:9100/metrics"
    status_code: 200
  register: result

- name: Show verification result
  ansible.builtin.debug:
    msg: "Node Exporter responded successfully on port 9100"
```
Explanation:
Ensures Node Exporter is active and accessible before Prometheus can scrape metrics.

***Reload systemd:***
```yaml
handlers:
  - name: Reload systemd
    ansible.builtin.systemd:
      daemon_reload: true
```
Explanation:
Reloads systemd whenever the service or socket unit files are updated.

Results

Node Exporter 1.9.1 is running on both VMs.

 The Node Exporter socket is active and enabled.

 The firewall allows Prometheus to connect on port 9100.

Prometheus now shows all scrape targets (“controller,” “webserver,” “dbserver”) as Up.

Key Takeaways

Starting with local container testing helped identify the correct scrape configuration.


 Using systemd, proper ownership, and firewall rules ensures the solution is production-ready.
