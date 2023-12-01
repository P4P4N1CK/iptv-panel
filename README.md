# IPTV Service API Documentation

Welcome to the IPTV Service API documentation. This API allows users to manage their IPTV accounts, reseller accounts, and provides various utility functions.

## Installation

To set up the IPTV Service API, you can use the provided installation script. Open a terminal and run the following command:

```
bash <(curl -s https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/setup.sh)
```

## Update
```
bash <(curl -s https://raw.githubusercontent.com/syfqsamvpn/iptv-panel/main/update.sh)
```

## Table of Contents

1. [Introduction](#1-introduction)
2. [Authentication](#2-authentication)
3. [Endpoints](#3-endpoints)
    - [1. `GET /api/get_user_data`](#1-get-apiget_user_data)
    - [2. `POST /shorten`](#2-post-shorten)
    - [3. `GET /{short_id}`](#3-get-short_id)
    - [4. `POST /api/register_reseller`](#4-post-api-register_reseller)
    - [5. `POST /api/add_user`](#5-post-api-add_user)
    - [6. `GET /iptv`](#6-get-iptv)
    - [7. `POST /api/delete_user`](#7-post-apidelete_user)
    - [8. `GET /api/get_users_by_reseller`](#8-get-apiget_users_by_reseller)
    - [9. `GET /api/check_multilogin`](#9-get-apicheck_multilogin)
    - [10. `GET /api/check_all_multilogin`](#10-get-apicheck_all_multilogin)
    - [11. `POST /api/renew_user`](#11-post-apirenew_user)
    - [12. `POST /api/add_reseller_balance`](#12-post-apiadd_reseller_balance)
    - [13. `POST /api/add_user_custom`](#13-post-apiadd_user_custom)
    - [14. `GET /api/get_all_resellers`](#14-get-apiget_all_resellers)
4. [Error Handling](#4-error-handling)
5. [Examples](#5-examples)
6. [FAQs](#6-faqs)

## 1. Introduction

The IPTV Service API provides a range of functionalities for managing user accounts, resellers, and utility operations. To use this API, you will need to authenticate using the appropriate credentials.

## 2. Authentication

Authentication is required for certain endpoints. The primary means of authentication is using the `admin_password` parameter in the request. Ensure that you include this parameter in the request header for the relevant endpoints.

## 3. Endpoints

### 1. `GET /api/get_user_data`

**Description**

Get user data based on the provided `user_uuid` and `password_input`. This endpoint requires authentication using the `admin_password`.

**Parameters**

- `user_uuid` (string, required): User UUID.
- `password_input` (string, required): Admin password for authentication.

**Response**

Returns user data or an error message.

### 2. `POST /shorten`

**Description**

Shorten a given URL.

**Request Body**

- `url` (string, required): The URL to be shortened.

**Response**

Returns the shortened URL.

### 3. `GET /{short_id}`

**Description**

Redirects to the original URL corresponding to the given short ID.

### 4. `POST /api/register_reseller`

**Description**

Register a new reseller with the provided information.

**Request Body**

- `password` (string, required): Admin password for authentication.
- `balance` (number, required): Initial balance for the reseller.
- `username` (string, required): Reseller's desired username.

**Response**

Returns reseller information, including the generated link and initial balance.

### 5. `POST /api/add_user`

**Description**

Register a new IPTV user.

**Request Body**

- `username` (string, required): User's desired username.
- `reseller_username` (string, required): Reseller's username for authentication.
- `reseller_password` (string, required): Reseller's password for authentication.
- `package` (string, required): Package name for the user.

**Response**

Returns user information, including the generated link and remaining balance.

### 6. `GET /iptv`

**Description**

Handles IPTV requests and ensures valid user authentication.

**Parameters**

- `id` (string, required): User's IPTV ID.
- `uuid` (string, required): User's UUID.

**Response**

Redirects to the appropriate content or returns an error message.

### 7. `POST /api/delete_user`

**Description**

Deletes a user based on the provided `username`, `uuid`, and `admin_password`.

**Request Body**

- `username` (string, required): User's username.
- `uuid` (string, required): User's UUID.
- `admin_password` (string, required): Admin password for authentication.

**Response**

Returns a success message or an error if the user is not found.

### 8. `GET /api/get_users_by_reseller`

**Description**

Get a list of users associated with a specific reseller.

**Parameters**

- `reseller_username` (string, required): Reseller's username.
- `password_input` (string, required): Admin password for authentication.

**Response**

Returns a list of users associated with the reseller.

### 9. `GET /api/check_multilogin`

**Description**

Check if a user has multiple logins based on the provided `user_uuid` and `password_input`.

**Parameters**

- `user_uuid` (string, required): User's UUID.
- `password_input` (string, required): Admin password for authentication.

**Response**

Returns the multilogin status for the specified user.

### 10. `GET /api/check_all_multilogin`

**Description**

Check the multilogin status for all users.

**Parameters**

- `password_input` (string, required): Admin password for authentication.

**Response**

Returns the multilogin status for all users.

### 11. `POST /api/renew_user`

**Description**

Renew a user's subscription.

**Request Body**

- `reseller_username` (string, required): Reseller username for authentication.
- `reseller_password` (string, required): Reseller password for authentication.
- `uuid` (string, required): User's UUID.
- `package` (string, required): Package name for the user.

**Response**

Returns a success message or an error if the user is not found.

### 12. `POST /api/add_reseller_balance`

**Description**

Add balance to a seller's account.

**Request Body**

- `username` (string, required): User's username.
- `amount` (number, required): Amount to add to the user's balance.
- `password` (string, required): Admin password for authentication.

**Response**

Returns the updated balance or an error if the user is not found.

### 13. `POST /api/add_user_custom`

**Description**

Custom API to add a user with specific parameters.

**Request Body**

- `admin_password` (string, required): Admin password for authentication.
- `reseller_username` (string, required): Reseller's username.
- `reseller_password`

 (string, required): Reseller's password.
- `username` (string, required): User's username.
- `days` (number, required): Number of days for the user's subscription.

**Response**

Returns user information or an error message.

### 14. `GET /api/get_all_resellers`

**Description**

Get a list of all resellers.

**Parameters**

- `password_input` (string, required): Admin password for authentication.

**Response**

Returns a list of all resellers.

### 15. `POST /api/add_secure_url`

**Description**

Add a secure URL with a short ID for redirection.

**Request Body**

- `short_id` (string, required): Short ID for the secure URL.
- `url` (string, required): The URL to be associated with the short ID.

**Response**

Returns the success message or an error if the addition fails.

### 16. `POST /api/edit_secure_url`

**Description**

Edit the URL associated with a secure short ID.

**Request Body**

- `short_id` (string, required): Short ID of the secure URL to be edited.
- `new_url` (string, required): The new URL to replace the existing one.

**Response**

Returns the success message or an error if the edit fails.

## 4. Error Handling

Errors are communicated through standard HTTP status codes and JSON responses. Check the error message in the response body for details on the issue.

Example:

```json
{
    "error": "Reseller not found",
    "code": 404
}
```

## 5. Examples

Below are additional examples for the newly documented endpoints:

1. **Add User**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username": "new_user", "reseller_username": "reseller_name", "reseller_password": "reseller_pass", "package": "basic"}' "https://your-api-host/api/add_user"
   ```

2. **Delete User**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username": "user_to_delete", "uuid": "user_uuid", "admin_password": "admin_pass"}' "https://your-api-host/api/delete_user"
   ```

3. **Renew User**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username": "user_to_renew", "uuid": "user_uuid", "admin_password": "admin_pass"}' "https://your-api-host/api/renew_user"
   ```

4. **Add Balance**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"username": "user_to_add_balance", "uuid": "user_uuid", "amount": 10, "admin_password": "admin_pass"}' "https://your-api-host/api/add_balance"
   ```

5. **Add User Custom**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"admin_password": "12345678", "reseller_username": "reseller_username", "reseller_password": "reseller_password", "username": "samvpn53g44", "days": 7}' "https://your-api-host/api/add_user_custom"
   ```

6. **Get All Resellers**
   ```bash
   curl -X GET "https://your-api-host/api/get_all_resellers?password_input=12345678"
   ```

## 6. FAQs

### Q: How can I reset my password?
A: Passwords can be changed in data.txt.

### Q: Can I register multiple users with a single request?
A: No, the API currently supports registering one user at a time.

---
