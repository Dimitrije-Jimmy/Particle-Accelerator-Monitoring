import time
from datetime import datetime
import random
import threading
import os
from pathlib import Path
import queue

# Get the current file's path
current_file = Path(__file__)

# Navigate to the root of the project (assuming the script is in 'src/')
root_dir = current_file.parent.parent  # Adjust as necessary (src is one level deep)

#print(f"Current File: {current_file}")
#print(f"Current File Parent: {current_file.parent}")
#print(f"Root Directory: {root_dir}")

# Initialize a global queue for passing log messages
log_queue = queue.Queue()


class Experiment:
    def __init__(self, mean: float = 5.0, stddev: float = 0.5, bias: float = 4.0, data_file: str = 'data_exp2.txt') -> None:
        """
        Initialize the Experiment object.

        Args:
            mean (float): The mean value of the pressure data.
            stddev (float): The standard deviation of the pressure data.
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
        self.data_file = os.path.join(root_dir, 'logs', data_file)
        self.running = False
        self.bias_injected = False
        self.device_failure = False

    def start_experiment(self) -> None:
        """
        Start the experiment by continuously generating pressure data and writing it to a file.

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

            # Generate Pressure data
            pressure = round(random.gauss(self.mean, self.stddev), 2)

            # Optionally inject abnormal bias
            if self.bias_injected:
                bias = round(random.uniform(self.bias, self.stddev), 2)  # Bias range
                pressure = round(pressure + bias, 2)
                print(f"Bias of {bias} bar injected into data.")

            # Write data to file with timestamp
            with open(self.data_file, 'a') as file:
                file.write(f"{pressure}, {datetime.now().isoformat()}, {time.time()}\n")

            print(f"Generated Pressure: {pressure} bar")
            time.sleep(2)
            self.clear_data()
            time.sleep(0.5)  # Small delay after clearing the file

    def stop_experiment(self) -> str:
        """
        Stop the experiment.

        Returns:
            str: Log message indicating experiment stopped.
        """
        self.running = False
        log_message = "Experiment 2 stopped."
        log_queue.put(log_message)
        print(log_message)
        return log_message

    # Methods to toggle bias injection and device failure
    def toggle_bias(self) -> str:
        """
        Toggle bias injection for experiment 2.

        Returns:
            str: Log message indicating bias injection state.
        """
        self.bias_injected = not self.bias_injected
        state = "enabled" if self.bias_injected else "disabled"
        log_message = f"Bias 2 injection {state}."
        log_queue.put(log_message)
        print(log_message)
        return log_message

    def toggle_device_failure(self) -> str:
        """
        Toggle device failure simulation for experiment 2.

        Returns:
            str: Log message indicating device failure simulation state.
        """
        self.device_failure = not self.device_failure
        state = "active" if self.device_failure else "inactive"
        log_message = f"Device 2 failure simulation {state}."
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
