import time
import csv
from datetime import datetime
from enum import Enum
import psycopg2
from pathlib import Path
import os
from dotenv import load_dotenv
import threading

# Load the .env file
load_dotenv()

# Access environment variables
#db_name = os.getenv("DB_NAME")
#db_user = os.getenv("DB_USER")
#db_password = os.getenv("DB_PASSWORD")
#db_host = os.getenv("DB_HOST")
#db_port = os.getenv("DB_PORT")
database_url = os.getenv("DATABASE_URL")

class SensorState(Enum):
    OFF = 'off'
    ON = 'on'
    MEASURING = 'measuring'
    IDLE = 'idle'

class RadiationSensor:
    def __init__(self, name: str, data_file: str = 'data_exp3.txt', db_conn: psycopg2.extensions.connection = None, loglogs: bool = False):
        """
        Initialize the TemperatureSensor object.

        Args:
            name (str): The name of the sensor.
            data_file (str, optional): The file name of the data file used by the sensor. Defaults to 'data_exp3.txt'.
            db_conn (psycopg2.extensions.connection, optional): The database connection to use for logging. Defaults to None.
            loglogs (bool, optional): Whether to log the log messages to the database. Defaults to False.
        """
        self.name = name
        self.state = SensorState.OFF
        self.current_radiation = None
        self.log_messages = []  # For storing log messages

        current_file = Path(__file__)
        root_dir = current_file.parent.parent
        self.data_file = os.path.join(root_dir, 'logs', data_file)
        self.log_file = os.path.join(root_dir, 'logs', f'{self.name}.csv')
        self.db_conn = db_conn  # Database connection

        self.ucl = 0.3  # Default UCL
        self.lcl = 0.1  # Default LCL

        self.loglogs = loglogs

        # Create the table for this sensor if it doesn't exist
        self.create_table()

    def create_table(self) -> None:
        """Create a table for the device in the PostgreSQL database."""
        if self.db_conn:
            with self.db_conn.cursor() as cur:
                table_name = f"{self.name}_measurements"

                sql = f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id SERIAL PRIMARY KEY,
                        radiation DOUBLE PRECISION NOT NULL,
                        timestamp_measured TIMESTAMPTZ NOT NULL,
                        timestamp_logged TIMESTAMPTZ NOT NULL
                    );
                """
                cur.execute(sql)
                self.db_conn.commit()

    def start(self) -> None:
        """Starts the sensor and sets its state to ON."""
        self.state = SensorState.ON
        self.log_messages.append(f"{datetime.now()}: {self.name} is now ON")
        print(f"{self.name} is now ON")

    def stop(self) -> None:
        """Stops the sensor and sets its state to OFF."""
        self.state = SensorState.OFF
        self.log_messages.append(f"{datetime.now()}: {self.name} is now OFF")
        print(f"{self.name} is now OFF")

    def start_measuring(self) -> None:
        """Starts the measuring process for the sensor."""
        if self.state == SensorState.ON or self.state == SensorState.IDLE:
            self.state = SensorState.MEASURING
            self.log_messages.append(f"{datetime.now()}: {self.name} started measuring")
            print(f"{self.name} started measuring")
            threading.Thread(target=self._measure).start()
        else:
            self.log_messages.append(f"{datetime.now()}: {self.name} must be ON to start measuring")
            print(f"{self.name} must be ON to start measuring")

    def stop_measuring(self) -> None:
        """Stops the measuring process of the sensor."""
        if self.state == SensorState.MEASURING:
            self.state = SensorState.IDLE
            self.log_messages.append(f"{datetime.now()}: {self.name} is now IDLE")
            print(f"{self.name} is now IDLE")

    def _measure(self) -> None:
        """Continuously read temperature data from the file."""
        while self.state == SensorState.MEASURING:
            data = self.read_data()
            if data is not None:
                if self.loglogs:
                    self.log_messages.append(f"{datetime.now()}: Measured radiation: {data['radiation']}°C at {data['timestamp_file']}")
                print(f"Measured radiation: {data['radiation']}°C at {data['timestamp_file']}")
            time.sleep(1)  # Adjust the sleep time as needed

    def read_data(self) -> dict[str, float | datetime] | None:
        """
        Reads the radiation and timestamp from the data file.

        Returns a dictionary with the radiation and timestamp if the file
        can be read, otherwise None.

        Parameters
        ----------
        None

        Returns
        -------
        dict[str, float | datetime] | None
            A dictionary with keys 'radiation' and 'timestamp_file' if the
            file can be read, otherwise None.
        """
        try:
            with open(self.data_file, 'r') as file:
                data = file.readlines()
                if data != []:
                    data = data[0].split(', ')
                    radiation = data[0]
                    timestamp_file = datetime.fromisoformat(data[1])
                    timeit_file = data[2]

                    self.current_radiation = float(radiation)
                    timestamp_read = datetime.now().isoformat()
                    self.log_data(timestamp_file, timestamp_read)
                    return {"radiation": self.current_radiation, "timestamp_file": timestamp_file}
        except (FileNotFoundError, ValueError) as e:
            self.log_messages.append(f"{datetime.now()}: Error reading file: {e}")
            print(f"Error reading file: {e}")
            return None

    def log_data(self, timestamp_file: datetime, timestamp_read: datetime) -> None:
        """
        Logs the radiation to a CSV file and database.

        Parameters
        ----------
        timestamp_file : datetime
            The timestamp of the data file.
        timestamp_read : datetime
            The current timestamp.

        Returns
        -------
        None
        """
        # Log to CSV
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.current_radiation, timestamp_file, timestamp_read])
            if self.loglogs:
                self.log_messages.append(f"{datetime.now()}: Logged data: {self.current_radiation}, {timestamp_file}, {timestamp_read}")
            print(f"Logged data: {self.current_radiation}, {timestamp_file}, {timestamp_read}")

        # Log to PostgreSQL
        if self.db_conn:
            with self.db_conn.cursor() as cur:
                table_name = f"{self.name}_measurements"
                cur.execute(f"""
                    INSERT INTO {table_name} (radiation, timestamp_measured, timestamp_logged)
                    VALUES (%s, %s, %s)
                """, (self.current_radiation, timestamp_file, timestamp_read))
                self.db_conn.commit()

    def get_status(self) -> None:
        """Returns the current state and radiation."""
        return {
            "name": self.name,
            "state": self.state.value,
            "current_radiation": self.current_radiation
        }

    def get_logs(self) -> None:
        """Returns the log messages."""
        return self.log_messages

    def disable(self) -> None:
        """Disable the sensor."""
        self.stop_measuring()
        self.stop()
        self.log_messages.append(f"{datetime.now()}: {self.name} has been disabled")
        print(f"{self.name} has been disabled")


    def log_warning(self, message) -> None:
        """Logs a warning message to the sensor's log messages."""
        self.log_messages.append(f"WARNING: {message}")

    def change_loglogs(self) -> None:
        """Changes the loglogs value."""
        if self.loglogs:
            self.loglogs = False
            logmessage = f'Sensor 3 detailed logs turned OFF'
            self.log_messages.append(logmessage)
            print(logmessage)
        else:
            self.loglogs = True
            logmessage = f'Sensor 3 detailed logs turned ON'
            self.log_messages.append(logmessage)
            print(logmessage)