# Microservices-Based E-Commerce Platform

This project is an advanced e-commerce platform built using microservices architecture. It consists of six distinct services: Product, Inventory, Order, Payment, Notification, and User. Each service is self-contained, scalable, and communicates with others via Kafka for event-driven architecture.

## Table of Contents

- [Project_Description]
- [Services_Overview]
- [Architecture_Diagram]
- [Prerequisites]
- [Setup_Instructions]

## Project Description

This platform enables users to manage products, inventory, orders, and payments seamlessly across distributed services. The integration with Stripe for payment processing and Kafka for asynchronous communication makes this system robust, flexible, and scalable.

## Services Overview

### 1. **Product Service**
   - **Responsibilities**: Manages product data, including creation, updates, and retrieval.
   - **Database**: PostgreSQL.
   - **Key Endpoints**: 
     - `POST /products/`
     - `GET /products/`
     - `GET /products/{product_id}`
     - `PATCH /products/{product_id}`
     - `DELETE /products/{product_id}`

### 2. **Inventory Service**
   - **Responsibilities**: Manages inventory levels, updating stock based on orders.
   - **Database**: PostgreSQL.
   - **Key Endpoints**:
     - `PATCH /inventory/{product_id}` - Adjust stock based on orders.
     - Listens to Kafka topics for order status and payment completion.

### 3. **Order Service**
   - **Responsibilities**: Manages orders from creation to payment tracking.
   - **Database**: PostgreSQL.
   - **Key Endpoints**:
     - `POST /orders/`
     - `GET /orders/`
     - `PATCH /orders/{order_id}` - Updates the status of an order.

### 4. **Payment Service**
   - **Responsibilities**: Integrates with Stripe for payment processing, handles payment status updates.
   - **Database**: PostgreSQL.
   - **Key Endpoints**:
     - `POST /payments/` - Initiates a payment.
     - `GET /stripe-callback/payment-success/` - Handles successful payment.
     - `GET /stripe-callback/payment-fail/` - Handles failed payment.
   - **Integration**: Sends events to update order status upon payment success.

### 5. **Notification Service**
   - **Responsibilities**: Sends notifications (e.g., order confirmation, payment success).
   - **Database**: None (stateless service, could use external notification systems like Twilio, SendGrid).
   - **Integration**: Listens to Kafka topics to trigger notifications.

### 6. **User Service**
   - **Responsibilities**: Handles user authentication, registration, and profile management.
   - **Database**: PostgreSQL.
   - **Key Endpoints**:
     - `POST /register/`
     - `POST /token/` - Generates JWT tokens for authentication.
     - `GET /user_profile/` - Retrieves user profile information.

## Architecture Diagram

![Architecture_Diagram]

The architecture follows a microservices pattern where each service is isolated and communicates with others via Kafka. The use of FastAPI allows for asynchronous operations, making the system highly responsive and scalable.

## Prerequisites

- **Docker**: To run services in containers.
- **Kafka**: For inter-service communication.
- **PostgreSQL**: Each service that requires a database uses PostgreSQL.
- **Stripe API**: For handling payments in the Payment service.
- **FastAPI**: All services are built using FastAPI.

## Setup Instructions

1. **Clone the Repository**

    ```bash
    git clone https://github.com/ahadnaeem785/mart_project
    cd yourprojectname
    ```

2. **Set Up Docker and Kafka**
   
   Ensure Docker and Kafka are running:
   
   ```bash
   docker compose up --build
