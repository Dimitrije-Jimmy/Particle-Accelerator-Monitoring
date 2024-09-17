class MonitoringService:
    def __init__(self, sensor) -> None:
        """
        Initialize the MonitoringService with a Sensor object.

        :param sensor: Sensor object to monitor
        :type sensor: device_app.sensor.Sensor
        """
        self.sensor = sensor

    def check_out_of_control(self, df, data_column) -> list[str]:
        """
        Check if the given sensor data is out of control limits.

        :param df: Sensor data to check
        :type df: pd.DataFrame
        :param data_column: Name of the column in df to check
        :type data_column: str
        :return: List of warning messages
        :rtype: List[str]
        """
        warnings = []
        ucl = self.sensor.ucl
        lcl = self.sensor.lcl
        for timestamp, value in zip(df['timestamp_measured'], df[data_column]):
            if value > ucl or value < lcl:
                warning_msg = f"{self.sensor.name}: Value {value} at {timestamp} is out of control limits."
                warnings.append(warning_msg)
        return warnings

    def check_device_failure(self, df) -> list[str]:
        """
        Check if the given sensor data indicates a device failure.

        :param df: Sensor data to check
        :type df: pd.DataFrame
        :return: List of warning messages
        :rtype: List[str]
        """
        if df.empty and self.sensor.state == self.sensor.state.MEASURING:
            warning_msg = f"{self.sensor.name}: No data detected while measuring. Possible device failure."
            return [warning_msg]
        return []
