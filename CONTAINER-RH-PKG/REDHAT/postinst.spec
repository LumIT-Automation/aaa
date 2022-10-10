%post
#!/bin/bash

printf "\n* Container postinst...\n" | tee -a /dev/tty

printf "\n* Building podman image...\n" | tee -a /dev/tty
cd /usr/lib/sso

# Build container image.
buildah bud -t sso . | tee -a /dev/tty

printf "\n* The container will start in few seconds.\n\n"

printf '\n* The default admin password is \"password\"'
printf '\n* To change it use: /usr/bin/sso-reset-admin-password.sh\n'
printf '\n* To enable radius authentication edit: /var/lib/containers/storage/volumes/sso/_data/aaa/identityProvider/radius_conf.py'
printf '\n* To enable ldap AD authentication edit: /var/lib/containers/storage/volumes/sso/_data/aaa/identityProvider/ad_conf.py\n\n'

function containerSetup()
{
    wallBanner="RPM automation-interface-sso-container post-install configuration message:\n"
    cd /usr/lib/sso

    # Grab the host timezone.
    timeZone=$(timedatectl show| awk -F'=' '/Timezone/ {print $2}')

    # First container run: associate name, bind ports, bind fs volume, define init process, ...
    # sso folder will be bound to /var/lib/containers/storage/volumes/.
    podman run --name sso -v sso:/var/www/aaa/aaa -v sso-db:/var/lib/mysql -v sso-cacerts:/usr/local/share/ca-certificates -dt localhost/sso /lib/systemd/systemd
    podman exec sso chown -R www-data:www-data /var/www/aaa/aaa

    podman exec sso chown -R mysql:mysql /var/lib/mysql # within container.
    podman exec sso systemctl restart mysql

    podman exec sso find /usr/local/share/ca-certificates -type f -exec chown 0:0 {} \;
    podman exec sso find /usr/local/share/ca-certificates -type f -exec chmod 644 {} \;
    podman exec sso update-ca-certificates

    printf "$wallBanner Starting Container Service on HOST..." | wall -n # (upon installation, container is already run).
    systemctl daemon-reload

    systemctl start automation-interface-sso-container
    systemctl enable automation-interface-sso-container

    printf "$wallBanner Configuring container..." | wall -n
    # Setup a Django secret key (per-installation): using host-bound folders.
    djangoSecretKey=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)
    sed -i "s|^SECRET_KEY =.*|SECRET_KEY = \"$djangoSecretKey\"|g" /var/lib/containers/storage/volumes/sso/_data/settings.py

    printf "$wallBanner Set the timezone of the container to be the same as the host timezone..." | wall -n
    podman exec sso bash -c "timedatectl set-timezone $timeZone"

    # Configure only if not already configured.
    if ! grep -Eq 'BEGIN RSA PRIVATE KEY' /var/lib/containers/storage/volumes/sso/_data/settings_jwt.py; then # container's file.
        # Setup the JWT token keypair (per-installation).
        # Generate the TLS key and replace in settings_jwt.py.
        podman exec sso jwtkey-generate.sh
        podman exec sso chown www-data:www-data /var/www/aaa/aaa/settings_jwt.py
        podman exec sso chmod 400 /var/www/aaa/aaa/settings_jwt.py
    fi

    printf "$wallBanner Internal database configuration..." | wall -n
    if podman exec sso mysql -e "exit"; then
        # User sso.
        # Upon podman image creation, a password is generated for the user sso.
        databaseUserPassword=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

        if [ "$(podman exec sso mysql --vertical -e "SELECT User FROM mysql.user WHERE User = 'sso';" | tail -1 | awk '{print $2}')" == "" ]; then
            # User sso not present: create.
            echo "Creating sso user..."
            podman exec sso mysql -e "CREATE USER 'sso'@'localhost' IDENTIFIED BY '$databaseUserPassword';"
            podman exec sso mysql -e "GRANT USAGE ON *.* TO 'sso'@'localhost' REQUIRE NONE WITH MAX_QUERIES_PER_HOUR 0 MAX_CONNECTIONS_PER_HOUR 0 MAX_UPDATES_PER_HOUR 0 MAX_USER_CONNECTIONS 0;"
            podman exec sso mysql -e 'GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX, ALTER, CREATE TEMPORARY TABLES, CREATE VIEW, SHOW VIEW, EXECUTE ON `sso`.* TO `sso`@`localhost`;'
        else
            # Update user's password.
            echo "Updating sso user's password..."
            podman exec sso mysql -e "SET PASSWORD FOR 'sso'@'localhost' = PASSWORD('$databaseUserPassword');"
        fi

        # Change database password into Django config file, too.
        echo "Configuring Django..."
        sed -i "s/^.*DATABASE_USER$/        'USER': 'sso', #DATABASE_USER/g" /var/lib/containers/storage/volumes/sso/_data/settings.py
        sed -i "s/^.*DATABASE_PASSWORD$/        'PASSWORD': '$databaseUserPassword', #DATABASE_PASSWORD/g" /var/lib/containers/storage/volumes/sso/_data/settings.py

        # Database sso.
        echo "Creating database sso and restoring SQL dump..."
        if [ "$(podman exec sso mysql --vertical -e "SHOW DATABASES LIKE 'sso';" | tail -1 | awk -F': ' '{print $2}')" == "" ]; then
            podman exec sso mysql -e 'CREATE DATABASE sso DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;' # create database.
            podman exec sso mysql sso -e "source /var/www/aaa/sso/sql/sso.sql" # restore database dump.

            # Default admin user.
            adminPwd='password'
            podman exec sso bash -c "cd /var/www/aaa; \
                source /var/lib/aaa-venv/bin/activate; \
                echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin@automation.local', 'admin@automation.local', '$RET')\" | python manage.py shell; \
                deactivate"
        fi

        # Configure only if not already configured.
        if ! cat /var/lib/containers/storage/volumes/sso/_data/settings_workflow.py | awk -F'=' '/WORKFLOW_SECRET/ {print $2}' | sed 's/[ "]//g' | grep -Eq '[[:alnum:]]'; then
            workflowSecretKey=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)
            echo "WORKFLOW_SECRET = \"$workflowSecretKey\"" > /var/lib/containers/storage/volumes/sso/_data/settings_workflow.py # in order to be shared.
            podman exec sso chown www-data:www-data /var/www/aaa/aaa/settings_workflow.py
            podman exec sso chmod 400 /var/www/aaa/aaa/settings_workflow.py

            podman exec sso bash -c "cd /var/www/aaa; \
                source /var/lib/aaa-venv/bin/activate; \
                echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('workflow@automation.local', 'workflow@automation.local', '$workflowSecretKey')\" | python manage.py shell; \
                    deactivate"
        fi

        # Database update via diff.sql (migrations).
        echo "Applying migrations..."
        podman exec sso bash /var/www/aaa/sso/sql/migrate.sh
    else
        echo "Failed to access MariaDB RDBMS, auth_socket plugin must be enabled for the database root user. Quitting."
        exit 1
    fi

    printf "$wallBanner Restarting container's services..." | wall -n
    podman exec sso systemctl restart apache2
    podman exec sso systemctl restart mariadb

    diffOutput=$(podman exec sso diff /var/www/aaa_default_settings.py /var/www/aaa/aaa/settings.py | grep '^[<>].*' | grep -v SECRET | grep -v PASSWORD | grep -v VENV || true)
    if [ -n "$diffOutput" ]; then
        printf "$wallBanner Differences from package's stock config file and the installed one (please import NEW directives in your installed config file, if any):\n* $diffOutput" | wall -n
    else
        radiusHelp="To enable radius authentication edit: /var/lib/containers/storage/volumes/sso/_data/aaa/identityProvider/radius_conf.py\n"
        adHelp="To enable ldap AD authentication edit: /var/lib/containers/storage/volumes/sso/_data/aaa/identityProvider/ad_conf.py\n"
        adScript="Helper script To configure the Active Directory authentication: ad_conf_generator.sh."

        printf "$wallBanner $radiusHelp $adHelp $adScript" | wall -n
   fi

    # syslog-ng seems going into a catatonic state while updating a package: restarting the whole thing.
    if rpm -qa | grep -q automation-interface-log; then
        if systemctl list-unit-files | grep -q syslog-ng.service; then
            systemctl restart syslog-ng || true # on host.
            podman exec sso systemctl restart syslog-ng # on this container.
        fi
    fi

    printf "$wallBanner Installation completed." | wall -n
}

systemctl start atd

{ declare -f; cat << EOM; } | at now
containerSetup
EOM

exit 0

