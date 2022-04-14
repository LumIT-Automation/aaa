#!/bin/bash

read -rsp "Enter a new password for admin@automation.local: " passwd1
echo
read -rsp "Confirm the new password for admin@automation.local: " passwd2
echo

if [ "$passwd1" != "$passwd2" ]; then
    echo -e "\tEntered passwords differ."
    echo -e "\tPassword not changed"
    exit 1
fi


podman exec sso bash -c "cd /var/www/aaa; \
mv /var/lib/aaa-venv/bin/manage.py .; \
source /var/lib/aaa-venv/bin/activate; \
echo \"from django.contrib.auth.models import User; usr = User.objects.get(username='admin@automation.local'); usr.set_password('$passwd1'); usr.save()\" | python manage.py shell; \
deactivate; \
mv manage.py /var/lib/aaa-venv/bin;"

if [ $? -eq 0 ]; then
    echo "Password changed"
fi

exit 0

