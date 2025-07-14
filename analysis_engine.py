import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

class ExamAnalyzer:
    """
    Core analysis engine for processing student examination results
    """
    
    def __init__(self, pass_percentage: float = 40.0):
        self.pass_percentage = pass_percentage
        
    def analyze_results(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on examination results
        
        Args:
            df: DataFrame containing student examination data
            
        Returns:
            Dictionary containing all analysis results
        """
        # Get subject columns (exclude Student_ID and Student_Name)
        subject_cols = [col for col in df.columns if col not in ['Student_ID', 'Student_Name']]
        
        # Basic statistics
        total_students = len(df)
        total_subjects = len(subject_cols)
        
        # Calculate subject-wise statistics
        subject_wise_stats = self._calculate_subject_stats(df, subject_cols)
        
        # Calculate department pass rate
        department_pass_rate = self._calculate_department_pass_rate(df, subject_cols)
        
        # Find top performers
        overall_top_student = self._find_overall_top_student(df, subject_cols)
        top_students = self._find_top_students(df, subject_cols)
        
        # Calculate students who passed all subjects
        students_passed_all = self._count_students_passed_all(df, subject_cols)
        students_failed_any = total_students - students_passed_all
        
        # Calculate average score across all subjects
        all_scores = []
        for col in subject_cols:
            all_scores.extend(df[col].dropna().tolist())
        average_score = np.mean(all_scores) if all_scores else 0
        
        # Detect anomalies
        anomalies = self._detect_anomalies(df, subject_cols)
        
        return {
            'total_students': total_students,
            'total_subjects': total_subjects,
            'subject_wise_stats': subject_wise_stats,
            'department_pass_rate': department_pass_rate,
            'overall_top_student': overall_top_student,
            'top_students': top_students,
            'students_passed_all': students_passed_all,
            'students_failed_any': students_failed_any,
            'average_score': average_score,
            'anomalies': anomalies,
            'pass_percentage': self.pass_percentage
        }
    
    def _calculate_subject_stats(self, df: pd.DataFrame, subject_cols: List[str]) -> Dict[str, Dict]:
        """Calculate statistics for each subject"""
        subject_stats = {}
        
        for subject in subject_cols:
            # Get valid scores for this subject
            scores = df[subject].dropna()
            
            if len(scores) == 0:
                continue
                
            # Calculate basic statistics
            passed_count = len(scores[scores >= self.pass_percentage])
            failed_count = len(scores[scores < self.pass_percentage])
            total_count = len(scores)
            
            pass_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
            fail_rate = (failed_count / total_count) * 100 if total_count > 0 else 0
            
            average_score = scores.mean()
            highest_score = scores.max()
            lowest_score = scores.min()
            
            # Find topper
            topper_idx = scores.idxmax()
            topper_name = df.loc[topper_idx, 'Student_Name']
            topper_score = scores.max()
            
            subject_stats[subject] = {
                'passed_count': passed_count,
                'failed_count': failed_count,
                'total_count': total_count,
                'pass_rate': pass_rate,
                'fail_rate': fail_rate,
                'average_score': average_score,
                'highest_score': highest_score,
                'lowest_score': lowest_score,
                'topper': {
                    'name': topper_name,
                    'score': topper_score
                }
            }
        
        return subject_stats
    
    def _calculate_department_pass_rate(self, df: pd.DataFrame, subject_cols: List[str]) -> float:
        """Calculate overall department pass rate"""
        students_passed_all = self._count_students_passed_all(df, subject_cols)
        total_students = len(df)
        
        return (students_passed_all / total_students) * 100 if total_students > 0 else 0
    
    def _count_students_passed_all(self, df: pd.DataFrame, subject_cols: List[str]) -> int:
        """Count students who passed all subjects"""
        passed_all_count = 0
        
        for _, row in df.iterrows():
            passed_all = True
            for subject in subject_cols:
                if pd.isna(row[subject]) or row[subject] < self.pass_percentage:
                    passed_all = False
                    break
            
            if passed_all:
                passed_all_count += 1
        
        return passed_all_count
    
    def _find_overall_top_student(self, df: pd.DataFrame, subject_cols: List[str]) -> Optional[Dict]:
        """Find the overall top performing student"""
        student_averages = []
        
        for _, row in df.iterrows():
            scores = [row[col] for col in subject_cols if pd.notna(row[col])]
            if scores:
                average = np.mean(scores)
                student_averages.append({
                    'name': row['Student_Name'],
                    'average': average,
                    'scores': scores
                })
        
        if not student_averages:
            return None
        
        # Sort by average score
        student_averages.sort(key=lambda x: x['average'], reverse=True)
        
        return student_averages[0]
    
    def _find_top_students(self, df: pd.DataFrame, subject_cols: List[str], top_n: int = 10) -> List[Dict]:
        """Find top N students by overall performance"""
        student_averages = []
        
        for _, row in df.iterrows():
            scores = [row[col] for col in subject_cols if pd.notna(row[col])]
            if scores:
                average = np.mean(scores)
                student_averages.append({
                    'name': row['Student_Name'],
                    'average': average,
                    'total_subjects': len(scores)
                })
        
        # Sort by average score
        student_averages.sort(key=lambda x: x['average'], reverse=True)
        
        return student_averages[:top_n]
    
    def _detect_anomalies(self, df: pd.DataFrame, subject_cols: List[str]) -> List[Dict]:
        """Detect anomalies in the data"""
        anomalies = []
        
        for subject in subject_cols:
            scores = df[subject].dropna()
            
            if len(scores) == 0:
                anomalies.append({
                    'type': 'empty_subject',
                    'subject': subject,
                    'description': f"No valid scores found for {subject}"
                })
                continue
            
            # Check for perfect scores (might indicate data entry issues)
            perfect_scores = len(scores[scores == 100])
            if perfect_scores > len(scores) * 0.3:  # More than 30% perfect scores
                anomalies.append({
                    'type': 'excessive_perfect_scores',
                    'subject': subject,
                    'count': perfect_scores,
                    'description': f"Unusually high number of perfect scores in {subject} ({perfect_scores} students)"
                })
            
            # Check for zero scores
            zero_scores = len(scores[scores == 0])
            if zero_scores > 0:
                anomalies.append({
                    'type': 'zero_scores',
                    'subject': subject,
                    'count': zero_scores,
                    'description': f"{zero_scores} students have zero scores in {subject}"
                })
            
            # Check for very low pass rates
            pass_rate = len(scores[scores >= self.pass_percentage]) / len(scores) * 100
            if pass_rate < 20:  # Less than 20% pass rate
                anomalies.append({
                    'type': 'low_pass_rate',
                    'subject': subject,
                    'pass_rate': pass_rate,
                    'description': f"Very low pass rate in {subject} ({pass_rate:.1f}%)"
                })
        
        return anomalies
    
    def prepare_export_data(self, df: pd.DataFrame, analysis_results: Dict, show_student_ids: bool) -> Dict[str, pd.DataFrame]:
        """Prepare data for export"""
        subject_cols = [col for col in df.columns if col not in ['Student_ID', 'Student_Name']]
        
        # Summary data
        summary_data = {
            'Metric': [
                'Total Students',
                'Total Subjects',
                'Department Pass Rate (%)',
                'Students Passed All Subjects',
                'Students Failed At Least One Subject',
                'Average Score Across All Subjects (%)'
            ],
            'Value': [
                analysis_results['total_students'],
                analysis_results['total_subjects'],
                f"{analysis_results['department_pass_rate']:.2f}",
                analysis_results['students_passed_all'],
                analysis_results['students_failed_any'],
                f"{analysis_results['average_score']:.2f}"
            ]
        }
        
        # Subject analysis data
        subject_analysis_data = []
        for subject, stats in analysis_results['subject_wise_stats'].items():
            subject_analysis_data.append({
                'Subject': subject,
                'Total Students': stats['total_count'],
                'Passed': stats['passed_count'],
                'Failed': stats['failed_count'],
                'Pass Rate (%)': f"{stats['pass_rate']:.2f}",
                'Fail Rate (%)': f"{stats['fail_rate']:.2f}",
                'Average Score': f"{stats['average_score']:.2f}",
                'Highest Score': f"{stats['highest_score']:.2f}",
                'Lowest Score': f"{stats['lowest_score']:.2f}",
                'Topper': stats['topper']['name'] if not show_student_ids else f"Student_{hash(str(stats['topper']['name'])) % 10000:04d}"
            })
        
        # Student performance data
        student_performance_data = []
        for _, row in df.iterrows():
            student_data = {
                'Student_ID': row['Student_ID'] if show_student_ids else f"Student_{hash(str(row['Student_ID'])) % 10000:04d}",
                'Student_Name': row['Student_Name'] if show_student_ids else f"Student_{hash(str(row['Student_Name'])) % 10000:04d}"
            }
            
            # Add subject scores
            for subject in subject_cols:
                student_data[subject] = row[subject] if pd.notna(row[subject]) else 'N/A'
            
            # Calculate overall performance
            scores = [row[col] for col in subject_cols if pd.notna(row[col])]
            if scores:
                student_data['Average Score'] = f"{np.mean(scores):.2f}"
                student_data['Passed All Subjects'] = 'Yes' if all(score >= self.pass_percentage for score in scores) else 'No'
            else:
                student_data['Average Score'] = 'N/A'
                student_data['Passed All Subjects'] = 'N/A'
            
            student_performance_data.append(student_data)
        
        return {
            'summary': pd.DataFrame(summary_data),
            'subject_analysis': pd.DataFrame(subject_analysis_data),
            'student_performance': pd.DataFrame(student_performance_data)
        }
