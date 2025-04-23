# 🍋 Little Lemon API

🚀 **Live API URL**: [https://little-lemon-api-yexw.onrender.com/](https://little-lemon-api-yexw.onrender.com/)

This project implements a fully functional RESTful API for **Little Lemon**, a fictional restaurant. It enables client developers to build web and mobile applications that support various user roles with specific permissions, including menu management, order processing, delivery crew assignment, and more.

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
- Token-based authentication using Djoser
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
- Djoser (for authentication)  
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

Authentication is handled by [Djoser](https://djoser.readthedocs.io/). The following endpoints are used:

| Endpoint | Method | Access | Description |
|----------|--------|--------|-------------|
| `/auth/users/` | POST | Public | Register a new user |
| `/auth/users/me/` | GET | Authenticated | Retrieve current user details |
| `/auth/token/login/` | POST | Public | Obtain token for login |
| `/auth/token/logout/` | POST | Authenticated | Logout the current user |


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
| `/api/cart/menu-items/` | GET | Customer | View items in current user's cart |
| `/api/cart/menu-items/` | POST | Customer | Add item to cart |
| `/api/cart/menu-items/` | DELETE | Customer | Clear all items in the cart |

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
    git clone [https://github.com/ludvin7x/little-lemon-api.git](https://github.com/ludvin7x/little-lemon-api.git)
    cd little-lemon-api
    ```

2.  **Set Up the Virtual Environment and Install Dependencies**

    Use pipenv to install the project dependencies and activate the virtual environment:

    ```bash
    pipenv install
    pipenv shell
    ```

3.  **Generate the Secret Key**

    Create a `.env` file in the root directory of the project. This file will store environment-specific variables, such as the Django `SECRET_KEY`.

    ```ini
    # .env
    SECRET_KEY=your-generated-secret-key
    DEBUG=True # Optional: Set to True for development
    ```

    Generate a strong random `SECRET_KEY` by running the following command:

    ```bash
    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
    ```

    Copy the output and paste it as the value for `SECRET_KEY` in your `.env` file.

4.  **Run Database Migrations**

    Apply the necessary database migrations to set up the database schema:

    ```bash
    python manage.py migrate
    ```

5.  **Create a Superuser (Optional but Recommended)**

    Create a superuser account to access the Django Admin Panel, which is useful for managing users, groups, and potentially initial data:

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

## 📝 License

This project is for educational purposes only and is not intended for production use.
