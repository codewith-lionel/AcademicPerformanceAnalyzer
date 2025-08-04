import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from analysis_engine import ExamAnalyzer
from report_generator import ReportGenerator
from data_validator import DataValidator

# --- Custom CSS for style ---
st.markdown('''
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2d6cdf;
        margin-bottom: 0.5rem;
    }
    .section-banner {
        background: linear-gradient(90deg, #2d6cdf 0%, #6dd5ed 100%);
        color: white;
        padding: 0.7rem 1.2rem;
        border-radius: 0.5rem;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
        box-shadow: 0 2px 8px rgba(44, 62, 80, 0.08);
    }
    .stMetric label, .stMetric span {
        color: #2d6cdf !important;
    }
    .stDataFrame thead tr th {
        background: #e3f0fc !important;
        color: #2d6cdf !important;
    }
    </style>
''', unsafe_allow_html=True)

# Configure page
st.set_page_config(
    page_title="Student Examination Results Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.markdown('<div class="main-title">📊 Student Examination Results Analysis System</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar for file upload and configuration
with st.sidebar:
    st.header("Configuration")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx', 'xls'],
        help="Upload an Excel file containing student marks data"
    )
    
    # Initialize session state for pass marks
    if 'subject_pass_marks' not in st.session_state:
        st.session_state.subject_pass_marks = {}
    
    # Pass criteria configuration
    st.subheader("Pass Criteria Management")
    
    # Global pass percentage (fallback)
    global_pass_percentage = st.slider(
        "Default Pass Percentage",
        min_value=1,
        max_value=100,
        value=40,
        help="Default percentage for subjects without specific pass marks"
    )
    
    # Subject-specific pass marks
    if uploaded_file is not None:
        # Load data to get subject columns
        try:
            temp_df = pd.read_excel(uploaded_file)
            temp_validator = DataValidator()
            
            # Get subject columns
            required_cols = temp_validator.required_columns
            optional_cols = temp_validator.optional_columns
            subject_columns = [col for col in temp_df.columns if col not in required_cols + optional_cols]
            
            if subject_columns:
                st.write("**Subject-Specific Pass Marks:**")
                
                # Create input fields for each subject
                updated_pass_marks = {}
                for subject in subject_columns:
                    current_value = st.session_state.subject_pass_marks.get(subject, global_pass_percentage)
                    pass_mark = st.number_input(
                        f"{subject}",
                        min_value=0.0,
                        max_value=100.0,
                        value=float(current_value),
                        step=1.0,
                        key=f"pass_mark_{subject}"
                    )
                    updated_pass_marks[subject] = pass_mark
                
                # Update session state
                st.session_state.subject_pass_marks = updated_pass_marks
                
                # Reset to default button
                if st.button("Reset All to Default"):
                    for subject in subject_columns:
                        st.session_state.subject_pass_marks[subject] = global_pass_percentage
                    st.rerun()
        except Exception as e:
            st.write("Upload a file to configure subject-specific pass marks")
    
    # Analysis options
    st.subheader("Analysis Options")
    
    round_decimals = st.selectbox(
        "Decimal Places",
        options=[0, 1, 2, 3],
        index=2,
        help="Number of decimal places for percentage calculations"
    )

# Main content area
if uploaded_file is not None:
    try:
        # Initialize components
        validator = DataValidator(st.session_state.subject_pass_marks)
        analyzer = ExamAnalyzer(global_pass_percentage, st.session_state.subject_pass_marks)
        report_generator = ReportGenerator(round_decimals)
        
        # Load and validate data
        with st.spinner("Loading and validating data..."):
            df = pd.read_excel(uploaded_file)
            
            # Validate data
            validation_result = validator.validate_data(df)
            
            if not validation_result['is_valid']:
                st.error("❌ Data Validation Failed")
                for error in validation_result['errors']:
                    st.error(f"• {error}")
                st.stop()
            
            # Show warnings if any
            if validation_result['warnings']:
                st.warning("⚠️ Data Warnings:")
                for warning in validation_result['warnings']:
                    st.warning(f"• {warning}")
        
        # Display data preview
        st.markdown('<div class="section-banner">📋 Data Preview</div>', unsafe_allow_html=True)
        
        # Display data preview
        st.dataframe(df.head(10), use_container_width=True)
        
        # Perform analysis
        with st.spinner("Analyzing examination results..."):
            analysis_results = analyzer.analyze_results(df)
        
        # Display results in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "🎯 Department Summary",
            "📈 Subject Analysis",
            "🏆 Top Performers",
            "📄 Detailed Report"
        ])
        
        with tab1:
            st.markdown('<div class="section-banner">📊 Performance Overview</div>', unsafe_allow_html=True)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Students",
                    analysis_results['total_students']
                )
            
            with col2:
                st.metric(
                    "Total Subjects",
                    analysis_results['total_subjects']
                )
            
            with col3:
                st.metric(
                    "Department Pass Rate",
                    f"{analysis_results['department_pass_rate']:.{round_decimals}f}%"
                )
            
            with col4:
                avg_score = analysis_results['average_score']
                st.metric(
                    "Average Score",
                    f"{avg_score:.{round_decimals}f}%"
                )
            
            # Performance distribution chart
            st.markdown('<div class="section-banner">📈 Score Distribution</div>', unsafe_allow_html=True)
            
            # Create score ranges
            score_ranges = ['0-40', '41-60', '61-80', '81-100']
            range_counts = [0, 0, 0, 0]
            
            for _, row in df.iterrows():
                subject_cols = [col for col in df.columns if col not in ['Student_ID', 'Student_Name']]
                scores = [row[col] for col in subject_cols if pd.notna(row[col])]
                
                for score in scores:
                    if score <= 40:
                        range_counts[0] += 1
                    elif score <= 60:
                        range_counts[1] += 1
                    elif score <= 80:
                        range_counts[2] += 1
                    else:
                        range_counts[3] += 1
            
            fig_dist = px.bar(
                x=score_ranges,
                y=range_counts,
                title="Score Distribution Across All Subjects",
                labels={'x': 'Score Range', 'y': 'Number of Scores'},
                color=range_counts,
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        with tab2:
            st.markdown('<div class="section-banner">🎯 Department Performance Summary</div>', unsafe_allow_html=True)
            
            # Department statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Students Passed All Subjects",
                    analysis_results['students_passed_all']
                )
                
                st.metric(
                    "Students Failed At Least One Subject",
                    analysis_results['students_failed_any']
                )
            
            with col2:
                pass_rate = analysis_results['department_pass_rate']
                fail_rate = 100 - pass_rate
                
                fig_pie = px.pie(
                    values=[pass_rate, fail_rate],
                    names=['Pass', 'Fail'],
                    title="Department Pass/Fail Distribution",
                    color_discrete_map={'Pass': '#2ecc71', 'Fail': '#e74c3c'}
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # Subject-wise pass rates
            st.markdown('<div class="section-banner">📚 Subject-wise Pass Rates</div>', unsafe_allow_html=True)
            subject_stats = analysis_results['subject_wise_stats']
            
            subject_names = list(subject_stats.keys())
            pass_rates = [subject_stats[subject]['pass_rate'] for subject in subject_names]
            
            fig_bar = px.bar(
                x=subject_names,
                y=pass_rates,
                title="Subject-wise Pass Rates",
                labels={'x': 'Subject', 'y': 'Pass Rate (%)'},
                color=pass_rates,
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with tab3:
            st.markdown('<div class="section-banner">📈 Subject-wise Analysis</div>', unsafe_allow_html=True)
            
            # Subject selection
            subject_names = list(analysis_results['subject_wise_stats'].keys())
            selected_subject = st.selectbox("Select Subject for Detailed Analysis", subject_names)
            
            if selected_subject:
                subject_data = analysis_results['subject_wise_stats'][selected_subject]
                
                # Subject metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "Pass Rate",
                        f"{subject_data['pass_rate']:.{round_decimals}f}%"
                    )
                
                with col2:
                    st.metric(
                        "Fail Rate",
                        f"{subject_data['fail_rate']:.{round_decimals}f}%"
                    )
                
                with col3:
                    st.metric(
                        "Average Score",
                        f"{subject_data['average_score']:.{round_decimals}f}"
                    )
                
                with col4:
                    st.metric(
                        "Highest Score",
                        f"{subject_data['highest_score']:.{round_decimals}f}"
                    )
                
                # Subject performance details
                st.markdown(f'<div class="section-banner" style="background:linear-gradient(90deg,#11998e 0%,#38ef7d 100%)">Performance Details - {selected_subject}</div>', unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                with col1:
                    # Pass/Fail pie chart
                    fig_subject_pie = px.pie(
                        values=[subject_data['passed_count'], subject_data['failed_count']],
                        names=['Pass', 'Fail'],
                        title=f"{selected_subject} - Pass/Fail Distribution",
                        color_discrete_map={'Pass': '#2ecc71', 'Fail': '#e74c3c'}
                    )
                    st.plotly_chart(fig_subject_pie, use_container_width=True)

                with col2:
                    # Get pass mark for this subject
                    subject_pass_mark = st.session_state.subject_pass_marks.get(selected_subject, global_pass_percentage)
                    
                    # Score histogram
                    subject_scores = df[selected_subject].dropna()
                    fig_hist = px.histogram(
                        x=subject_scores,
                        nbins=20,
                        title=f"{selected_subject} - Score Distribution",
                        labels={'x': 'Score', 'y': 'Frequency'}
                    )
                    fig_hist.add_vline(x=subject_pass_mark, line_dash="dash", 
                                     line_color="red", annotation_text=f"Pass Line ({subject_pass_mark}%)")
                    st.plotly_chart(fig_hist, use_container_width=True)

                # List students who failed this subject
                # List students who passed this subject
                st.markdown(f'<div class="section-banner" style="background:linear-gradient(90deg,#38ef7d 0%,#11998e 100%)">✅ Students Who Passed {selected_subject}</div>', unsafe_allow_html=True)
                passed_students = subject_data.get('passed_students', [])
                if passed_students:
                    # Add the subject mark to the display
                    passed_students_display = pd.DataFrame(passed_students)
                    if not passed_students_display.empty:
                        # Add the score for the selected subject
                        passed_students_display['Score'] = passed_students_display['Student_ID'].map(
                            dict(zip(df['Student_ID'], df[selected_subject]))
                        )
                        # Only show relevant columns
                        st.dataframe(passed_students_display[['Student_ID', 'Student_Name', 'Score']], use_container_width=True)
                    else:
                        st.info(f"No students passed {selected_subject}.")
                else:
                    st.info(f"No students passed {selected_subject}.")

                # List students who failed this subject
                st.markdown(f'<div class="section-banner" style="background:linear-gradient(90deg,#e74c3c 0%,#f9d423 100%)">❌ Students Who Failed {selected_subject}</div>', unsafe_allow_html=True)
                failed_students = df[(df[selected_subject] < subject_pass_mark) & (pd.notna(df[selected_subject]))]
                if not failed_students.empty:
                    failed_students_display = failed_students[['Student_ID', 'Student_Name', selected_subject]].copy()
                    failed_students_display = failed_students_display.rename(columns={selected_subject: 'Score'})
                    st.dataframe(failed_students_display, use_container_width=True)
                else:
                    st.success(f"All students passed {selected_subject}!")
        
        with tab4:
            st.markdown('<div class="section-banner">🏆 Top Performers</div>', unsafe_allow_html=True)
            
            # Overall top performer
            overall_top = analysis_results['overall_top_student']
            if overall_top:
                st.success(f"🥇 Overall Top Performer: {overall_top['name']} (Average: {overall_top['average']:.{round_decimals}f}%)")
            
            # Subject-wise toppers
            st.subheader("Subject-wise Toppers")
            
            toppers_data = []
            for subject, stats in analysis_results['subject_wise_stats'].items():
                if stats['topper']:
                    toppers_data.append({
                        'Subject': subject,
                        'Topper': stats['topper']['name'],
                        'Score': f"{stats['topper']['score']:.{round_decimals}f}%"
                    })
            
            if toppers_data:
                toppers_df = pd.DataFrame(toppers_data)
                st.dataframe(toppers_df, use_container_width=True)
            
            # Top 5 students overall
            st.subheader("Top 5 Students Overall")
            top_students = analysis_results['top_students'][:5]
            
            if top_students:
                top_students_data = []
                for i, student in enumerate(top_students, 1):
                    top_students_data.append({
                        'Rank': i,
                        'Student': student['name'],
                        'Average Score': f"{student['average']:.{round_decimals}f}%"
                    })
                
                st.dataframe(pd.DataFrame(top_students_data), use_container_width=True)
        
        with tab5:
            st.markdown('<div class="section-banner">📄 Detailed Analysis Report</div>', unsafe_allow_html=True)
            
            # Generate comprehensive report
            report_content = report_generator.generate_report(analysis_results, True)
            
            # Display report
            st.markdown(report_content)
            
            # Download report
            st.download_button(
                label="📥 Download Report",
                data=report_content,
                file_name="examination_analysis_report.md",
                mime="text/markdown"
            )
            
            # Export data option
            st.subheader("Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Export processed data to Excel
                export_data = analyzer.prepare_export_data(df, analysis_results, True)
                
                # Convert to Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    export_data['summary'].to_excel(writer, sheet_name='Summary', index=False)
                    export_data['subject_analysis'].to_excel(writer, sheet_name='Subject Analysis', index=False)
                    export_data['student_performance'].to_excel(writer, sheet_name='Student Performance', index=False)
                
                st.download_button(
                    label="📊 Export Analysis to Excel",
                    data=output.getvalue(),
                    file_name="examination_analysis_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            
            with col2:
                # Export to PDF
                try:
                    pdf_data = analyzer.export_to_pdf(df, analysis_results)
                    st.download_button(
                        label="📄 Export Report to PDF",
                        data=pdf_data,
                        file_name="examination_analysis_report.pdf",
                        mime="application/pdf"
                    )
                except Exception as pdf_error:
                    st.error(f"PDF export error: {str(pdf_error)}")
                    st.info("Please ensure reportlab is installed: pip install reportlab")
    
    except Exception as e:
        st.error(f"❌ An error occurred while processing the file: {str(e)}")
        st.info("Please ensure your Excel file has the correct format with student data.")

else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload an Excel file to begin analysis")
    
    st.subheader("📋 File Format Requirements")
    st.markdown("""
    Your Excel file should contain:
    - **Student_ID** column (required)
    - **Student_Name** column (required)
    - **Subject columns** with numerical scores (0-100)
    
    Example format:
    """)
    
    # Sample format table
    sample_data = {
        'Student_ID': ['S001', 'S002', 'S003'],
        'Student_Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Mathematics': [85, 92, 78],
        'Physics': [78, 88, 85],
        'Chemistry': [92, 85, 90]
    }
    
    st.dataframe(pd.DataFrame(sample_data), use_container_width=True)
    
    st.subheader("🔍 Analysis Features")
    st.markdown("""
    This system provides:
    - **Department Performance**: Overall pass/fail statistics
    - **Subject Analysis**: Individual subject performance metrics
    - **Top Performers**: Subject-wise and overall toppers
    - **Visual Reports**: Charts and graphs for easy interpretation
    - **Data Export**: Download analysis results and reports
    - **Privacy Protection**: Option to anonymize student identities
    """)
