# Examination 1 - Understanding SSH and public key authentication

Connect to one of the virtual lab machines through SSH, i.e.

    $ ssh -i deploy_key -l deploy webserver

Study the `.ssh` folder in the home directory of the `deploy` user:

    $ ls -ld ~/.ssh

Look at the contents of the `~/.ssh` directory:

    $ ls -la ~/.ssh/

## QUESTION A

What are the permissions of the `~/.ssh` directory?

Why are the permissions set in such a way?

Answer: 700 (drwx------)
Only the owner (deploy) has read, write, and execute permissions.

Group members and others have no access.

This is done for security reasons: SSH private keys must be kept private, and if others could read or modify the .ssh directory, they could compromise the ability to log in securely.

## QUESTION B

What does the file `~/.ssh/authorized_keys` contain?

Answer: The file contains the public SSH key of the user or machine that is allowed to log in as deploy without a password.



## QUESTION C

When logged into one of the VMs, how can you connect to the
other VM without a password?

Answer: I generated an SSH key pair for the deploy user on the webserver and manually copied the public key to the dbserver.

On the webserver, I displayed the public key using: 
cat ~/.ssh/id_ed25519.pub
Finally, I tested the connection from the webserver:
ssh deploy@<dbserver_ip>

and logged in without entering a password — confirming that key-based authentication worked.

Later, I did the same process in the opposite direction: I generated an SSH key on the dbserver, copied its public key to the webserver’s authorized_keys, and verified that I could also connect from dbserver back to webserver without a password.

This established passwordless SSH access in both directions between the two virtual machines.

### Hints:

* man ssh-keygen(1)
* ssh-copy-id(1) or use a text editor

## BONUS QUESTION

Can you run a command on a remote host via SSH? How?

Answer: Yes, it is possible to run commands on a remote host through SSH without logging in interactively.
After setting up passwordless SSH between the webserver and dbserver, I could execute commands directly from one machine to the other.

For example, from the webserver I ran:
