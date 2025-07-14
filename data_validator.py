import pandas as pd
import numpy as np
from typing import Dict, List, Any

class DataValidator:
    """
    Validates Excel data for examination results analysis
    """
    
    def __init__(self):
        self.required_columns = ['Student_ID', 'Student_Name']
        self.min_score = 0
        self.max_score = 100
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate the uploaded Excel data
        
        Args:
            df: DataFrame containing the uploaded data
            
        Returns:
            Dictionary containing validation results
        """
        errors = []
        warnings = []
        
        # Check if DataFrame is empty
        if df.empty:
            errors.append("The uploaded file is empty or contains no data.")
            return {
                'is_valid': False,
                'errors': errors,
                'warnings': warnings
            }
        
        # Check required columns
        missing_columns = []
        for col in self.required_columns:
            if col not in df.columns:
                missing_columns.append(col)
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        
        # Check for subject columns (numeric data)
        subject_columns = [col for col in df.columns if col not in self.required_columns]
        
        if not subject_columns:
            errors.append("No subject columns found. Please ensure your file contains at least one subject with numeric scores.")
        
        # Validate data types and ranges
        if not errors:  # Only proceed if no critical errors
            # Check Student_ID column
            if 'Student_ID' in df.columns:
                if df['Student_ID'].isnull().any():
                    errors.append("Student_ID column contains missing values.")
                
                # Check for duplicate student IDs
                duplicates = df['Student_ID'].duplicated()
                if duplicates.any():
                    duplicate_ids = df[duplicates]['Student_ID'].tolist()
                    errors.append(f"Duplicate Student_IDs found: {', '.join(map(str, duplicate_ids))}")
            
            # Check Student_Name column
            if 'Student_Name' in df.columns:
                if df['Student_Name'].isnull().any():
                    warnings.append("Student_Name column contains missing values.")
                
                # Check for potentially duplicate names
                duplicate_names = df['Student_Name'].duplicated()
                if duplicate_names.any():
                    warnings.append("Potential duplicate student names found. Please verify if these are different students.")
            
            # Validate subject columns
            for subject in subject_columns:
                subject_errors, subject_warnings = self._validate_subject_column(df, subject)
                errors.extend(subject_errors)
                warnings.extend(subject_warnings)
        
        # Check minimum data requirements
        if not errors:
            # Check if we have enough data for meaningful analysis
            if len(df) < 5:
                warnings.append("Dataset contains fewer than 5 students. Analysis may not be statistically meaningful.")
            
            # Check if all subject columns are empty
            all_subjects_empty = True
            for subject in subject_columns:
                if not df[subject].isnull().all():
                    all_subjects_empty = False
                    break
            
            if all_subjects_empty:
                errors.append("All subject columns are empty. No data available for analysis.")
        
        # Data quality checks
        if not errors:
            quality_warnings = self._check_data_quality(df, subject_columns)
            warnings.extend(quality_warnings)
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _validate_subject_column(self, df: pd.DataFrame, subject: str) -> tuple:
        """Validate a single subject column"""
        errors = []
        warnings = []
        
        # Check if column exists
        if subject not in df.columns:
            errors.append(f"Subject column '{subject}' not found.")
            return errors, warnings
        
        # Get non-null values
        non_null_values = df[subject].dropna()
        
        if len(non_null_values) == 0:
            warnings.append(f"Subject '{subject}' has no valid scores.")
            return errors, warnings
        
        # Check data type (should be numeric)
        try:
            numeric_values = pd.to_numeric(non_null_values, errors='coerce')
            invalid_count = numeric_values.isnull().sum()
            
            if invalid_count > 0:
                errors.append(f"Subject '{subject}' contains {invalid_count} non-numeric values.")
        except:
            errors.append(f"Subject '{subject}' contains invalid data that cannot be converted to numbers.")
            return errors, warnings
        
        # Check value ranges
        numeric_values = numeric_values.dropna()
        
        if len(numeric_values) > 0:
            min_val = numeric_values.min()
            max_val = numeric_values.max()
            
            if min_val < self.min_score:
                errors.append(f"Subject '{subject}' contains scores below {self.min_score}: minimum value is {min_val}")
            
            if max_val > self.max_score:
                errors.append(f"Subject '{subject}' contains scores above {self.max_score}: maximum value is {max_val}")
            
            # Check for unusual patterns
            if min_val == max_val:
                warnings.append(f"Subject '{subject}' has identical scores for all students ({min_val})")
            
            # Check for too many missing values
            total_students = len(df)
            missing_count = df[subject].isnull().sum()
            missing_percentage = (missing_count / total_students) * 100
            
            if missing_percentage > 50:
                warnings.append(f"Subject '{subject}' has {missing_percentage:.1f}% missing values")
            elif missing_percentage > 20:
                warnings.append(f"Subject '{subject}' has {missing_percentage:.1f}% missing values")
        
        return errors, warnings
    
    def _check_data_quality(self, df: pd.DataFrame, subject_columns: List[str]) -> List[str]:
        """Check overall data quality and return warnings"""
        warnings = []
        
        # Check for students with all missing subject scores
        students_with_no_scores = 0
        for _, row in df.iterrows():
            has_score = False
            for subject in subject_columns:
                if pd.notna(row[subject]):
                    has_score = True
                    break
            
            if not has_score:
                students_with_no_scores += 1
        
        if students_with_no_scores > 0:
            warnings.append(f"{students_with_no_scores} students have no scores in any subject")
        
        # Check for subjects with very few students
        for subject in subject_columns:
            valid_scores = df[subject].dropna()
            if len(valid_scores) < 3:
                warnings.append(f"Subject '{subject}' has fewer than 3 valid scores")
        
        # Check for potential data entry errors (e.g., scores that are multiples of 5 or 10)
        for subject in subject_columns:
            valid_scores = df[subject].dropna()
            if len(valid_scores) > 0:
                # Check if more than 80% of scores are multiples of 5
                multiples_of_5 = sum(1 for score in valid_scores if score % 5 == 0)
                if multiples_of_5 > len(valid_scores) * 0.8:
                    warnings.append(f"Subject '{subject}' has unusually high number of scores that are multiples of 5")
        
        return warnings
    
    def get_column_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get information about columns in the dataset"""
        info = {
            'total_columns': len(df.columns),
            'required_columns': [],
            'subject_columns': [],
            'unknown_columns': []
        }
        
        for col in df.columns:
            if col in self.required_columns:
                info['required_columns'].append(col)
            elif col not in self.required_columns:
                # Assume it's a subject column if it contains numeric data
                try:
                    pd.to_numeric(df[col], errors='coerce')
                    info['subject_columns'].append(col)
                except:
                    info['unknown_columns'].append(col)
        
        return info
