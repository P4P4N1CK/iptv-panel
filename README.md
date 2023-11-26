---

# IPTV Service API Documentation

Welcome to the IPTV Service API documentation. This API allows users to manage their IPTV accounts, reseller accounts, and provides various utility functions.

## Table of Contents

1. [Introduction](#1-introduction)
2. [Authentication](#2-authentication)
3. [Endpoints](#3-endpoints)
    - [1. `GET /api/get_user_data`](#1-get-api-get_user_data)
    - [2. `POST /shorten`](#2-post-shorten)
    - [3. `GET /{short_id}`](#3-get-short_id)
    - [4. `POST /api/register_reseller`](#4-post-api-register_reseller)
    - [5. `POST /api/add_user`](#5-post-api-add_user)
    - [6. `GET /iptv`](#6-get-iptv)
    - [7. `POST /api/delete_user`](#7-post-api-delete_user)
    - [8. `GET /api/get_users_by_reseller`](#8-get-api-get_users_by_reseller)
    - [9. `GET /api/check_multilogin`](#9-get-api-check_multilogin)
    - [10. `GET /api/check_all_multilogin`](#10-get-api-check_all_multilogin)
4. [Error Handling](#error-handling)
5. [Examples](#examples)
6. [FAQs](#faqs)

## 1. Introduction

The IPTV Service API provides a range of functionalities for managing user accounts, resellers, and utility operations. To use this API, you will need to authenticate using the appropriate credentials.

## 2. Authentication

Authentication is required for certain endpoints. The primary means of authentication is using the `admin_password` parameter in the request. Ensure that you include this parameter in the request header for the relevant endpoints.

## 3. Endpoints

### 1. `GET /api/get_user_data`

#### Description

Get user data based on the provided `user_uuid` and `password_input`. This endpoint requires authentication using the `admin_password`.

#### Parameters

- `user_uuid` (string, required): User UUID.
- `password_input` (string, required): Admin password for authentication.

#### Response

Returns user data or an error message.

### 2. `POST /shorten`

#### Description

Shorten a given URL.

#### Request Body

- `url` (string, required): The URL to be shortened.

#### Response

Returns the shortened URL.

### 3. `GET /{short_id}`

#### Description

Redirects to the original URL corresponding to the given short ID.

### 4. `POST /api/register_reseller`

#### Description

Register a new reseller.

#### Request Body

- `username` (string, required): Reseller username.
- `balance` (float, required): Reseller balance.
- `password` (string, required): Admin password for authentication.

#### Response

Returns reseller credentials or an error message.

...

## 4. Error Handling

Errors are communicated through standard HTTP status codes and JSON responses. Check the error message in the response body for details on the issue.

Example:

```json
{
    "error": "Invalid admin password",
    "code": 401
}
```

## 5. Examples

Below are some example use cases for the API:

1. **Get User Data**
   ```bash
   curl -X GET "https://your-api-host/api/get_user_data?user_uuid=example_uuid&password_input=admin_password"
   ```

2. **Shorten URL**
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"url": "https://example.com"}' "https://your-api-host/shorten"
   ```

...

## 6. FAQs

### Q: How can I reset my password?
A: Passwords can be change in data.txt.

### Q: Can I register multiple users with a single request?
A: No, the API currently supports registering one user at a time.

---
