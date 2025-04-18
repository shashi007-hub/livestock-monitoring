## System Design Documentation

This document provides a comprehensive overview of the system architecture, component responsibilities, and interactions.

### 1. System Architecture

The system follows a distributed architecture with the following key components:

* **FastAPI Server**: A Python application using the FastAPI framework.

* **MQTT Broker**: A message broker for asynchronous communication (e.g., Mosquitto).

* **PostgreSQL Database**: A relational database for storing structured data.

* **Go Worker Processes**: Go applications responsible for executing the DL model inference.

### 2. Component Responsibilities

#### 2.1 FastAPI Server

* **API Management**:

    * Handles HTTP requests from clients (e.g., web applications, mobile apps).

    * Defines API endpoints for accessing and manipulating data (e.g., bovine data, sensor data).

    * Validates request data and returns appropriate responses.

* **User Authentication and Authorization**:

    * Implements user authentication to verify the identity of users (e.g., using JWT, OAuth2).

    * Manages user roles and permissions to control access to specific API endpoints and data.

    * Protects sensitive data and ensures that only authorized users can perform certain actions.

* **Database Interaction**:

    * Uses SQLAlchemy to interact with the PostgreSQL database.

    * Stores and retrieves data related to bovines, sensors, users, and other relevant entities.

* **Task Distribution**:

    * Publishes task announcement messages to the MQTT broker.

    * These messages trigger the Go worker processes to perform inference.

* **Business Logic**:

    * Implements the core business logic of the farm management system.

    * This includes data processing, aggregation, and coordination of different system components, user management, and access control.

#### 2.2 MQTT Broker

* **Message Routing**:

    * Routes messages between different components based on topics.

    * Ensures that task announcements are delivered to the appropriate Go worker processes.

* **Asynchronous Communication**:

    * Enables asynchronous communication between the FastAPI server and the Go worker processes.

    * This decouples the components and allows them to operate independently.

* **Scalability**:

    * Provides a scalable and efficient way to distribute tasks and collect results.

#### 2.3 PostgreSQL Database

* **Data Storage**:

    * Persistently stores structured data for the farm management system.

    * This includes information about:

        * Bovines (e.g., ID, breed, health records)

        * Sensors (e.g., ID, type, location)

        * Users (e.g., accounts, roles, permissions)

        * Sensor data readings

        * Model inference results

* **Data Retrieval**:

    * Provides efficient mechanisms for querying and retrieving data.

    * Supports complex queries and relationships between data entities.

* **Data Integrity**:

    * Ensures data consistency and integrity through transactions and constraints.

#### 2.4 Go Worker Processes

* **Task Execution**:

    * Subscribe to task announcement topics on the MQTT broker.

    * Receive tasks that contain information about which data needs to be processed.

* **DL Model Inference**:

    * Load and execute the DL model (ONNX) to perform inference on the sensor data.

    * This is the core computational task of the worker process.

* **Result Publication**:

    * Publish the inference results to a designated topic on the MQTT broker.

    * The FastAPI server can then subscribe to this topic to collect the results.

* **Concurrency**:

    * Use Goroutines to achieve high levels of concurrency when processing inference tasks.

    * Efficiently utilize the CPU and memory resources of the worker nodes.

### 3. Component Interactions

1.  **Data Ingestion**:

    * Sensors collect data and send it to the MQTT broker.

    * The FastAPI server may subscribe to these topics to store the raw data in the PostgreSQL database.

2.  **User Authentication**:

    * A user interacts with the FastAPI server through a client (e.g., web browser).

    * The user provides their credentials (e.g., username and password) to the FastAPI server.

    * The FastAPI server verifies the credentials against the data stored in the PostgreSQL database.

    * Upon successful authentication, the FastAPI server issues a token (e.g., JWT) to the client.

    * The client includes this token in subsequent requests to the FastAPI server.

    * The FastAPI server validates the token in each request to ensure that the user is authorized to access the requested resource.

3.  **Task Distribution**:

    * The FastAPI server, based on incoming requests or scheduled tasks, publishes task announcement messages to the MQTT broker.

    * These messages contain the necessary information for the Go workers to perform inference (e.g., data location, model parameters).

4.  **Task Processing**:

    * Go worker processes subscribe to the task announcement topic on the MQTT broker.

    * When a task announcement arrives, a worker process claims the task.

    * The worker process retrieves the relevant sensor data (either from the MQTT broker or a data storage).

    * The worker process performs the DL model inference.

5.  **Result Collection**:

    * The Go worker process publishes the inference results to a designated topic on the MQTT broker.

    * The FastAPI server subscribes to this topic to receive the results.

    * The FastAPI server may then store the results in the PostgreSQL database or send them to other applications.

### 4. Deployment Diagram

[FastAPI Server] <--> [PostgreSQL Database]|| (MQTT)v[MQTT Broker]^| (MQTT)[Go Worker Processes]
### 5. Authentication Flow

sequenceDiagramparticipant Userparticipant Clientparticipant FastAPI Serverparticipant PostgreSQL DatabaseUser->>Client: Request loginClient->>FastAPI Server: Send credentials (username, password)FastAPI Server->>PostgreSQL Database: Verify credentialsPostgreSQL Database-->>FastAPI Server: Return authentication statusFastAPI Server-->>Client: Issue token (if successful)Client-->>User: Login successfulUser->>Client: Access protected resourceClient->>FastAPI Server: Send request with tokenFastAPI Server->>FastAPI Server: Validate tokenFastAPI Server->>PostgreSQL Database: Authorize request (check permissions)PostgreSQL Database-->>FastAPI Server: Return authorization statusFastAPI Server-->>Client: Return requested resource (if authorized)Client-->>User: Resource access successful
### 6. Data Flow Diagram

flowchart TDA[Sensor] -- Data --> B(MQTT Broker)B -- Task Announcement --> C{Go Worker Process}C -- Sensor Data Request --> BB -- Sensor Data --> CC -- Inference Results --> BB -- Results to FastAPI --> D[FastAPI Server]D -- Store Results --> E(PostgreSQL Database)style A fill:#90EE90,stroke:#333,stroke-width:2pxstyle B fill:#87CEFA,stroke:#333,stroke-width:2pxstyle C fill:#FFFFE