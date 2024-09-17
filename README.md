# Particle Accelerator Monitoring Dashboard

This project is a sensor monitoring dashboard built with Dash, Plotly, and PostgreSQL. It simulates a particle accelerator experiment environment where multiple sensors collect data, allowing operators to visualize and control the particle accelerator experiment process efficiently.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Running](#installation-and-running)
  - [Using Docker (Recommended)](#using-docker-recommended)
  - [Manual Setup (Alternative)](#manual-setup-alternative)
- [Usage](#usage)
- [Possible Improvements](#possible-improvements)
- [Acknowledgments](#acknowledgments)

## Features

- Real-time monitoring of sensor data (Temperature, Pressure, Radiation)
- Control charts with upper and lower control limits
- Histograms showing data distribution
- Sensor logs with alerts for out-of-control measurements
- Experiment simulations with bias injection and device failure modes
- Interactive web UI built with Dash and Plotly

## Project Structure

```
project/
├── app.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .gitignore
├── .dockerignore
│
├── device_app/
│   ├── sensor1.py
│   ├── sensor2.py
│   ├── sensor3.py
│   └── monitoring_service.py
│
├── assets/
│   ├── base-styles.css
│   ├── fonts.css
│   ├── spc-custom-styles.css
│   ├── Cosylab-logo-2023.png
│   └── modal.js
│
├── experiment_app/
│   ├── experiment1.py
│   ├── experiment2.py
│   └── experiment3.py
│
└── experiment_app/
    ├── data_exp1.txt
    ├── data_exp2.txt
    ├── data_exp3.txt
    ├── temperature_sensor.csv
    ├── pressure_sensor.csv
    └── radiation_sensor.csv
```

- `app.py`: The main application file.
- `Dockerfile`: Docker configuration for the web application.
- `docker-compose.yml`: Docker Compose configuration to run the web app and PostgreSQL database.
- `requirements.txt`: Python dependencies.
- `.gitignore` and `.dockerignore`: Files to exclude certain files from Git and Docker builds (e.g., `.env` file).

## Prerequisites

- **Docker**: Install Docker from [here](https://docs.docker.com/get-docker/).
- **Docker Compose**: Comes with Docker Desktop on Windows and macOS. On Linux, you may need to install it separately.


## Installation and Running

### Using Docker (Recommended)

The application and the PostgreSQL database are containerized using Docker for easy setup and deployment.

#### **1. Clone the Repository**

```bash
git clone https://github.com/Dimitrije-Jimmy/Particle-Accelerator-Monitoring.git
cd https://github.com/Dimitrije-Jimmy/Particle-Accelerator-Monitoring
```

#### **2. Build and Run the Docker Containers**:

```bash
docker-compose up --build
```

- This command builds the Docker images and starts the containers defined in docker-compose.yml.
- It may take a few minutes on the first run to download necessary images and build the containers.
    
#### **3. Access the Application**:

Open your web browser and navigate to:
```arduino
http://localhost:8050/
```

The application should now be running, and you can interact with the dashboard.

#### **4. Stopping the Application**:

To stop the application and remove the containers, press `Ctrl+C` in the terminal where `docker-compose` is running, then execute:
```bash
docker-compose down
```

### Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the application manually.

#### Prerequisites
- Python 3.7 or higher
- PostgreSQL database
- Git

#### **1. Clone the Repository**

```bash
git clone https://github.com/Dimitrije-Jimmy/Particle-Accelerator-Monitoring.git
cd https://github.com/Dimitrije-Jimmy/Particle-Accelerator-Monitoring
```

#### **2. Create a Virtual Environment**:

```bash
python -m venv venv
```

#### **3. Activate the Virtual Environment**:

* On Windows:

  ```bash
  venv\Scripts\activate
  ```

* On macOS/Linux:

  ```bash
  source venv/bin/activate
  ```

#### **4. Install the required packages**:

```bash
pip install -r requirements.txt
```

#### **4. Install the required packages**:
* Install PostgreSQL if you haven't already.
* Create a database and user:

```sql
CREATE DATABASE sensor_data;
CREATE USER yourusername WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE sensor_data TO yourusername;
```

- Update the `DATABASE_URL` in a `.env` file:
```bash
DATABASE_URL=postgresql://yourusername:yourpassword@localhost:5432/sensor_data
```

#### **6. Run Database Migrations or Setup**:
(Optional) If you have migration scripts or need to set up the database schema, do so now.

#### **7. Run the Application**:

```bash
python -m app
```

#### **8. Access the Application**:

Access the application in your web browser:
```arduino
http://127.0.0.1:8050/ or [local.](http://localhost:8050/)
```

## Usage
* **Navigate through the tabs** to monitor sensor data and control experiments.
* **Select devices and time intervals** to view specific data.
* **Use the controls** to start/stop sensors and experiments, inject bias, or simulate device failures.
* **View logs and alerts** for detailed information.

## Possible Improvements
* **User Interface Enhancements**: Improve the UI design for better user experience.
* **Code Modularity**: Refactor code for better modularity and reusability.
* **Authentication**: Implement user login and registration for secure access.
* **Testing**: Perform thorough testing for concurrent users and devices.

## Acknowledgments
This project was developed as part of job interview task and a learning experience to enhance skills in:
* Object-oriented programming in Python
* Building interactive web UIs with Dash and Plotly
* Integrating Python with PostgreSQL
* Working with JavaScript and CSS

