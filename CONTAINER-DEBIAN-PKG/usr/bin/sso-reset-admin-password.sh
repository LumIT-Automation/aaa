#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <admin_password>"
    echo "Script to reset the admin password of the sso service."
    exit 1
else
    adminPwd="$1"
fi

podman exec sso bash -c "cd /var/www/aaa; \
mv /var/lib/aaa-venv/bin/manage.py .; \
source /var/lib/aaa-venv/bin/activate; \
echo \"from django.contrib.auth.models import User; usr = User.objects.get(username='admin@automation.local'); usr.set_password('$adminPwd'); usr.save()\" | python manage.py shell; \
deactivate; \
mv manage.py /var/lib/aaa-venv/bin;"

exit 0
