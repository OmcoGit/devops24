#!/usr/bin/python
# Shebang-rad: anger att Python ska användas för att köra filen

from ansible.module_utils.basic import AnsibleModule
# Importerar AnsibleModule, som hanterar argument, fel och resultat i Ansible-moduler

def main():
    # Huvudfunktionen för modulen

    # Skapa AnsibleModule-objektet och definiera vilka argument modulen tar
    module = AnsibleModule(
        argument_spec=dict(
            message=dict(type='str', required=True)  # 'message' är en obligatorisk sträng
        )
    )

    # Hämta användarens meddelande
    msg = module.params['message']

    # Vänd strängen baklänges
    reversed_msg = msg[::-1]

    # Skapa resultat-dictionary som vi skickar tillbaka till Ansible
    result = {
        'original_message': msg,        # Originalmeddelandet
        'reversed_message': reversed_msg, # Meddelandet baklänges
        'changed': msg != reversed_msg   # True om strängen ändrades (inte ett palindrom)
    }

    # Hantera fail-fallet
    if msg == "fail me":
        # Om användaren skickar "fail me" → misslyckas modulen
        # **result packas upp till argument så att Ansible får hela resultatet
        module.fail_json(msg="You requested this to fail", **result)

    # Skicka resultatet tillbaka till Ansible
    module.exit_json(**result)

# Kör main() om filen körs direkt
if __name__ == '__main__':
    main()
