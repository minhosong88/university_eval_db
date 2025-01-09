# University Program Evaluation Database System

## Overview

This application is designed to support the evaluation of degree programs at a university. It streamlines the process of collecting, managing, and analyzing data related to degrees, courses, instructors, goals, and evaluations. The system integrates a MySQL database with an intuitive GUI for efficient data entry, querying, and reporting, enabling program administrators to make data-driven decisions for academic improvement.

The project was developed as part of a comprehensive exploration of database design and application development principles, adhering to professional software development practices.

## Key Features

### Data Management

- **Degrees**: Add and manage degree information, including unique combinations of degree names and levels (e.g., BA, BS, MS, Ph.D., etc.).
- **Courses**: Associate courses with degrees, supporting multi-degree relationships.
- **Instructors**: Store instructor information, including unique IDs and names.
- **Sections**: Manage course sections by semester and year, including enrollment details.
- **Goals**: Define and track evaluation goals specific to each degree.

### Program Evaluation

- Enter evaluations for course sections based on predefined goals.
- Record the number of students achieving specific performance levels (A, B, C, F).
- Add improvement suggestions to enhance future goal achievement.
- Support evaluation duplication for courses associated with multiple degrees.

### Query and Reporting

- List courses, sections, and goals associated with specific degrees.
- Retrieve sections for a course or instructor within a specified time range.
- Analyze evaluation completeness and generate insights for program assessment.

## Technology Stack

- **Programming Language**: Python
- **Database**: MySQL
- **GUI Framework**: Tkinter
- **Development Tools**: MySQL Workbench, Python's `mysql-connector` library

## Setup and Installation

1. **Database Initialization**:

   - Ensure MySQL is installed and running.
   - Use the provided scripts to initialize the database schema (`data_manipulate_func.py`).

2. **Application Setup**:

   - Clone the repository.
   - Install required Python dependencies using `pip`:
     ```bash
     pip install mysql-connector-python
     ```
   - Run the main application file (`GUI.py`) to launch the interface.

3. **Configuration**:
   - Update `connection.py` with your MySQL server credentials.

## Usage

1. **Login**: Enter the database name, username, and password to establish a connection.
2. **Data Entry**: Use the intuitive GUI to add degrees, courses, instructors, sections, and goals.
3. **Evaluation**: Enter evaluation data for courses and sections, or update existing evaluations.
4. **Queries**: Retrieve detailed reports and insights for degrees, courses, or instructors.

## File Structure

- `connection.py`: Handles database connection initialization.
- `context.py`: Manages the application's database context.
- `data_entry_gui.py`: GUI for data entry operations.
- `eval_entry_gui.py`: GUI for entering and managing evaluations.
- `query_gui.py`: GUI for executing queries and displaying results.
- `data_manipulate_func.py`: Contains functions for database schema creation and data manipulation.
- `query_func.py`: Implements logic for querying database information.
- `GUI.py`: Main entry point for the application.

## Challenges and Learning Outcomes

This project reinforced key principles in:

- Relational database design and schema normalization.
- Developing robust GUI applications for database interactions.
- Writing reusable and modular Python code for maintainability.
- Handling data integrity and consistency through triggers and constraints.

## Future Enhancements

- Implement a web-based front-end for remote accessibility.
- Add advanced reporting features using visualization libraries.
- Expand support for additional evaluation methods and metrics.

## Acknowledgments

This project was developed as part of a coursework requirement for a database systems class. It emphasizes practical application of database management principles to solve real-world challenges.

## Contact

For questions or further information about this project, please contact:

- **Minho Song**  
  [hominsong@naver.com]  
  [www.linkedin.com/in/minhosong88]
