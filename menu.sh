#!/bin/bash
clear

BASE_URL="https://iptv.samproject.tech"
admin_password="sam1122"

register_reseller() {
    local username=$1
    local balance=$2

    echo "Registering reseller $username with balance $balance..."
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"username\":\"$username\",\"balance\":$balance,\"password\":\"$admin_password\"}" $BASE_URL/api/register_reseller)
    echo $response | jq
    read -n 1 -s -r -p "Press any key to back on menu"
}

add_user() {
    local username=$1
    local reseller_username=$2
    local reseller_password=$3
    local package=$4

    echo "Adding user $username with package $package..."
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"username\":\"$username\",\"reseller_username\":\"$reseller_username\",\"reseller_password\":\"$reseller_password\",\"package\":\"$package\"}" $BASE_URL/api/add_user)
    echo $response | jq
    read -n 1 -s -r -p "Press any key to back on menu"
}

shorten_url() {
    local long_url=$1

    echo "Shortening URL: $long_url"
    response=$(curl -s -X POST -H "Content-Type: application/json" -d "{\"url\":\"$long_url\"}" $BASE_URL/shorten)
    echo $response | jq
    read -n 1 -s -r -p "Press any key to back on menu"
}

check_multilogin() {
    local user_uuid=$1

    echo "Checking multilogin for user with UUID: $user_uuid"
    response=$(curl -s "$BASE_URL/api/check_multilogin?user_uuid=$user_uuid")
    echo $response | jq
    read -n 1 -s -r -p "Press any key to back on menu"
}

# Display menu
main_menu() {
    echo -e "\nChoose an option:"
    echo "1. Register Reseller"
    echo "2. Add User"
    echo "3. Shorten URL"
    echo "4. Check Multilogin"
    echo "5. Exit"

    read -p "Enter your choice: " choice

    case $choice in
    1)
        read -p "Enter reseller username: " reseller_username
        read -p "Enter reseller balance: " balance
        clear
        register_reseller "$reseller_username" "$balance"
        ;;
    2)
        read -p "Enter username: " username
        read -p "Enter reseller username: " reseller_username
        read -p "Enter reseller password: " reseller_password
        read -p "Enter package: " package
        clear
        add_user "$username" "$reseller_username" "$reseller_password" "$package"
        ;;
    3)
        read -p "Enter long URL: " long_url
        clear
        shorten_url "$long_url"
        ;;
    4)
        read -p "Enter user UUID: " user_uuid
        clear
        check_multilogin "$user_uuid"
        ;;
    5)
        echo "Exiting..."
        clear
        exit 0
        ;;
    *)
        clear
        echo "Invalid choice. Please enter a number between 1 and 5."
        ;;
    esac
}


main_menu