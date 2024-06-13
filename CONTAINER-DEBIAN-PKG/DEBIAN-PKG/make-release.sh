#!/bin/bash

set -e

function System()
{
    base=$FUNCNAME
    this=$1

    # Declare methods.
    for method in $(compgen -A function)
    do
        export ${method/#$base\_/$this\_}="${method} ${this}"
    done

    # Properties list.
    ACTION="$ACTION"
}

# ##################################################################################################################################################
# Public
# ##################################################################################################################################################

#
# Void System_run().
#
function System_run()
{
    if [ "$ACTION" == "deb" ]; then
        if System_checkEnvironment; then
            System_definitions
            System_cleanup

            System_systemFilesSetup
            System_debianFilesSetup

            System_codeCollect
            System_codeConfig
            System_codeFilesPermissions
            System_venv
            System_fixDebVersion
            System_swaggerFile

            System_debCreate
            System_cleanup

            echo "Created /tmp/$projectName.deb"
        else
            echo "A Debian Bookworm operating system is required for the deb-ification. Aborting."
            exit 1
        fi
    else
        exit 1
    fi
}

# ##################################################################################################################################################
# Private static
# ##################################################################################################################################################

function System_checkEnvironment()
{
    if [ -f /etc/os-release ]; then
        if ! grep -q 'Debian GNU/Linux 12 (bookworm)' /etc/os-release; then
            return 1
        fi
    else
        return 1
    fi

    return 0
}


function System_definitions()
{
    declare -g debPackageRelease
    declare -g currentGitCommit

    declare -g projectName
    declare -g workingFolder
    declare -g workingFolderPath

    if [ -f DEBIAN-PKG/deb.release ]; then
        # Get program version from the release file.
        debPackageRelease=$(echo $(cat DEBIAN-PKG/deb.release))
    else
        echo "Error: deb.release missing."
        echo "Usage: bash DEBIAN-PKG/make-release.sh --action deb"
        exit 1
    fi

    git config --global --add safe.directory $(cd .. && pwd)
    currentGitCommit=$(git log --pretty=oneline | head -1 | awk '{print $1}')

    projectName="automation-interface-sso_${debPackageRelease}_amd64"
    workingFolder="/tmp"
    workingFolderPath="${workingFolder}/${projectName}"
}


function System_cleanup()
{
    if [ -n "$workingFolderPath" ]; then
        if [ -d "$workingFolderPath" ]; then
            rm -fR "$workingFolderPath"
        fi
    fi

    # Create a new working folder.
    mkdir $workingFolderPath
}


function System_codeCollect()
{
    mkdir -p $workingFolderPath/var/www/aaa
    mkdir -p $workingFolderPath/var/lib/aaa-venv

    # Copy files.
    cp -R ../aaa $workingFolderPath/var/www/aaa
    cp -R ../sso $workingFolderPath/var/www/aaa
    cp ../manage.py $workingFolderPath/var/www/aaa
    cp ../license.txt $workingFolderPath/var/www/aaa

    # Remove __pycache__ folders and not-required ones.
    rm -fR $(find $workingFolderPath/var/www/aaa -name __pycache__)
}


function System_codeConfig()
{
    sed -i "s/^DEBUG =.*/DEBUG = False/g" $workingFolderPath/var/www/aaa/aaa/settings.py

    # The following settings are emptied here and filled-in by postinst/s (debconf).
    sed -i "s/^SECRET_KEY =.*/SECRET_KEY = \"1234567890\"/g" $workingFolderPath/var/www/aaa/aaa/settings.py
    sed -i "s/^ALLOWED_HOSTS =.*/ALLOWED_HOSTS = ['*']/g" $workingFolderPath/var/www/aaa/aaa/settings.py

    sed -i -e ':a;N;$!ba;s|"publicKey.*,|"publicKey": '\'\'\'\'\'\','|g' $workingFolderPath/var/www/aaa/aaa/settings_jwt.py
    sed -i -e ':a;N;$!ba;s|"privateKey.*}|"privateKey": '\'\'\'\'\'\''\n}|g' $workingFolderPath/var/www/aaa/aaa/settings_jwt.py

    sed -i "s/^WORKFLOW_SECRET =.*/WORKFLOW_SECRET = \"\"/g" $workingFolderPath/var/www/aaa/aaa/settings_workflow.py

    sed -i "s/^RADIUS_SERVER =.*/RADIUS_SERVER = \"\"/g" $workingFolderPath/var/www/aaa/aaa/identityProvider/radius_conf.py
    sed -i "s/^RADIUS_PORT =.*/RADIUS_PORT = 0/g" $workingFolderPath/var/www/aaa/aaa/identityProvider/radius_conf.py
    sed -i "s/^RADIUS_SECRET =.*/RADIUS_SECRET = \"\"/g" $workingFolderPath/var/www/aaa/aaa/identityProvider/radius_conf.py

    sed -i "s/^AUTH_LDAP_SERVER_URI =.*/AUTH_LDAP_SERVER_URI = \"\"/g" $workingFolderPath/var/www/aaa/aaa/identityProvider/ldap_conf.py

    sed -i "s/^SUPERADMIN_IDENTITY_AD_GROUPS =.*/SUPERADMIN_IDENTITY_AD_GROUPS = []/g" $workingFolderPath/var/www/aaa/aaa/settings.py

    # Also, copy the settings.py file into another location in order to keep the default config saved.
    cp -f $workingFolderPath/var/www/aaa/aaa/settings.py $workingFolderPath/var/www/aaa_default_settings.py
}


function System_codeFilesPermissions()
{
    # Forcing standard permissions (755 for folders, 644 for files, owned by www-data:www-data).
    chown -R www-data:www-data $workingFolderPath/var/www/aaa
    find $workingFolderPath/var/www/aaa -type d -exec chmod 750 {} \;
    find $workingFolderPath/var/www/aaa -type f -exec chmod 640 {} \;

    # Particular permissions.
    #resources=( "$projectName/var/www/aaa" )
    #for res in "${resources[@]}"; do
    #    find $res -type d -exec chmod 750 {} \;
    #    find $res -type f -exec chmod 640 {} \;
    #done
}


function System_venv()
{
    # Put all pip dependencies in a virtual env.
    # All dependencies will be then included in the .deb package; Apache virtual host is set up accordingly.
    cp ../aaa/pip.requirements $workingFolderPath/var/lib/aaa-venv

    # Start virtual environment for the collection of the dependencies.
    cd $workingFolderPath
    python3 -m venv var/lib/aaa-venv
    source var/lib/aaa-venv/bin/activate

    # Install pip dependencies in the virtual environment.
    python -m pip install --upgrade pip
    python -m pip install -r var/lib/aaa-venv/pip.requirements
    python -m pip freeze > /tmp/pip.freeze.venv

    # Exit from the virtual env.
    deactivate
    cd -

    rm $workingFolderPath/var/lib/aaa-venv/pip.requirements

    # Removing cached information within the venv (--> cleanup the venv).
    rm -R $(find $workingFolderPath/var/lib/aaa-venv/ -name __pycache__)
    sed -i "s|$workingFolderPath||g" $(grep -iR $workingFolderPath $workingFolderPath/var/lib/aaa-venv/ | awk -F: '{print $1}')
}


function System_fixDebVersion()
{
    debVer=`echo $debPackageRelease | awk -F'-' '{print $1'}`
    if [ -r ../aaa/pip.lock ]; then
        SameVer="y"
        for pyPack in $(cat /tmp/pip.freeze.venv | awk -F'==' '{print $1}'); do
            # Get version from new freeze file.
            nVer=$(cat /tmp/pip.freeze.venv | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            # Get version from old freeze file.
            if grep -Eq "^$pyPack==" ../aaa/pip.lock; then
                oVer=$(cat ../aaa/pip.lock | grep -E "^$pyPack==" | awk -F'==' '{print $2}')
            else
                oVer='missing'
            fi

            if [ "$nVer" != "$oVer" ]; then
                SameVer="n"
                echo -e "Package \e[92m${pyPack}\e[0m have a different version than before: Old: $oVer, New: $nVer"
            fi
        done

        if [ "$SameVer" != "y" ]; then
            echo " - Overwriting pip.lock file..."
            cp /tmp/pip.freeze.venv ../aaa/pip.lock
            echo "Some python package version is changed, please adjust debian version file."
        else
            echo "Versions of the python packages are not changed."
        fi
    else
        echo " - File pip.lock was not present."
        cp /tmp/pip.freeze.venv ../aaa/pip.lock
    fi
}


function System_systemFilesSetup()
{
    # Setting up system files.
    cp -R DEBIAN-PKG/etc $workingFolderPath
    cp -R DEBIAN-PKG/usr $workingFolderPath

    find $workingFolderPath -type d -exec chmod 755 {} \;
    find $workingFolderPath -type f -exec chmod 644 {} \;

    chmod +x $workingFolderPath/usr/bin/consul.sh
    chmod +x $workingFolderPath/usr/bin/jwtkey-generate.sh
    chmod +x $workingFolderPath/usr/bin/syslogng-target.sh
}


function System_debianFilesSetup()
{
    # Setting up all the files needed to build the package (DEBIAN folder).
    cp -R DEBIAN-PKG/DEBIAN $workingFolderPath

    sed -i "s/^Version:.*/Version:\ $debPackageRelease/g" $workingFolderPath/DEBIAN/control
    sed -i "s/GITCOMMIT/$currentGitCommit/g" $workingFolderPath/DEBIAN/control

    chmod +x $workingFolderPath/DEBIAN/postinst
    chmod +x $workingFolderPath/DEBIAN/preinst
}



function System_swaggerFile() {
    mkdir $workingFolderPath/var/www/aaa/doc
    cp /var/www/aaa/doc/postman.json $workingFolderPath/var/www/aaa/doc/
    postman2openapi -f yaml /var/www/aaa/doc/postman.json > $workingFolderPath/var/www/aaa/doc/swagger.yaml
}



function System_debCreate()
{
    cd $workingFolder
    dpkg-deb --build $projectName
}

# ##################################################################################################################################################
# Main
# ##################################################################################################################################################

ACTION=""

# Must be run as root.
ID=$(id -u)
if [ $ID -ne 0 ]; then
    echo "This script needs super cow powers."
    exit 1
fi

# Parse user input.
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --action)
            ACTION="$2"
            shift
            shift
            ;;

        *)
            shift
            ;;
    esac
done

if [ -z "$ACTION" ]; then
    echo "Missing parameters. Use --action deb."
else
    System "system"
    $system_run
fi

exit 0
