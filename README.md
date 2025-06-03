# 🍋 Restaurant Manager API

🚀 **Live API URL**: [https://little-lemon-api-yexw.onrender.com/](https://little-lemon-api-yexw.onrender.com/)

This project implements a fully functional RESTful API for **Lemon**, a fictional restaurant. It enables client developers to build web and mobile applications that support various user roles with specific permissions, including menu management, order processing, delivery crew assignment, and more.

---

## Table of Contents

1.  [Features](#features)
2.  [Technologies Used](#technologies-used)
3.  [Project Structure](#project-structure)
4.  [User Roles](#user-roles)
5.  [Authentication](#authentication)
6.  [API Endpoints Overview](#api-endpoints-overview)
    * [Menu Items](#menu-items)
    * [User Group Management](#user-group-management)
    * [Cart Management](#cart-management)
    * [Order Management](#order-management)
7.  [Filtering, Sorting & Pagination](#filtering-sorting--pagination)
8.  [Throttling](#throttling)
9.  [Error Handling](#error-handling)
10. [Running the Project Locally](#running-the-project-locally)
11. [License](#license)

## 🚀 Features

- REST API for restaurant operations
- Role-based access control: Manager, Delivery Crew, Customer
- Token-based authentication using Djoser with **JWT (JSON Web Tokens)
- Menu, cart, and order management
- Group-based user administration
- Filtering, searching, sorting, and pagination
- Request throttling for both authenticated and anonymous users
- Proper error handling with descriptive HTTP status codes

---

## 📦 Technologies Used

- Python 3.x  
- Django 4.x  
- Django REST Framework  
- Djoser (for authentication with JWT)  
- Pipenv (for virtual environment and dependency management)  
- SQLite (development database)  

---

## 🗂 Project Structure

All API logic is contained within a single Django app called `LittleLemonAPI`.

```
LittleLemonAPI/
├── admin.py
├── models.py
├── permissions.py
├── serializers.py
├── urls.py
└── views.py
```

Dependencies are managed using `pipenv`.

---

## 👥 User Roles

- **Manager** – Full access to all endpoints
- **Delivery Crew** – View assigned orders and update delivery status
- **Customer** – Browse menu, manage cart, and place orders

Users without a group are considered **Customers** by default.  
Groups and user assignments are managed via the Django Admin Panel.

---


## 🔐 Authentication

Authentication is handled by Djoser and uses JSON Web Tokens (JWT) for a stateless and secure approach. The following endpoints are used:

| Endpoint | Method | Access | Description |
|---|---|---|---|
| /auth/users/ | POST | Public | Register a new user |
| /auth/users/me/ | GET | Authenticated | Retrieve current user details |
| /auth/jwt/create/ | POST | Public | Obtain JWT access and refresh tokens for login (send username and password) |
| /auth/jwt/refresh/ | POST | Public | Obtain a new access token using a valid refresh token |
| /auth/jwt/verify/ | POST | Public | Verify the validity of an access token |
| /auth/users/set_password/ | POST | Authenticated | Change user's password |
| /auth/users/reset_password/ | POST | Public | Request password reset email |
| /auth/users/reset_password_confirm/ | POST | Public | Confirm password reset using UID and token |

Using JWT Tokens:
Once you obtain an access token from /auth/jwt/create/, you must include it in the Authorization header of all subsequent protected API requests:

Authorization: Bearer <your_access_token>

When your access token expires, use the refresh token with the /auth/jwt/refresh/ endpoint to get a new access token.

---

## 📚 API Endpoints Overview

### 📋 Menu Items

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/menu-items/` | GET | All | List all menu items |
| `/api/menu-items/` | POST | Manager | Add a new menu item |
| `/api/menu-items/{id}/` | GET | All | Retrieve a menu item |
| `/api/menu-items/{id}/` | PUT/PATCH/DELETE | Manager | Update or delete a menu item |

Supports filtering, sorting, and pagination.

---

### 👥 User Group Management

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/groups/manager/users/` | GET/POST | Manager | View/add users to the manager group |
| `/api/groups/manager/users/{userId}/` | DELETE | Manager | Remove user from manager group |
| `/api/groups/delivery-crew/users/` | GET/POST | Manager | View/add users to the delivery crew |
| `/api/groups/delivery-crew/users/{userId}/` | DELETE | Manager | Remove user from delivery crew group |

---


### 🗂️ Categories

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/categories/` | GET | All | List all categories |
| `/api/categories/{id}/` | GET | All | Retrieve category details |


### 🛒 Cart Management

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/cart/`      | GET    | Customer | View all items in the authenticated user's cart      |
| `/api/cart/`      | POST   | Customer | Add item to the cart or update quantity if it exists |
| `/api/cart/<id>/` | PATCH  | Customer | Update the quantity of a specific item in the cart   |
| `/api/cart/<id>/` | DELETE | Customer | Remove a specific item from the cart                 |
| `/api/cart/`      | DELETE | Customer | Clear all items from the cart                        |


---


### 📦 Order Management

| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/orders/` | GET | Customer | List user’s orders |
| `/api/orders/create/` | POST | Customer | Create a new order from cart |
| `/api/orders/{id}/` | GET | Customer | View a specific order |
| `/api/orders/{id}/assign-delivery-crew/` | POST | Manager | Assign delivery crew to the order |
| `/api/orders/{id}/` | PUT/PATCH | Manager | Update or manage order |
| `/api/orders/{id}/` | DELETE | Manager | Delete an order |
| `/api/orders/` | GET | Manager | View all orders |
| `/api/orders/` | GET | Delivery Crew | View assigned orders |
| `/api/orders/{id}/` | PATCH | Delivery Crew | Update order delivery status |


| Endpoint | Method | Role | Description |
|----------|--------|------|-------------|
| `/api/orders/` | GET | Customer | List user’s orders |
| `/api/orders/` | POST | Customer | Create a new order from cart |
| `/api/orders/{id}/` | GET | Customer | View a specific order |
| `/api/orders/` | GET | Manager | View all orders |
| `/api/orders/{id}/` | PUT/PATCH | Manager | Assign delivery crew and update status |
| `/api/orders/{id}/` | DELETE | Manager | Delete an order |
| `/api/orders/` | GET | Delivery Crew | View assigned orders |
| `/api/orders/{id}/` | PATCH | Delivery Crew | Update order delivery status |

---

## ⚙️ Filtering, Sorting & Pagination

These features are supported for:

- `/api/menu-items/`
- `/api/orders/`

Capabilities:

- Filter by attributes like category or status
- Sort by fields like price or date
- Paginate results using query parameters (e.g., `?page=2`)

---

## 🚦 Throttling

Throttling is applied to limit request rates:

| User Type | Limit |
|-----------|-------|
| Anonymous | 10 requests/min |
| Authenticated | 100 requests/min |

Returns a `429 Too Many Requests` response when the limit is exceeded.

---

## 🚨 Error Handling

The API returns appropriate HTTP status codes based on the outcome of the request:

| Code | Meaning |
|------|---------|
| 200 | OK – Successful GET, PUT, PATCH, DELETE |
| 201 | Created – Successful POST |
| 400 | Bad Request – Validation errors |
| 401 | Unauthorized – Invalid token or credentials |
| 403 | Forbidden – Insufficient permissions |
| 404 | Not Found – Resource does not exist |
| 429 | Too Many Requests – Throttling limit exceeded |

---

## Running the Project Locally

Follow these steps to set up and run the Little Lemon API on your local machine.

**Prerequisites:**

* Python 3.x
* Pipenv

1.  **Clone the Repository**

    Clone the project repository from GitHub:

    ```bash
    git clone https://github.com/ludvin7x/little-lemon-api.git
    cd little-lemon-api
    ```

2.  **Set Up the Virtual Environment and Install Dependencies**

    Use pipenv to install the project dependencies and activate the virtual environment:

    ```bash
    pipenv install
    pipenv shell
    ```

3.  **Generate Environment Variables**

    A new utility script `generate_env.py` is included to help generate the `.env` file with the necessary environment variables for local development, including a secure `SECRET_KEY` and debug settings.

    Run the script:

    ```bash
    python generate_env.py
    ```

    This will create a `.env` file in the root directory with appropriate values for local usage.

4.  **Run Database Migrations**

    Apply the necessary database migrations to set up the database schema:

    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser (Optional but Recommended)**

    Create a superuser account to access the Django Admin Panel, which is useful for managing users, groups, and initial data:

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to create the user.

6.  **Start the Development Server**

    Launch the Django development server:

    ```bash
    python manage.py runserver
    ```

    The API should now be running locally, typically accessible at `http://127.0.0.1:8000/`. You can access the Django Admin panel at `http://127.0.0.1:8000/admin/` (if you created a superuser).

---

## 📝 License

This project is for educational purposes only and is not intended for production use.
