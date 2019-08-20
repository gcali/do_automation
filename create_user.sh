#!/usr/bin/env bash

set -e
set -o nounset

if [[ $# < 3 ]]; then
    >&2 echo "Not enough arguments"
    exit 1;
fi

connection_string=$1
user_name=$2
password=$3

if [[ $user_name != "$user_name" ]]; then
    >&2 echo "Wrong user name"
    exit 2;
fi

ssh "$connection_string" 'bash -se' <<HERE

adduser --disabled-password --gecos "" $user_name
echo "$user_name:$password" | chpasswd
adduser $user_name sudo

cp -rv ~/.ssh ~$user_name/

chown -R $user_name:$user_name ~$user_name/.ssh
HERE
