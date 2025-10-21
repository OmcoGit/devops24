# Examination 14 - Firewalls (VG)

The IT security team has noticed that we do not have any firewalls enabled on the servers,
and thus ITSEC surmises that the servers are vulnerable to intruders and malware.

As a first step to appeasing them, we will install and enable `firewalld` and
enable the services needed for connecting to the web server(s) and the database server(s).

# QUESTION A

Create a playbook `14-firewall.yml` that utilizes the [ansible.posix.firewalld](https://docs.ansible.com/ansible/latest/collections/ansible/posix/firewalld_module.html) module to enable the following services in firewalld:

* On the webserver(s), `http` and `https`
* On the database servers(s), the `mysql`

You will need to install `firewalld` and `python3-firewall`, and you will need to enable
the `firewalld` service and have it running on all servers.

When the playbook is run, you should be able to do the following on each of the
servers:

## dbserver

    [deploy@dbserver ~]$ sudo cat /etc/firewalld/zones/public.xml
    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <description>For use in public areas. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.</description>
      <service name="ssh"/>
      <service name="dhcpv6-client"/>
      <service name="cockpit"/>
      <service name="mysql"/>
    <forward/>
    </zone>

## webserver

    [deploy@webserver ~]$ sudo cat /etc/firewalld/zones/public.xml
    <?xml version="1.0" encoding="utf-8"?>
    <zone>
      <short>Public</short>
      <description>For use in public areas. You do not trust the other computers on networks to not harm your computer. Only selected incoming connections are accepted.</description>
      <service name="ssh"/>
      <service name="dhcpv6-client"/>
      <service name="cockpit"/>
      <service name="https"/>
      <service name="http"/>
      <forward/>
    </zone>

# Resources and Documentation

https://firewalld.org/

***Answer:*** To complete this task, I created an Ansible playbook called 14-firewall.yml.
The playbook installs and enables firewalld and configures the necessary services for both the web and database servers.

On all servers, the playbook installs firewalld and python3-firewall, then ensures that the firewalld service is enabled and running.

On the webservers, it enables the http and https services.

On the database servers, it enables the mysql service.

After running the playbook, the firewall configuration can be verified with:
```yaml
sudo cat /etc/firewalld/zones/public.xml
```

The output confirms that:

The webserver allows http and https services.

The dbserver allows the mysql service.

This ensures that only the required services are accessible while the servers remain protected by firewalld.