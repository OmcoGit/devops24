# Examination 18 - Write an Ansible module (VG)

Ansible modules are types of plugins that execute automation tasks on a 'target'. In the previous
examinations you have used many different modules, written by Ansible developers.

A module in Ansible is a Python script that adheres to a particular convention.

You can see the places where Ansible looks for modules by dumping the Ansible configuration
and then search for `DEFAULT_MODULE_PATH`:

    $ ansible-config dump | grep -i module_path

We will now write our own module, and run it through Ansible.

# QUESTION A

Look at [Developing modules](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html)
and create a module that

* Is called `anagrammer`
* Takes one parameter, `message`, that is a string.
* Returns two values:
    - `original_message` that is the string that is passed through `message`
    - `reversed_message` that is the `message` string, only backwards (reversed).
* If the `original_message` and `reversed_message` is different, the `changed` parameter should be `True`, otherwise
  it should be `False`.

When you are done, you should be able to do

    $ ANSIBLE_LIBRARY=./library ansible -m anagrammer -a 'message="hello world"' localhost

And it should return

    localhost | CHANGED => {
        "changed": true,
        "original_message": "hello world",
        "reversed_message": "dlrow olleh"
    }

You should also be able to do

    ANSIBLE_LIBRARY=./library ansible -m anagrammer -a 'message="sirap i paris"' localhost

And it should return

    localhost | SUCCESS => {
        "changed": false,
        "original_message": "sirap i paris",
        "reversed_message": "sirap i paris"
    }

If you pass in 'fail me', it should fail like this:

    localhost | FAILED! => {
        "changed": true,
        "msg": "You requested this to fail",
        "original_message": "fail me",
        "reversed_message": "em liaf"
    }


***Answer:***
I created a custom Ansible module called anagrammer that takes a string parameter message and returns two values:

original_message – the original string passed to the module.

reversed_message – the string reversed (backwards).

The module also sets changed to:
True if the reversed string is different from the original (i.e., not a palindrome).

False if the string is a palindrome.

If the message "fail me" is passed, the module fails with a message using fail_json().

The module reverses the string using Python slicing ([::-1]), compares it to the original, and returns the result via exit_json().

Example usage:
```bash
$ ANSIBLE_LIBRARY=./library ansible -m anagrammer -a 'message="hello world"' localhost
# returns changed=True, original_message="hello world", reversed_message="dlrow olleh"

$ ANSIBLE_LIBRARY=./library ansible -m anagrammer -a 'message="sirap i paris"' localhost
# returns changed=False, original_message="sirap i paris", reversed_message="sirap i paris"

$ ANSIBLE_LIBRARY=./library ansible -m anagrammer -a 'message="fail me"' localhost
# module fails with msg="You requested this to fail"
```

# QUESTION B

Study the output of `ansible-config dump | grep -i module_path`. You will notice that there is a directory
in your home directory that Ansible looks for modules in.

Create that directory, and copy the Ansible module you just wrote there, then make a playbook
that uses this module with the correct parameters.

You don't need to worry about FQCN and namespaces in this examination.

***Answer:***
I placed the custom anagrammer module in a location where Ansible can find it and tested that it works correctly.

Steps taken:
Created the directory:
```bash
mkdir -p ~/.ansible/plugins/modules
```
Copied the custom module to the directory:
```bash
cp ~/ansible/library/anagrammer.py ~/.ansible/plugins/modules/
```
Tested the module:
```bash
ansible localhost -m anagrammer -a 'message="hello world"'
```
Output:
```json
"original_message": "hello world",
"reversed_message": "dlrow olleh",
"changed": true
```
This confirmed that Ansible could find and execute the module.

For GitHub or sharing, the module can also stay in a local library/ directory in the project, and ANSIBLE_LIBRARY=./library can be used to reference it without installing globally.

# QUESTION C

Create a playbook called `18-anagrammer.yml` that uses this module.

Make the playbook use a default variable for the message that can be overriden by using something like:

    $ ansible-playbook --verbose --extra-vars message='"This is a whole other message"' 18-custom-module.yml

***Answer:***
I created a playbook called 18-anagrammer.yml that uses the custom anagrammer module with a default variable for the message. The variable can be overridden at runtime using --extra-vars.

Playbook Contents:
```yaml
---
- name: Test custom anagrammer module
  hosts: localhost
  gather_facts: false

  vars:
    # Default message; can be overridden via --extra-vars
    message: "hello world"

  tasks:
    - name: Run anagrammer module
      anagrammer:
        message: "{{ message }}"
```
Behavior / Explanation:

Default variable:

The vars: section sets a default value for message ("hello world").

This default is used unless overridden with --extra-vars when running the playbook.

Task:

Calls the anagrammer module with the message variable.

The module reverses the string and sets changed accordingly.

###### Overriding the default variable:
```bash
ansible-playbook --verbose --extra-vars message='"This is a whole other message"' 18-anagrammer.yml
```
This replaces the default "hello world" with the custom string.

Example Output:

Using the default message:
```json
"original_message": "hello world",
"reversed_message": "dlrow olleh",
"changed": true
```

Using an overridden message:
```json
"original_message": "palindrome",
"reversed_message": "emordnilap",
"changed": true
```
The playbook demonstrates how to use a custom module with a variable.

The message variable is flexible and can be easily changed without editing the playbook.
# BONUS QUESTION

What is the relationship between the booleans you can use in Python, and the various "truthy/falsy" values
you most often use in Ansible?

What modules/filters are there in Ansible that can safely test for "truthy/falsy" values, and return something
more stringent?

***Answer:***
In Python, True and False are Boolean values.

In Ansible, many other values are interpreted as “truthy” or “falsy”:

Falsy values: "" (empty string), 0, None, [] (empty list), {} (empty dictionary)

Truthy values: any non-empty string, non-zero numbers, non-empty lists/dictionaries

Because Ansible automatically converts many values to Boolean, sometimes a value might be considered “true” even if it isn’t strictly a Python True.

Python Booleans (True/False) are strict, but Ansible uses “truthy/falsy” evaluation.

Using filters like bool, default, and modules like assert ensures more predictable behavior when checking truthiness.
