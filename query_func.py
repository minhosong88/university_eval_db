
def return_associated_course(cur, degree, level):
    """
    This function intends to return all courses provided by different levels of the given degree.
    """
    cur.execute("""
      SELECT course_id, is_core, degree_name, level
      FROM deg_course
      WHERE degree_name = %s AND level = %s;
              """, (degree, level))
    course_info = cur.fetchall()

    return course_info


def return_all_sections_per_degree(cur, degree, level, begin, end):
    """
    This function intends to return all sections provided by different levels of the given degree.
    """
    cur.execute("""
      SELECT s.sec_id, s.course_id, dc.degree_name, dc.level, s.year, s.semester
      FROM deg_course dc JOIN section s ON dc.course_id = s.course_id
      WHERE dc.degree_name = %s AND dc.level = %s
        AND s.year BETWEEN %s AND %s 
      ORDER BY s.year DESC, (CASE WHEN s.semester ='Spring' THEN 1
        WHEN s.semester = 'Summer' THEN 2
        WHEN s.semester = 'Fall' THEN 3 END);            
              """, (degree, level,  begin, end))
    section_info = cur.fetchall()

    return section_info


def return_all_goals(cur, degree, level):
    """
    This function intends to return all goals associated with different levels of the given degree.
    """
    cur.execute("""
      SELECT g.goal_code, g.description, g.degree_name, g.level
      FROM goal g
      WHERE g.degree_name = %s AND g.level = %s
      ORDER BY g.level, g.goal_code;        
              """, (degree, level))
    goal_info = cur.fetchall()

    return goal_info


def return_courses_with_goals(cur, degree, level):
    """
    This function intends to return all goals and courses associated with different levels of the given degree.
    """
    cur.execute("""
      SELECT g.goal_code, g.description, dc.course_id, dc.degree_name, dc.level
      FROM deg_course dc JOIN goal g ON dc.degree_name = g.degree_name 
      WHERE g.degree_name = %s AND g.level = %s AND dc.level = %s
      ORDER BY dc.level AND g.goal_code;
              """, (degree, level, level))
    course_goal_info = cur.fetchall()

    return course_goal_info


def return_all_section_per_course(cur, course, begin_year, end_year, begin_semester, end_semester):
    cur.execute("""
        SELECT s.sec_id, s.course_id, s.year, s.semester
        FROM section s JOIN course c ON c.course_id = s.course_id
        WHERE c.course_id = %s
        AND s.year BETWEEN %s AND %s
        ORDER BY s.year, (
        CASE 
            WHEN s.semester = 'Spring' THEN 1
            WHEN s.semester = 'Summer' THEN 2
            WHEN s.semester = 'Fall' THEN 3
        END
        );
              """, (course, begin_year, end_year))
    all_section_per_course_info = cur.fetchall()
    mapping = {"Spring": 1, "Summer": 2, "Fall": 3}
    begin_s = mapping.get(begin_semester)
    end_s = mapping.get(end_semester)
    filtered_section = []
    for sec_id, course_id, year, semester in all_section_per_course_info:
        given_s = mapping.get(semester)
        if ((year == int(begin_year) and given_s >= int(begin_s)) or (year == end_year and given_s <= int(end_s)) or (year > int(begin_year) or year < int(end_year))):

            filtered_section.append((sec_id, course_id, year, semester))

    return filtered_section


def return_all_sections_per_instructor(cur, ins_id, begin_year, end_year, begin_semester, end_semester):

    cur.execute("""
      SELECT s.sec_id, s.course_id, s.year, s.semester
      FROM section s 
      JOIN instructor i ON s.ins_id = i.ins_id
      JOIN course c ON s.course_id = c.course_id  
      WHERE i.ins_id = %s
        AND s.year BETWEEN %s AND %s
        ORDER BY s.year, (
        CASE 
            WHEN s.semester = 'Spring' THEN 1
            WHEN s.semester = 'Summer' THEN 2
            WHEN s.semester = 'Fall' THEN 3
        END
        );
              """, (ins_id, begin_year, end_year))
    all_section_per_ins_info = cur.fetchall()
    mapping = {"Spring": 1, "Summer": 2, "Fall": 3}
    begin_s = mapping.get(begin_semester)
    end_s = mapping.get(end_semester)
    filtered_section = []
    for sec_id, course_id, year, semester in all_section_per_ins_info:
        given_s = mapping.get(semester)
        if ((year == int(begin_year) and given_s >= int(begin_s)) or (year == end_year and given_s <= int(end_s)) or (year > int(begin_year) or year < int(end_year))):

            filtered_section.append((sec_id, course_id, year, semester))

    return filtered_section

    return all_section_per_ins_info


def check_evaluation_status(cur, year, semester, ins_id):
    cur.execute("""
    SELECT DISTINCT s.course_id, s.sec_id, s.year, s.semester, dc.degree_name, dc.level, e.improvement, e.grade_a, e.grade_b, e.grade_c, e.grade_f,e.measure_type
    FROM section s
    JOIN deg_course dc ON s.course_id = dc.course_id
    JOIN goal g ON dc.degree_name = g.degree_name AND dc.level = g.level
    LEFT JOIN evaluation e 
      ON s.sec_id = e.sec_id AND s.year = e.year AND s.semester = e.semester
         AND e.degree_name = dc.degree_name AND e.level = dc.level AND s.course_id = e.course_id
    WHERE s.semester = %s AND s.year = %s AND s.ins_id = %s;
    """, (semester, year, ins_id))
    evaluation_info = cur.fetchall()

    # Initialize the results
    section_status = []

    # Iterate evaluation info
    for course_id, sec_id, year, semester, degree_name, level, improvement, grade_a, grade_b, grade_c, grade_f, measure_type in evaluation_info:

        # Initialize the missing fields
        missing_field = []

        # Add improvement in the missing field if improvement is NULL
        if not improvement:
            missing_field.append("improvement")

        # Add grade and its counts if grade counts is NULL
        grades = {
            'grade_a': grade_a,
            'grade_b': grade_b,
            'grade_c': grade_c,
            'grade_f': grade_f,
        }
        print(grades)
        for grade_name, grade_count in grades.items():
            if grade_count is None:
                missing_field.append(grade_name)
        print(missing_field)
        # Check the missing field by counting the number of missing field
        if len(missing_field) == 5:  # all fileds are missing
            status = "evaluation Not Entered"
        elif len(missing_field) <= 4 and len(missing_field) > 0:  # some are missing
            status = "evaluation Partially Entered"
        elif len(missing_field) == 0:  # no missing field
            status = "evaluation Fully Entered"

            # Append section and degree-specific status
        section_status.append({
            "course_id": course_id,
            "sec_id": sec_id,
            "year": year,
            "semester": semester,
            "degree_name": degree_name,
            "level": level,
            "status": status,
            "missing_fields": missing_field,
            "improvement": improvement,
            "grade_a": grade_a,
            "grade_b": grade_b,
            "grade_c": grade_c,
            "grade_f": grade_f,
            "measure_type": measure_type,
        })

    return section_status


def return_sections_over_percentage(cur, year: int, semester, percentage: int):
    cur.execute("""
      SELECT DISTINCT s.sec_id, s.course_id, s.year, s.semester, s.Num_Student, ((e.grade_a + e.grade_b + e.grade_c) / NULLIF((e.grade_a + e.grade_b + e.grade_c + e.grade_f), 0)) * 100 AS Non_F_Percentage
      FROM evaluation e JOIN section s ON e.sec_id = s.sec_id
        AND e.year = s.year
        AND e.semester = s.semester
      WHERE e.year = %s AND e.semester = %s
      Having Non_F_Percentage >= %s; 
               """, (year, semester, percentage))

    section_over_percentage_info = cur.fetchall()
    return section_over_percentage_info


def get_degrees(cur):
    cur.execute("SELECT CONCAT(name, ' , ', level) FROM degree;")
    all_degrees = cur.fetchall()
    all_degrees_to_list = [row[0] for row in all_degrees]
    return all_degrees_to_list if all_degrees_to_list else ["No Degrees"]


def get_courses(cur):
    cur.execute("SELECT CONCAT(course_id, ' , ', name) FROM course;")
    all_courses = cur.fetchall()
    all_courses_to_list = [row[0] for row in all_courses]
    return all_courses_to_list if all_courses_to_list else ["No Courses"]


def get_instructors(cur):
    cur.execute("SELECT CONCAT(ins_id, ' , ', name) FROM instructor")
    all_instructors = cur.fetchall()
    all_instructors_to_list = [row[0] for row in all_instructors]
    return all_instructors_to_list if all_instructors_to_list else ["No Instructor"]


def get_section_info(cur):
    cur.execute("SELECT sec_id, year, semester, course_id FROM section")
    all_sections = cur.fetchall()
    return all_sections if all_sections else [("No sec_id", "No Year", "No Semester", "No Course")]


def get_degree_info(cur):
    cur.execute("""
        SELECT name, level
        FROM degree     
                """)
    degree_info = cur.fetchall()
    return degree_info if degree_info else [("No degree Name", "No Level")]


def get_degree_goal_info(cur):
    cur.execute("""
        SELECT d.name, d.level, g.goal_code
        FROM degree d JOIN goal g on d.name = g.degree_name AND d.level = g.level     
                """)
    degree_info = cur.fetchall()
    return degree_info if degree_info else [("No degree Name", "No Level", "No Goal")]


def get_evaluation_info(cur):
    cur.execute("""
        SELECT *
        FROM evaluation
        WHERE        
                
                """)


def get_source_evaluation(cur, sec_id, semester, year, course_id):
    cur.execute("""
    SELECT improvement, grade_a, grade_b, grade_c, grade_f, measure_type
    FROM evaluation
    WHERE sec_id = %s AND semester = %s AND year = %s
      AND course_id = %s;
    """, (sec_id, semester, year, course_id))

    source_evaluation = cur.fetchone()
    if source_evaluation is None:
        print(
            f"No other evaluation found for {course_id}-{sec_id}-{year}-{semester}.")
        return {"error": "Source evaluation not found"}
    return source_evaluation
