#!/usr/bin/env bash


if [[ -z "$1" ]]
then
	echo "Password required"
	exit 1
fi

PASSWORD="$1"

USERNAME='giovanni'
if [[ -n "$2" ]]
then
	USERNAME="$2"
fi


adduser --gecos "" --disabled-password "$USERNAME" 
echo "$USERNAME:$PASSWORD" | chpasswd

OTHER_HOME=$(eval echo "~$USERNAME")
cp -rv ~/.ssh "$OTHER_HOME/"
chown -R $USERNAME:$USERNAME "$OTHER_HOME/.ssh"

adduser giovanni sudo
