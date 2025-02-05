import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
import logging
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class DatasetMetadata:
    name: str
    created_at: datetime
    rows: int
    columns: int
    data_types: Dict[str, str]
    missing_values: Dict[str, int]
    validation_status: str
    processing_history: List[str]

class DataValidator:
    """
    Validates and sanitizes input data according to predefined rules.
    """
    def __init__(self):
        self.logger = logging.getLogger("data_validator")
        self.validation_rules = {
            "numeric": self._validate_numeric,
            "categorical": self._validate_categorical,
            "temporal": self._validate_temporal
        }

    def _validate_numeric(self, data: pd.Series) -> tuple[bool, List[str]]:
        """Validates numeric data for range and outliers."""
        issues = []
        if data.isnull().sum() > len(data) * 0.2:
            issues.append(f"High number of missing values: {data.isnull().sum()}")
        
        # Check for outliers using IQR
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = ((data < lower) | (data > upper)).sum()
        
        if outliers > len(data) * 0.1:
            issues.append(f"High number of outliers: {outliers}")
        
        return len(issues) == 0, issues

    def _validate_categorical(self, data: pd.Series) -> tuple[bool, List[str]]:
        """Validates categorical data for cardinality and missing values."""
        issues = []
        unique_values = data.nunique()
        
        if unique_values == len(data):
            issues.append("Possibly incorrect categorical data: all values are unique")
        
        if data.isnull().sum() > len(data) * 0.1:
            issues.append(f"High number of missing values: {data.isnull().sum()}")
        
        return len(issues) == 0, issues

    def _validate_temporal(self, data: pd.Series) -> tuple[bool, List[str]]:
        """Validates temporal data for range and consistency."""
        issues = []
        try:
            pd.to_datetime(data)
        except Exception as e:
            issues.append(f"Invalid temporal data: {str(e)}")
            return False, issues
        
        return len(issues) == 0, issues

class DataPipeline:
    """
    Manages the end-to-end data processing pipeline including validation,
    transformation, and storage.
    """
    def __init__(self):
        self.validator = DataValidator()
        self.logger = logging.getLogger("data_pipeline")
        self.processed_datasets: Dict[str, DatasetMetadata] = {}

    def process_dataset(self, 
                       data: Union[pd.DataFrame, str, bytes],
                       dataset_name: str,
                       column_types: Optional[Dict[str, str]] = None) -> tuple[pd.DataFrame, DatasetMetadata]:
        """
        Processes a dataset through the complete pipeline.
        
        Parameters:
            data: Input data (DataFrame, file path, or bytes)
            dataset_name: Name identifier for the dataset
            column_types: Optional dictionary specifying column types
        
        Returns:
            Processed DataFrame and metadata
        """
        # Load data if necessary
        if isinstance(data, (str, bytes)):
            data = self._load_data(data)

        # Initialize metadata
        metadata = DatasetMetadata(
            name=dataset_name,
            created_at=datetime.now(),
            rows=len(data),
            columns=len(data.columns),
            data_types={},
            missing_values={},
            validation_status="pending",
            processing_history=[]
        )

        # Infer or use provided column types
        if column_types is None:
            column_types = self._infer_column_types(data)

        # Validate and clean data
        data, metadata = self._validate_and_clean(data, column_types, metadata)

        # Transform data
        data = self._transform_data(data, column_types)

        # Store metadata
        self.processed_datasets[dataset_name] = metadata

        return data, metadata

    def _load_data(self, data_source: Union[str, bytes]) -> pd.DataFrame:
        """Loads data from various sources."""
        try:
            if isinstance(data_source, bytes):
                return pd.read_csv(data_source)
            elif data_source.endswith('.csv'):
                return pd.read_csv(data_source)
            elif data_source.endswith('.json'):
                return pd.read_json(data_source)
            else:
                raise ValueError(f"Unsupported data source format: {data_source}")
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise

    def _infer_column_types(self, data: pd.DataFrame) -> Dict[str, str]:
        """Infers column types from data."""
        column_types = {}
        for column in data.columns:
            if pd.api.types.is_numeric_dtype(data[column]):
                column_types[column] = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(data[column]):
                column_types[column] = "temporal"
            else:
                column_types[column] = "categorical"
        return column_types

    def _validate_and_clean(self, 
                           data: pd.DataFrame, 
                           column_types: Dict[str, str],
                           metadata: DatasetMetadata) -> tuple[pd.DataFrame, DatasetMetadata]:
        """Validates and cleans the dataset."""
        validation_issues = []
        
        for column, dtype in column_types.items():
            if column not in data.columns:
                continue
                
            is_valid, issues = self.validator.validation_rules[dtype](data[column])
            if not is_valid:
                validation_issues.extend([f"{column}: {issue}" for issue in issues])
            
            # Record missing values
            metadata.missing_values[column] = data[column].isnull().sum()
            
            # Basic cleaning
            if dtype == "numeric":
                data[column] = pd.to_numeric(data[column], errors='coerce')
            elif dtype == "temporal":
                data[column] = pd.to_datetime(data[column], errors='coerce')

        metadata.validation_status = "failed" if validation_issues else "passed"
        metadata.processing_history.append(f"Validation completed with {len(validation_issues)} issues")
        
        return data, metadata

    def _transform_data(self, data: pd.DataFrame, column_types: Dict[str, str]) -> pd.DataFrame:
        """Applies transformations to the dataset."""
        for column, dtype in column_types.items():
            if column not in data.columns:
                continue
                
            if dtype == "numeric":
                # Handle outliers
                Q1 = data[column].quantile(0.25)
                Q3 = data[column].quantile(0.75)
                IQR = Q3 - Q1
                data[column] = data[column].clip(lower=Q1 - 1.5*IQR, upper=Q3 + 1.5*IQR)
                
                # Normalize
                data[column] = (data[column] - data[column].mean()) / data[column].std()
                
            elif dtype == "categorical":
                # Encode categorical variables
                if data[column].nunique() < 10:  # For low cardinality
                    data = pd.get_dummies(data, columns=[column], prefix=column)
                else:  # For high cardinality
                    data[column] = pd.factorize(data[column])[0]
        
        return data

    def export_results(self, dataset_name: str, format: str = "json") -> Union[str, bytes]:
        """Exports processing results and metadata."""
        if dataset_name not in self.processed_datasets:
            raise ValueError(f"Dataset {