# membrane.py

from typing import Callable, Dict, List


class Membrane:
    def __init__(self, filter_function: Callable[[Dict], bool]):
        """
        Membrane encapsulates the system, acting as an input interface and protective shell.
        It integrates seamlessly with the data preprocessing pipeline and dashboard visualization components.
        Ensures alignment with overall system security and threat mitigation processes.
        """
        self.filter_function = filter_function
        self.environment_data = []
        self.dashboard_data = {"raw_data": 0, "insights": 0, "threats_blocked": 0}

    def drop_data(self, raw_data: List[Dict]):
        """
        Handles drag-and-drop input, validating and releasing data into the system.
        Updates threat statistics for invalid data.
        Ensures correct integration with the data ingestion pipeline.
        """
        filtered_data = [data for data in raw_data if self.filter_function(data)]
        threats_blocked = len(raw_data) - len(filtered_data)
        self.environment_data.extend(filtered_data)
        self.dashboard_data["raw_data"] += len(filtered_data)
        self.dashboard_data["threats_blocked"] += threats_blocked

    def get_dashboard_stats(self) -> Dict:
        """
        Provides summary statistics for integration into the dashboard, ensuring real-time monitoring of threats and processed data.
        """
        return self.dashboard_data
