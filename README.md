# Academic Performance Analyzer 📊

A comprehensive web application for analyzing student examination results with interactive visualizations and detailed reporting.

## Features

- **📁 File Upload**: Support for Excel files (.xlsx, .xls)
- **📊 Interactive Dashboards**: Visual analysis with charts and graphs
- **📈 Performance Analytics**: Subject-wise and student-wise analysis
- **📋 Detailed Reports**: Pass/fail analysis and performance trends
- **🔧 Configurable Settings**: Customizable pass criteria
- **🔒 Privacy Options**: Toggle student ID visibility

## Screenshots

_Upload your screenshots here to showcase the application_

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager

### Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/academic-performance-analyzer.git
   cd academic-performance-analyzer
   ```

2. **Create a virtual environment** (recommended)

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:8501`

## Usage

### Data Format

Your Excel file should contain:

- `Student_ID`: Unique identifier for each student
- `Student_Name`: Student's name
- Subject columns with numerical marks

Example:
| Student_ID | Student_Name | Math | Science | English | History |
|------------|--------------|------|---------|---------|---------|
| 001 | John Doe | 85 | 78 | 92 | 76 |
| 002 | Jane Smith | 76 | 89 | 85 | 82 |

### Analysis Features

1. **Upload Data**: Use the sidebar to upload your Excel file
2. **Configure Settings**: Set pass percentage and display options
3. **View Analytics**: Explore various charts and statistics
4. **Generate Reports**: Download detailed analysis reports

## Project Structure

```
AcademicPerformanceAnalyzer/
├── app.py                 # Main Streamlit application
├── analysis_engine.py     # Core analysis logic
├── data_validator.py      # Data validation utilities
├── report_generator.py    # Report generation functions
├── requirements.txt       # Python dependencies
├── pyproject.toml        # Project configuration
├── .replit              # Replit configuration
└── README.md            # Project documentation
```

## Technologies Used

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualizations
- **OpenPyXL**: Excel file handling

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

## Acknowledgments

- Thanks to the Streamlit community for the excellent documentation
- Plotly team for the amazing visualization library
- All contributors who helped improve this project

---

⭐ If you found this project helpful, please give it a star!
