import time
from datetime import datetime
import random
import threading
import os
from pathlib import Path
import queue

# Initialize a global queue for passing log messages
log_queue = queue.Queue()

class Experiment:
    def __init__(self, mean: float = 50.0, stddev: float = 5.0, bias: float = 30.0, data_file: str = 'data_exp1.txt') -> None:
        """
        Initialize the Experiment object.

        Args:
            mean (float): The mean value of the temperature data.
            stddev (float): The standard deviation of the temperature data.
            bias (float): The bias value to be injected into the data.
            data_file (str): The file name of the data file used by the sensor.

        Returns:
            None
        """
        self.mean = mean
        self.stddev = stddev
        self.bias = bias
        current_file = Path(__file__)
        root_dir = current_file.parent.parent
        #self.data_file = str(root_dir) +'\\logs\\' +data_file
        self.data_file = os.path.join(root_dir, 'logs', data_file)
        self.running = False
        self.bias_injected = False
        self.device_failure = False

    def start_experiment(self) -> None:
        """
        Starts the experiment.

        This method will start generating data and writing it to the file. It will
        also log a message indicating that the experiment has started. The method
        will continue to run until the `stop_experiment` method is called.

        The data is generated using a normal distribution with the given mean and
        standard deviation. The bias is applied to the data by adding a random
        value between 0 and the given bias to each data point.

        The data is written to the file with a timestamp and the current time.

        Args:
            None

        Returns:
            None
        """
        self.running = True
        while self.running:
            # If device failure, skip data generation
            if self.device_failure:
                time.sleep(2)
                continue

            # Generate temperature data
            temperature = round(random.gauss(self.mean, self.stddev), 2)

            # Optionally inject abnormal bias
            if self.bias_injected:
                bias = round(random.uniform(self.bias, self.stddev), 2)  # Bias range
                temperature = round(temperature + bias, 2)
                print(f"Bias of {bias} °C injected into data.")

            # Write data to file with timestamp
            with open(self.data_file, 'a') as file:
                file.write(f"{temperature}, {datetime.now().isoformat()}, {time.time()}\n")

            log_message = f"Generated Temperature: {temperature} °C at {datetime.now().isoformat()}"
            #log_queue.put(log_message)     # Don't log it because you have to empty entire queue then
            print(log_message)
            time.sleep(2)
            self.clear_data()
            time.sleep(1)  # Small delay after clearing the file

    def stop_experiment(self) -> str:
        """
        Stops the experiment.

        This method will stop the experiment from generating data and writing it to the
        file. It will also log a message indicating that the experiment has stopped.

        Returns:
            str: The log message that was written to the log queue.
        """
        self.running = False
        log_message = "Experiment 1 stopped."
        log_queue.put(log_message)
        print(log_message)
        return log_message

    # Methods to toggle bias injection and device failure
    def toggle_bias(self) -> str:
        """
        Toggles bias injection.

        This method is used to inject bias into the experiment data. When the bias
        injection is active, the experiment will generate data with an added bias
        value. Otherwise, the experiment will generate data without bias.

        Returns:
            str: A log message indicating the status of bias injection.
        """
        self.bias_injected = not self.bias_injected
        state = "enabled" if self.bias_injected else "disabled"
        log_message = f"Bias 1 injection {state}."
        log_queue.put(log_message)
        print(log_message)
        return log_message

    def toggle_device_failure(self) -> str:
        """
        Toggles device failure simulation.

        This method is used to simulate device failure. When the device failure
        is active, the experiment will stop generating data before being toggled again.

        Returns:
            str: A log message indicating the status of device failure simulation.
        """
        self.device_failure = not self.device_failure
        state = "active" if self.device_failure else "inactive"
        log_message = f"Device 1 failure simulation {state}."
        log_queue.put(log_message)
        print(log_message)
        return log_message

    def clear_data(self) -> None:
        """Clears the data file by overwriting it with an empty string."""
        with open(self.data_file, 'w'):
            pass
        #print("Data file cleared.")

# Use threading for controlling the experiment in a non-blocking way
exp = Experiment()

def run_experiment() -> None:
    """Starts the experiment in a separate thread."""
    thread = threading.Thread(target=exp.start_experiment)
    thread.start()

if __name__ == "__main__":
    run_experiment()
