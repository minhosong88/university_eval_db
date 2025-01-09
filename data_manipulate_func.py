import re
from context import context
import mysql.connector


def create_tables(cur):
    """
    Creates all required tables in the database if they do not already exist.
    Ensures schema consistency with proper constraints and relationships.

    Args:
        cur (mysql.connector.cursor): Cursor object to execute SQL queries.
    """
    cur.execute("""
      CREATE TABLE IF NOT EXISTS degree (
        name VARCHAR(100) CHECK (CHAR_LENGTH(name) >= 1),
        level VARCHAR(50) NOT NULL,
        PRIMARY KEY (name, level)
        );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS course (
        name VARCHAR(100) NOT NULL CHECK (CHAR_LENGTH(name) >= 1),
        course_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(course_id) >= 6),
        PRIMARY KEY (course_id)
      );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS instructor (
        ins_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(ins_id) = 8) PRIMARY KEY,
        name VARCHAR(50) NOT NULL CHECK (CHAR_LENGTH(name) >= 1)
      );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS section (
        sec_id VARCHAR(3) NOT NULL,
        year YEAR NOT NULL,
        semester ENUM('Spring', 'Summer', 'Fall') NOT NULL,
        course_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(course_id) >= 6),
        ins_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(ins_id) = 8),
        num_student INT UNSIGNED NOT NULL,
        PRIMARY KEY (sec_id, semester, year, course_id),
        FOREIGN KEY (course_id) REFERENCES course(course_id),
        FOREIGN KEY (ins_id) REFERENCES instructor(ins_id)
      );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS goal (
        degree_name VARCHAR(100) CHECK (CHAR_LENGTH(degree_name) >= 1),
        level VARCHAR(50) NOT NULL,
        goal_code VARCHAR(4) NOT NULL,
        description VARCHAR(255) CHECK (CHAR_LENGTH(description) >= 1),
        PRIMARY KEY (degree_name, level, goal_code),
        FOREIGN KEY (degree_name, level) REFERENCES degree(name, level)
      );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS deg_course (
        degree_name VARCHAR(100) CHECK (CHAR_LENGTH(degree_name) >= 1),
        level VARCHAR(50) NOT NULL,
        course_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(course_id) >= 6),
        Is_Core BOOLEAN NOT NULL DEFAULT FALSE,
        PRIMARY KEY (degree_name, level, course_id),
        FOREIGN KEY (degree_name, level) REFERENCES degree(name, level),
        FOREIGN KEY (course_id) REFERENCES course(course_id)
      );
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS evaluation (
        sec_id VARCHAR(3) NOT NULL,
        semester ENUM('Spring', 'Summer', 'Fall') NOT NULL,
        year YEAR NOT NULL,
        course_id VARCHAR(8) NOT NULL CHECK (CHAR_LENGTH(course_id) >= 6),
        degree_name VARCHAR(100) CHECK (CHAR_LENGTH(degree_name) >= 1),
        level VARCHAR(50) NOT NULL,
        goal_code VARCHAR(4) NOT NULL,
        improvement VARCHAR(255) DEFAULT NULL,
        grade_a INT UNSIGNED DEFAULT NULL,
        grade_b INT UNSIGNED DEFAULT NULL,
        grade_c INT UNSIGNED DEFAULT NULL,
        grade_f INT UNSIGNED DEFAULT NULL,
        measure_type VARCHAR(50) NOT NULL,
        PRIMARY KEY (sec_id, semester, year, course_id, degree_name, level, goal_code),
        FOREIGN KEY (sec_id, semester, year, course_id) REFERENCES section(sec_id, semester, year, course_id),
        FOREIGN KEY (degree_name, level, goal_code) REFERENCES goal(degree_name, level, goal_code),
        FOREIGN KEY (degree_name, level, course_id) REFERENCES deg_course (degree_name, level, course_id)
      );
                """)

    # Implement sql trigger to enforce data consistency in evaluation so that the same course-section across goals or degree does not have different data entry
    # For example: goal1-degree1-course1-section1 // goal2-degree1-course1-section1 // goal1-degree2-course1-section1// all can have different data under this schema. Therefore, enforce the same course-section to have the same records.
    cur.execute("""
        DROP TRIGGER IF EXISTS enforce_consistent_evaluations;
    """)
    cur.execute("""
        DROP PROCEDURE IF EXISTS update_evaluations;
    """)
    cur.execute("""
        CREATE TRIGGER enforce_consistent_evaluations
        BEFORE INSERT ON evaluation
        FOR EACH ROW
        BEGIN
            DECLARE counts INT;
            DECLARE inconsistent_counts INT;
            
            SELECT COUNT(*)
            INTO counts
            FROM evaluation
            WHERE sec_id = NEW.sec_id
                AND semester = NEW.semester
                AND year = NEW.year
                AND course_id = NEW.course_id;
            
            IF counts > 0 THEN
                SELECT COUNT(*)
                INTO inconsistent_counts
                FROM evaluation
                WHERE sec_id = NEW.sec_id
                    AND semester = NEW.semester
                    AND year = NEW.year
                    AND course_id = NEW.course_id
                    AND (NOT (grade_a <=> NEW.grade_a) OR
                        NOT (grade_b <=> NEW.grade_b) OR
                        NOT (grade_c <=> NEW.grade_c) OR
                        NOT (grade_f <=> NEW.grade_f) OR
                        NOT (improvement <=> NEW.improvement) OR
                        NOT (measure_type <=> NEW.measure_type));
                IF inconsistent_counts > 0 THEN
                    SIGNAL SQLSTATE '45000'
                        SET MESSAGE_TEXT = 'Inconsistent evaluation data for the same course, section, semester, and year. Please Duplicate The Record';
                END IF;
            END IF;
        END;
                """)
    # If the same constraints applies to updates, it will basically prevent all updates of evaluation across degrees, updating all related records is chosen for consistency.
    cur.execute("""
        CREATE PROCEDURE update_evaluations(
            IN p_sec_id VARCHAR(3),
            IN p_semester VARCHAR(7),
            IN p_year INT UNSIGNED,
            IN p_course_id VARCHAR(8),
            IN p_degree_name VARCHAR(100),
            IN p_level VARCHAR(50),
            IN p_goal_code VARCHAR(4),
            IN p_improvement VARCHAR(255),
            IN p_grade_a INT,
            IN p_grade_b INT,
            IN p_grade_c INT,
            IN p_grade_f INT,
            IN p_measure_type VARCHAR(10)
        )
        BEGIN
            DECLARE records INT;

            SELECT COUNT(*) INTO records
            FROM evaluation
            WHERE sec_id = p_sec_id
                AND semester = p_semester
                AND year = p_year
                AND course_id = p_course_id
                AND NOT (degree_name = p_degree_name AND level = p_level AND goal_code = p_goal_code);
            
            IF records = 0 THEN
                UPDATE evaluation
                SET improvement = p_improvement,
                    grade_a = p_grade_a,
                    grade_b = p_grade_b,
                    grade_c = p_grade_c,
                    grade_f = p_grade_f,
                    measure_type = p_measure_type
                WHERE sec_id = p_sec_id
                    AND semester = p_semester
                    AND year = p_year
                    AND course_id = p_course_id
                    AND degree_name = p_degree_name
                    AND level = p_level
                    AND goal_code = p_goal_code;
                
                
            ELSEIF records > 0 THEN
                UPDATE evaluation
                SET improvement = p_improvement,
                    grade_a = p_grade_a,
                    grade_b = p_grade_b,
                    grade_c = p_grade_c,
                    grade_f = p_grade_f,
                    measure_type = p_measure_type
                WHERE sec_id = p_sec_id
                    AND semester = p_semester
                    AND year = p_year
                    AND course_id = p_course_id
                    AND degree_name = p_degree_name
                    AND level = p_level
                    AND goal_code = p_goal_code;
                UPDATE evaluation
                SET goal_code = p_goal_code,
                    improvement = p_improvement,
                    grade_a = p_grade_a,
                    grade_b = p_grade_b,
                    grade_c = p_grade_c,
                    grade_f = p_grade_f,
                    measure_type = p_measure_type
                WHERE sec_id = p_sec_id
                    AND semester = p_semester
                    AND year = p_year
                    AND course_id = p_course_id
                    AND NOT (degree_name = p_degree_name AND level = p_level);
            END IF;
        END;
        
                """)


def clear_data(cur):
    """
    Clears all data from the database tables while maintaining the schema integrity.

    Args:
        cur (mysql.connector.cursor): Cursor object to execute SQL queries.

    Returns:
        list: Messages indicating the success or failure of data clearing for each table.
    """
    # Create tables if tables don't exist
    create_tables(cur)

    # Define the table deletion order to maintain data integrity
    deletion_order = ['evaluation', 'section', 'instructor',
                      'deg_course', 'course', 'goal', 'degree']

    # Filter deletion order by the specified table names
    messages = []
    for table in deletion_order:
        try:
            cur.execute(f"DELETE FROM {table};")
            print(f"Data cleared from {table}")
            messages.append({"table": table, "status": "success",
                            "message": f"Data cleared from {table}"})
        except Exception as e:
            print(f"Failed to delete from table {table}: {e}")
            messages.append({"table": table, "status": "error",
                            "message": f"Failed to delete from table {table}: {e}"})
    return messages


def enter_degree(cur, deg_name: str, level: str):
    """
    Inserts a new degree into the database.

    Args:
        cur (mysql.connector.cursor): Cursor object to execute SQL queries.
        deg_name (str): Name of the degree.
        level (str): Level of the degree (e.g., BA, BS, MS).

    Returns:
        dict: Success or error message based on the operation.
    """
    deg_name = deg_name.title()
    deg_name_pattern = r'^[A-Za-z\s]+$'
    if not re.match(deg_name_pattern, deg_name):
        return {"error": f"Degree name should consist of alphabets, and spaces. Your entry: {deg_name}"}
    level_pattern = r"^[A-Za-z\s.]+$"
    if not re.match(level_pattern, level):
        return {"error": f"Level should consist of alphabets, spaces, and period. Your entry: {level}"}

    cur.execute("""
    SELECT *
    FROM degree
    WHERE name = %s AND level = %s;
    """, (deg_name, level))
    check_d = cur.fetchone()
    cur.fetchall()
    # Define standard evaluation methods

    if check_d is None:
        cur.execute("""
      INSERT INTO degree (name, level)
      VALUES (%s, %s);
                """, (deg_name, level))
        context.db.commit()
        print(f'{deg_name},{level} inserted successfully')
        return {"message": f"{deg_name},{level} inserted successfully"}
    else:
        print(f'{deg_name},{level} currently exists')
        return {"error": f"{deg_name},{level} currently exists"}


def enter_course(cur, course_name: str, course_id: str):
    """
    Inserts a new course into the database.

    Args:
        cur (mysql.connector.cursor): Cursor object to execute SQL queries.
        course_name (str): Name of the course.
        course_id (str): Unique identifier for the course.

    Returns:
        dict: Success or error message based on the operation.
    """
    # Data is already stripped when submitted.
    # Valid course_id format: 2-4 characters + 4-digit numbers
    course_name = course_name.title()
    course_name_pattern = r'^[A-Za-z\s\-]+[0-9]*$'
    if not re.match(course_name_pattern, course_name):
        return {"error": f"Course Name only allows alphabets, spaces, digits, and hyphens: {course_id}"}

    course_id = course_id.upper()
    course_id_pattern = r"^[A-Z]{2,4}\d{4}$"
    if not re.match(course_id_pattern, course_id):
        return {"error": f"course_id must be 2-4 uppercase letters followed by 4 digits., your_entry: {course_id}"}

    cur.execute("""
    SELECT *
    FROM course
    WHERE course_id = %s;
    """, (course_id,))
    check_c = cur.fetchone()

    if check_c is None:
        cur.execute("""
      INSERT INTO course (name, course_id)
      VALUES (%s, %s);
                """, (course_name, course_id))
        context.db.commit()

        print(f'{course_name},{course_id} inserted successfully')
        return {"message": f"{course_name},{course_id} inserted successfully"}
    else:
        print(f'{course_name},{course_id} currently exists')
        return {"error": f"{course_name},{course_id} currently exists"}


def enter_goal(cur, deg_name: str, level, goal_code, description):
    """
    Inserts a new goal into the database.

    Args:
        cur (mysql.connector.cursor): Cursor object to execute SQL queries.
        deg_name (str): Name of the degree.
        level (str): Level of the degree.
        goal_code (str): Unique code for the goal.
        description (str): Description of the goal.

    Returns:
        dict: Success or error message based on the operation.
    """
    # Degree name do not allow special characters
    deg_name = deg_name.title()
    deg_name_pattern = r'^[A-Za-z\s]+$'
    if not re.match(deg_name_pattern, deg_name):
        return {"error": f"Degree name should consist of alphabets, and spaces. Your entry: {deg_name}"}

    level_pattern = r"^[A-Za-z\s.]+$"
    if not re.match(level_pattern, level):
        return {"error": f"Level should consist of alphabets, spaces, and period. Your entry: {level}"}
    # goal_code: all upper case. ex) COMP
    # Valid goal_code format: 4-character string
    goal_code_pattern = r"^[A-Z0-9]{4}$"
    if not re.match(goal_code_pattern, goal_code):
        return {"error": f"goal_code must be an 4-character alphanumeric string. Your entry: {goal_code}"}
    description_pattern = r'^[A-Za-z\s\-]+$'
    if not re.match(description_pattern, description):
        return {"error": f"Description should consist of alphabets, hyphen, and spaces. Your entry: {description}"}
    cur.execute("""
    SELECT *
    FROM goal
    WHERE degree_name = %s AND level = %s AND goal_code = %s;
              """, (deg_name, level, goal_code))
    check_g = cur.fetchall()

    if not check_g:
        try:
            cur.execute("""
        INSERT INTO goal (degree_name, level, goal_code, description)
        VALUES (%s, %s, %s, %s);
                    """, (deg_name, level, goal_code, description))
            context.db.commit()
            print(
                f"{goal_code},{deg_name},{level},{description} inserted successfully")
            return {"message": f"{goal_code}, {deg_name}, {level}, {description} inserted successfully."}
        except mysql.connector.Error as e:
            return {"error": f"{str(e)}"}
    else:
        print(f"{goal_code},{deg_name},{level},{description} currently exists")
        return {"error": f"{goal_code},{deg_name},{level},{description} currently exists"}


def enter_degree_course(cur, deg_name, level, course_id, is_core: False):
    """
    Inserts a relationship between a degree and a course into the `deg_course` table.

    Args:
        cur (mysql.connector.cursor): The cursor object used to execute SQL queries.
        deg_name (str): The name of the degree (e.g., "Computer Science").
        level (str): The level of the degree (e.g., "BS", "MS").
        course_id (str): The unique identifier for the course (e.g., "CSCI1010").
        is_core (bool): Indicates whether the course is a core course for the degree. Defaults to False.

    Returns:
        dict: A dictionary containing a success or error message.

    Validation Steps:
        1. Validates that `course_id` follows the format of 2-4 uppercase letters followed by 4 digits.
        2. Confirms that the degree has associated goals before linking the course.
        3. Ensures that the relationship does not already exist in the `deg_course` table.

    Raises:
        mysql.connector.Error: If a database error occurs during the insertion.

    Example:
        >>> enter_degree_course(cur, "Computer Science", "BS", "CSCI1010", True)
        {"message": "Computer Science, BS, CSCI1010, True inserted successfully."}
    """
    # Valid course_id: 2-4 letter + 4-digit numbers
    course_id = course_id.upper()
    course_id_pattern = r"^[A-Z]{2,4}\d{4}$"
    if not re.match(course_id_pattern, course_id):
        return {"error": f"course_id must be 2-4 uppercase letters followed by 4 digits. Your entry: {course_id}"}

    cur.execute("""
    SELECT *
    FROM goal
    WHERE degree_name = %s AND level = %s;
                """, (deg_name, level))
    check_g = cur.fetchone()
    cur.fetchall()
    if check_g is None:
        print(f"No goals associated with {deg_name} {level}")
        return {"error": f"No goals associated with {deg_name} {level}"}

    cur.execute("""
    SELECT *
    FROM deg_course
    WHERE degree_name = %s AND level = %s AND course_id = %s;
                """, (deg_name, level, course_id))
    check_dc = cur.fetchall()

    if check_dc:
        print(f"{deg_name},{level},{level},{course_id} currently exists")
        return {"error": f"{deg_name},{level},{level},{course_id} currently exists"}
    else:
        try:
            cur.execute("""
        INSERT INTO deg_course (degree_name, level, course_id, Is_Core)
        VALUES (%s, %s, %s, %s);
                    """, (deg_name, level, course_id, is_core))
            context.db.commit()
            print(f"{deg_name},{level},{course_id},{is_core} inserted successfully")
            return {"message": f"{deg_name}, {level}, {course_id}, {is_core} inserted successfully."}
        except mysql.connector.Error as e:
            return {"error": f"{str(e)}"}


def enter_section(cur, sec_id, year, semester, course_id, ins_id, num_std):
    """
    Inserts a new section into the `section` table.

    Args:
        cur (mysql.connector.cursor): The cursor object used to execute SQL queries.
        sec_id (str): The section ID (3-digit number).
        year (int): The year the section is offered.
        semester (str): The semester the section is offered (e.g., "Spring", "Summer", "Fall").
        course_id (str): The unique identifier for the course (2-4 letters + 4 digits).
        ins_id (str): The instructor's unique 8-character alphanumeric ID.
        num_std (int): The number of students enrolled in the section.

    Returns:
        dict: A success message if the section is inserted, or an error message if validation fails
        or if the section already exists.

    Validation:
        - Ensures `sec_id` is a 3-digit number.
        - Validates `course_id` format (2-4 uppercase letters followed by 4 digits).
        - Checks that `ins_id` is an 8-character alphanumeric string.
        - Prevents duplicate entries for the same section.
    """
    # Validate formats: 3-digit numbers
    sec_id_pattern = r"^\d{3}$"
    if not re.match(sec_id_pattern, sec_id):
        return {"error": f"sec_id must be 3-digit numbers. your_entry: {sec_id}"}
    # Valid course_id: 2-4 letter + 4-digit numbers
    course_id = course_id.upper()
    course_id_pattern = r"^[A-Z]{2,4}\d{4}$"
    if not re.match(course_id_pattern, course_id):
        return {"error": f"course_id must be 2-4 uppercase letters followed by 4 digits. Your entry: {course_id}"}
    # Valid ins_id: 8-character string
    ins_id_pattern = r"^[a-zA-Z0-9]{8}$"
    if not re.match(ins_id_pattern, ins_id):
        return {"error": f"ins_id must be an 8-character alphanumeric string. Your entry: {ins_id}"}

    cur.execute("""
    SELECT *
    FROM section
    WHERE sec_id = %s AND year = %s AND semester = %s AND course_id = %s;
    """, (sec_id, year, semester, course_id))
    check_s = cur.fetchone()
    if check_s is not None:
        print(
            f"{sec_id}, {course_id}, {semester} {year} currently exists.")
        return {"error": f"{sec_id}, {course_id}, {semester} {year} currently exists."}
    else:
        try:
            cur.execute("""
        INSERT INTO section (sec_id, year, semester, course_id, ins_id, num_student)
        VALUES (%s, %s, %s, %s, %s, %s);
        """, (sec_id, year, semester, course_id, ins_id, num_std))
            context.db.commit()
            print(
                f"{sec_id},{course_id}, {semester} {year} inserted successfully.")
            return {"message": f"{sec_id},{course_id}, {semester} {year} inserted successfully."}
        except mysql.connector.Error as e:
            return {"error": f"{str(e)}"}


def enter_instructor(cur, name, ins_id):
    """
    Inserts a new instructor into the `instructor` table.

    Args:
        cur (mysql.connector.cursor): The cursor object used to execute SQL queries.
        name (str): The name of the instructor (alphabets, spaces, and optional hyphens allowed).
        ins_id (str): The unique 8-character alphanumeric identifier for the instructor.

    Returns:
        dict: A success message if the instructor is inserted, or an error message if validation fails
        or if the instructor already exists.

    Validation:
        - Ensures `name` contains only alphabets, spaces, and optional hyphens.
        - Prevents duplicate entries for the same `ins_id`.
    """
    name = name.title()
    ins_name_pattern = r'^[A-Za-z\s\-]+$'
    if not re.match(ins_name_pattern, name):
        return {"error": f"Name should be alphabets, spaces, and optional hyphens: {name}"}

    cur.execute("""
      SELECT *
      FROM instructor
      WHERE ins_id = %s
                """, (ins_id,))
    check_i = cur.fetchone()
    if check_i is not None:
        print(
            f"{name}, {ins_id} currently exists.")
        return {"error": f"{name}, {ins_id} currently exists."}
    else:
        try:
            cur.execute("""
        INSERT INTO instructor (name, ins_id)
        VALUES (%s, %s);
                    """, (name, ins_id))
            context.db.commit()
            print(
                f"{name}, {ins_id} inserted successfully.")
            return {"message": f"{name}, {ins_id} inserted successfully."}
        except mysql.connector.Error as e:
            return {"error": f"{str(e)}"}


def enter_evaluation(cur, sec_id, semester, year, course_id, goal_code, deg_name, level, grade_a, grade_b, grade_c, grade_f, improvement: str, measure_type: str):
    """
            Inserts an evaluation record into the `evaluation` table.

            Validation:
            - Ensures `improvement` contains only alphabets, spaces, and hyphens.
            - Validates that the total number of students (grades entered) matches the actual number of students in the section.
            - Prevents insertion if the section record does not exist.

            Raises:
            mysql.connector.Error: If a database error occurs during the insertion.
        """
    improvement_pattern = r'^[A-Za-z\s\-]+$'
    if not re.match(improvement_pattern, improvement):
        return {"error": f"Improvement should consist of alphabets, hyphen, and spaces. Your entry: {improvement}"}
    measure_type = measure_type.strip().title()
    # Fetch the number of students
    cur.execute("""
         SELECT num_student
         FROM section
         WHERE sec_id = %s AND semester = %s AND year = %s AND course_id = %s;
                """, (sec_id, semester, year, course_id))

    check_s = cur.fetchone()
    if check_s is not None:
        num_student = check_s[0]
        num_entered = sum([int(grade_a or 0), int(grade_b or 0),
                           int(grade_c or 0), int(grade_f or 0)])
    else:
        return {"error": f"You don't have a record for {sec_id}, {semester},{year},{course_id}"}
    # Enforcing the grade counts not to exceed the number of students in the section.
    if num_student != num_entered:
        print(
            f"The numbers entered({num_entered}) do not match the total number of students{num_student}")
        return {"error": f"The numbers entered({num_entered}) do not match the total number of students{num_student}"}
    try:
        cur.execute("""
        INSERT INTO evaluation (sec_id, semester, year, course_id, goal_code, degree_name, level, improvement, grade_a, grade_b, grade_c, grade_f, measure_type)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                """, (sec_id, semester, year, course_id, goal_code, deg_name, level, improvement, int(grade_a), int(grade_b), int(grade_c), int(grade_f), measure_type))

    except mysql.connector.Error as e:
        return {"error": f"Database Error: {str(e)}"}
    print(
        f"evaluation for {deg_name},{level}, {goal_code} {sec_id}, {semester} {year}, {course_id}  inserted successfully.")
    context.db.commit()
    return {"message": f"evaluation for {deg_name},{level}, {goal_code} {sec_id}, {semester} {year}, {course_id} inserted successfully."}


def update_evaluation(cur, sec_id, semester, year, course_id, goal_code, deg_name, level, **update_values):
    """
    Updates an existing evaluation record in the `evaluation` table.

    Args:
        **update_values: Dictionary of fields to update, including:
            - grade_a (int): Updated number of students achieving grade A.
            - grade_b (int): Updated number of students achieving grade B.
            - grade_c (int): Updated number of students achieving grade C.
            - grade_f (int): Updated number of students achieving grade F.
            - improvement (str): Updated suggestions for improving goal achievement.
            - measure_type (str): Updated evaluation measure type (e.g., "Quiz", "Project").

    Returns:
        dict: A success message if the evaluation is updated, or an error message if validation fails.

    Validation:
        - Ensures `improvement` contains only alphabets, spaces, and hyphens.
        - Validates that the total number of grades entered matches the number of students in the section.
        - Uses a stored procedure (`update_evaluations`) to apply updates.

    Raises:
        Exception: If a database error occurs during the update process, changes are rolled back.
    """
    cur.execute("""
         SELECT num_student
         FROM section
         WHERE sec_id = %s AND semester = %s AND year = %s AND course_id = %s;
                """, (sec_id, semester, year, course_id))

    check_s = cur.fetchone()
    num_student = check_s[0]
    num_entered = sum([update_values.get('grade_a', 0), update_values.get('grade_b', 0),
                      update_values.get('grade_c', 0), update_values.get('grade_f', 0)])
    improvement = update_values.get(
        'improvement', None)
    improvement_pattern = r'^[A-Za-z\s\-]+$'
    if not re.match(improvement_pattern, improvement):
        return {"error": f"Improvement should consist of alphabets, hyphen, and spaces. Your entry: {improvement}"}
    # Enforcing the grade counts not to exceed the number of students in the section.
    if num_student != num_entered:
        print(
            f"The numbers entered({num_entered}) do not match the total number of students{num_student}")
        return {"error": f"The numbers entered({num_entered}) do not match the total number of students{num_student}"}

    try:

        cur.callproc('update_evaluations', [
            sec_id,
            semester,
            year,
            course_id,
            deg_name,
            level,
            goal_code,
            update_values.get(
                'improvement', None),
            update_values.get('grade_a', 0),
            update_values.get('grade_b', 0),
            update_values.get('grade_c', 0),
            update_values.get('grade_f', 0),
            update_values.get(
                'measure_type'),
        ]
        )
        context.db.commit()
        return {"message": "Evaluation updated successfully."}
    except Exception as e:
        print(f"An error occurred: {e}")
        context.db.rollback()  # Rollback in case of an error
        return {"error": str(e)}
