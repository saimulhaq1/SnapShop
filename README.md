# 🛒 SnapShop — Full Stack E-Commerce Platform

A full-featured e-commerce web application built with **Python** and **Flask**, following a strict **MVC architecture** with carefully controlled application states and dynamic **AJAX-powered** interactions throughout.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
  - [Customer Side](#-customer-side)
  - [Admin Side](#-admin-side)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)

---

## Overview

SnapShop is a production-ready e-commerce platform that covers everything from product browsing to order delivery. The project is split into two main areas:

- **Customer Storefront** — a smooth, responsive shopping experience with live pricing, reviews, and order tracking
- **Admin Panel** — a powerful management dashboard for super admins and staff with role-based access control

---

## ✨ Features

### 🧑💻 Customer Side

#### Authentication
- Secure user registration and login
- Change password from profile settings
- Session-based authentication

#### Product Browsing
- View all products with detailed product pages
- Multiple product images per listing
- Top **trending products** and **top-selling items** displayed on homepage
- Product search and category filtering

#### Reviews & Community
- Leave **star ratings** and **written reviews** on products
- **Comment** on product pages
- **Like** other customer reviews
- Upload images in comments

#### Shopping Cart
- Add/remove products from cart
- **Live price calculation** — cart total updates instantly via AJAX (no page reload)
- Voucher/discount code application with real-time validation

#### Vouchers & Discounts
- Apply voucher codes at checkout
- Supports **Percentage (%)** and **Fixed Amount** discount types

#### Checkout
- Save and manage multiple delivery addresses
- Multiple payment options:
  - 💳 **Card Payment** (account holder name, card details)
  - 📱 **Digital Wallet**
  - 💵 **Cash on Delivery (COD)**
- Order summary before confirming purchase

#### Order Tracking
- View order status in real time
- Delivery tracking updates
- **Notifications** for sales, order updates, and delivery status changes

---

### 🔧 Admin Side

#### Login & Access Control
- Separate admin login portal
- **Super Admin** can create staff accounts and define their access permissions
- Each staff member only sees pages the super admin allows

#### Dashboard
- **Pending Orders** count
- **Latest Orders** list
- **Total Products** on the website
- **Total Customers** registered
- **Top 5 Selling Products** — bar chart
- **Revenue (Last 7 Days)** — line chart
- **Collected Revenue** and **Estimated Net Profit**
- **Quick Management Links** — jump to any page instantly
- **Inventory Status** — highlights products with fewer than 5 units remaining ⚠️

#### Staff Management
- Add new admin accounts
- Define role permissions per staff member
- Restrict page access per role

#### Customer Management
- Search customers by name, mobile, or email
- View customer details:
  - Location (City)
  - Address type
  - Payment preference
  - Account status (Active / Inactive)
- **View full order history** per customer
- **Lifetime spending** total per customer
- Toggle customer account status (Active / Inactive)

#### Address Management
- View and manage all customer saved addresses

#### Product Management
- Full product table with:
  - Product Detail, Brand, Art Code, Barcode
  - Cost Price, Tax Amount, Stock, Status
  - History and Actions
- **Edit products** — change images, add more images, update details
- Set **delivery charges** (free or custom price)

#### Category Management
- Add new categories
- Assign **parent categories**
- If parent category doesn't exist, create it first as a top-level category

#### Banner Management
- Upload promotional banners
- Banners **auto-rotate every 5 seconds** on the customer storefront

#### Voucher Management
- Create vouchers with:
  - Voucher Code and Name
  - Discount Type: Percentage (%) or Fixed Amount (RS)
  - Discount Value
  - Target Category (specific or all products)
  - Minimum Cart Value
  - Valid From / Valid Until dates
  - **Special Constraints:**
    - New Customers Only (account < 24 hrs)
    - First Order Only (0 previous successful orders)
    - One-Time Use Per User

#### Product Feedback (Reviews)
- View all product reviews
- **Reply** to customer reviews
- **Delete** inappropriate comments
- Monitor star ratings per product

#### Order Management
- Full orders table:
  - Order #, Customer, Date, Status, Total Amount
- **Update order status**: Processing → Shipped → Delivered → Cancelled
- Filter orders by status

#### Payment Management
- Full payment records:
  - Transaction ID, Associated Order, Method, Account Holder, Processed Date, Amount, Status
- Card and Digital Wallet payments update customer lifetime value once admin marks as **Paid**
- COD payments update customer lifetime value once admin marks as **Delivered**

#### Admin Profile
- Change admin password
- Logout securely

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Architecture | MVC (Model-View-Controller) |
| Frontend | HTML, CSS, JavaScript |
| Async Interactions | AJAX |
| Database | SQL (SQLite / MySQL) |
| Authentication | Flask session-based auth |
| Charts | Chart.js (dashboard) |
| Version Control | Git, GitHub |

---

## 📁 Project Structure

```
snapshop/
│
├── app/
│   ├── controllers/          # Route handlers (MVC Controllers)
│   │   ├── customer/
│   │   │   ├── auth.py
│   │   │   ├── cart.py
│   │   │   ├── orders.py
│   │   │   └── products.py
│   │   └── admin/
│   │       ├── dashboard.py
│   │       ├── orders.py
│   │       ├── products.py
│   │       ├── customers.py
│   │       ├── vouchers.py
│   │       └── staff.py
│   │
│   ├── models/               # Database models (MVC Models)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│   │   └── voucher.py
│   │
│   ├── views/                # Jinja2 HTML templates (MVC Views)
│   │   ├── customer/
│   │   │   ├── home.html
│   │   │   ├── product.html
│   │   │   ├── cart.html
│   │   │   └── checkout.html
│   │   └── admin/
│   │       ├── dashboard.html
│   │       ├── orders.html
│   │       └── products.html
│   │
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   └── __init__.py
│
├── config.py
├── requirements.txt
└── run.py
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- MySQL
- Flask
- pip
- Git

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/saimulhaq1/snapshop.git
cd snapshop
```

**2. Create a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure the database**
```bash
# Edit config.py with your database credentials
# Then run migrations
flask db init
flask db migrate
flask db upgrade
```

**5. Run the application**
```bash
python run.py
```

**6. Open in browser**
```
Customer Site:  http://localhost:5000
Admin Panel:    http://localhost:5000/admin
```

---

## 🚀 Usage

### Customer
1. Register an account at `/register`
2. Browse products on the homepage
3. Add items to cart — prices update live
4. Apply a voucher code if available
5. Checkout with your preferred payment method
6. Track your order from your profile

### Admin
1. Login at `/admin/login`
2. Use the dashboard to monitor orders and revenue
3. Manage products, categories, and banners
4. Process orders and update delivery status
5. Create vouchers for promotions
6. Manage staff permissions from Staff Management page

---

## 📸 Screenshots

### Admin Dashboard
![Admin Dashboard](screenshots/admin/dashboard.png)

### Orders Management
![Orders](screenshots/admin/orders.png)

### Customer Homepage
![Homepage](screenshots/customer/homepage.png)

### Product Page
![Product Page](screenshots/customer/product-page.png)

### Shopping Cart
![Cart](screenshots/customer/cart.png)

### Checkout Process
![Checkout](screenshots/customer/checkout.png)

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 👨💻 Author

**M. Saim UlHaq**
- GitHub: [@saimulhaq1](https://github.com/saimulhaq1)
- Email: Saimlhaq09@gmail.com

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
