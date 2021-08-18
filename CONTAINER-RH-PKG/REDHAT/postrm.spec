%postun
#!/bin/bash

printf "\n* Container postrm...\n"

# $1 is the number of time that this package is present on the system. If this script is run from an upgrade and not
if [ "$1" -eq "0" ]; then
    if podman volume ls | awk '{print $2}' | grep -q ^sso$; then
        printf "\n* Clean up sso volumes ...\n"
        podman volume rm -f sso
        podman volume rm -f sso-db
    fi
fi

exit 0
