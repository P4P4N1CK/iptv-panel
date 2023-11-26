#!/bin/bash

domain=$(sed -n '1p' /root/iptv-panel/domain.txt)
API_BASE_URL="https://${domain}"
admin_password=$(grep -o 'admin_pass = "[^"]*' "/root/iptv-panel/data.txt" | grep -o '[^"]*$' | sed -n '1p')

function register_reseller() {
    read -p "Enter reseller username: " reseller_username
    read -p "Enter reseller balance: " reseller_balance

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/register_reseller" \
        --header 'Content-Type: application/json' \
        --data '{
            "password": "'"$admin_password"'",
            "balance": '"$reseller_balance"',
            "username": "'"$reseller_username"'"
        }')

    echo "$response"
}

function add_user() {
    read -p "Enter username: " username
    read -p "Enter reseller username: " reseller_username
    read -p "Enter reseller password: " reseller_password
    read -p "Enter package: " package

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/add_user" \
        --header 'Content-Type: application/json' \
        --data '{
            "username": "'"$username"'",
            "reseller_username": "'"$reseller_username"'",
            "reseller_password": "'"$reseller_password"'",
            "package": "'"$package"'",
            "admin_password": "'"$admin_password"'"
        }')

    echo "$response"
}

function add_balance() {
    read -p "Enter user UUID to add balance: " user_uuid
    read -p "Enter amount to add: " amount

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/add_balance" \
        --header 'Content-Type: application/json' \
        --data '{
            "user_uuid": "'"$user_uuid"'",
            "amount": '"$amount"',
            "admin_password": "'"$admin_password"'"
        }')

    echo "$response"
}

function renew_user() {
    read -p "Enter user UUID to renew: " user_uuid

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/renew_user" \
        --header 'Content-Type: application/json' \
        --data '{
            "user_uuid": "'"$user_uuid"'",
            "admin_password": "'"$admin_password"'"
        }')

    echo "$response"
}

function add_balance() {
    read -p "Enter user UUID to add balance: " user_uuid
    read -p "Enter amount to add: " amount

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/add_balance" \
        --header 'Content-Type: application/json' \
        --data '{
            "user_uuid": "'"$user_uuid"'",
            "amount": '"$amount"',
            "admin_password": "'"$admin_password"'"
        }')

    echo "$response"
}


function delete_user() {
    read -p "Enter username: " username
    read -p "Enter user UUID: " user_uuid

    response=$(curl -s --request POST \
        --url "$API_BASE_URL/api/delete_user" \
        --header 'Content-Type: application/json' \
        --data '{
            "username": "'"$username"'",
            "uuid": "'"$user_uuid"'",
            "admin_password": "'"$admin_password"'"
        }')

    echo "$response"
}

function get_user_data() {
    read -p "Enter user UUID: " user_uuid

    response=$(curl -s "$API_BASE_URL/api/get_user_data?user_uuid=$user_uuid&password_input=$admin_password")

    echo "$response"
}

function get_users_by_reseller() {
    read -p "Enter reseller username: " reseller_username

    response=$(curl -s "$API_BASE_URL/api/get_users_by_reseller?reseller_username=$reseller_username&password_input=$admin_password")

    echo "$response"
}

function check_multilogin() {
    read -p "Enter user UUID: " user_uuid

    response=$(curl -s "$API_BASE_URL/api/check_multilogin?user_uuid=$user_uuid&password_input=$admin_password")

    echo "$response"
}

function restart_api() {
    run.sh
}

while true; do
    clear
    echo "========= API Interaction Script ========="
    echo "1. Register Reseller"
    echo "2. Add User"
    echo "3. Delete User"
    echo "4. Get User Data"
    echo "5. Get Users by Reseller"
    echo "6. Check Multilogin"
    echo "7. Renew User"
    echo "8. Add Balance"
    echo "9. Restart Services"
    echo "10. Exit"
    echo "=========================================="
    read -p "Select an option (1-10): " choice

    case $choice in
    1)
        register_reseller
        ;;
    2)
        add_user
        ;;
    3)
        delete_user
        ;;
    4)
        get_user_data
        ;;
    5)
        get_users_by_reseller
        ;;
    6)
        check_multilogin
        ;;
    7)
        renew_user
        ;;
    8)
        add_balance
        ;;
    9)
        restart_api
        ;;
    10)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Please enter a number between 1 and 10."
        ;;
    esac

    read -p "Press enter to continue..."
done
