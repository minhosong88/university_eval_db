# --------------------------------------------
#  Query Search
#     Builds the window for Query Search
# --------------------------------------------
from tkinter import messagebox
from query_func import get_instructors, return_all_goals, return_all_section_per_course, return_all_sections_per_degree, return_all_sections_per_instructor, return_associated_course, return_courses_with_goals, get_courses, get_degrees
from context import context
from tkinter import *

tracker = 'empty'


def reset():
    global canvas
    global tracker
    tracker = 'empty'
    canvas.destroy()


def query_search():
    rootData = Tk()
    rootData.geometry("1100x400")
    canvas = Canvas(rootData)
    canvas.pack(side='right', fill="both", expand=True)

    def initializer():
        global canvas
        canvas = Canvas(rootData)
        canvas.pack(side='right', fill="both", expand=True)

        cg_search = Button(
            canvas, text="Course and Goal search", command=course_goal_query)
        cg_search.grid(
            row=0, column=0, padx=10, pady=10)
        sec_search = Button(canvas, text="Section search",
                            command=section_query)
        sec_search.grid(
            row=0, column=1, padx=10, pady=10)

    def course_goal_query():
        global tracker
        if tracker != 'course_goal' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'course_goal'

        cg_query_window = Tk()
        cg_query_window.geometry("800x400")
        window_l = Label(
            cg_query_window, text="Course and Goal search", width=18)
        window_l.grid(row=0, column=1, pady=10)

        # Dropdown menu for degree
        all_degrees = get_degrees(context.cursor)

        degree_l = Label(cg_query_window, text='Degree', anchor="e", width=18)
        degree_l.grid(row=1, column=1)
        selected_degree = StringVar(cg_query_window, value="")
        degree_dropdown = OptionMenu(
            cg_query_window, selected_degree, *all_degrees)
        degree_dropdown.grid(row=1, column=2)
        # Functions

        def search_courses(degree):
            if not degree:
                messagebox.showwarning(
                    "Input Error", "Degree Not Selected")
                return
            # Extract the degree name from concatenation before query
            name, level = degree.split(',')
            name = name.strip()
            level = level.strip()
            courses = return_associated_course(context.cursor, name, level)
            if courses:
                display_courses(courses)
            else:
                messagebox.showinfo("No Results", "No Courses Found")

        def display_courses(courses):
            courses_window = Toplevel()
            courses_window.title("Courses Associated With Degree")
            courses_window.geometry("600x400")

            # Create Header Row
            columns = ["Course_ID", "Is_Core", "Degree_name",
                       "Level"]
            for col, header in enumerate(columns):
                Label(courses_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(courses):
                course_id, is_core, degree_name, level = row
                is_core = "Y" if is_core else "N"
                Label(courses_window, text=f"{course_id}").grid(
                    row=i + 1, column=0)
                Label(courses_window, text=f"{is_core}").grid(
                    row=i + 1, column=1)
                Label(
                    courses_window, text=f"{degree_name}").grid(row=i + 1, column=2)
                Label(courses_window, text=f"{level}").grid(
                    row=i + 1, column=3)

        def search_goals(degree):
            if not degree:
                messagebox.showwarning("Input Error", "Degree Not Selected")
                return
            # Extract the degree name from concatenation before query
            name, level = degree.split(',')
            name = name.strip()
            level = level.strip()
            goals = return_all_goals(context.cursor, name, level)
            if goals:
                display_goals(goals)
            else:
                messagebox.showinfo("No Results", "No Goals Found")

        def display_goals(goals):
            goals_window = Toplevel()
            goals_window.title("Goals Associated With Degree")
            goals_window.geometry("600x400")

            # Create Header Row
            columns = ["Goal Code", "Description", "Degree_name",
                       "Level"]
            for col, header in enumerate(columns):
                Label(goals_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(goals):
                goal_code, description, degree_name, level = row
                Label(goals_window, text=f"{goal_code}").grid(
                    row=i + 1, column=0)
                Label(goals_window, text=f"{description}").grid(
                    row=i + 1, column=1)
                Label(
                    goals_window, text=f"{degree_name}").grid(row=i + 1, column=2)
                Label(goals_window, text=f"{level}").grid(
                    row=i + 1, column=3)

        def search_goal_course(degree):
            if not degree:
                messagebox.showwarning("Input Error", "Degree Not Selected")
                return
            # Extract the degree name from concatenation before query
            name, level = degree.split(',')
            name = name.strip()
            level = level.strip()
            goal_courses = return_courses_with_goals(
                context.cursor, name, level)
            if goal_courses:
                display_goal_course(goal_courses)
            else:
                messagebox.showinfo(
                    "No Results", "No Goals with Courses Found")

        def display_goal_course(goal_courses):
            goal_courses_window = Toplevel()
            goal_courses_window.title(
                "Courses and Goals Associated With Degree")
            goal_courses_window.geometry("600x400")

            # Create Header Row
            columns = ["Goal Code", "Description",
                       "Course_ID", "Degree Name", "Level"]
            for col, header in enumerate(columns):
                Label(goal_courses_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(goal_courses):
                goal_code, description, course_id, degree_name, level = row
                Label(goal_courses_window, text=f"{goal_code}").grid(
                    row=i + 1, column=0)
                Label(goal_courses_window, text=f"{description}").grid(
                    row=i + 1, column=1)
                Label(
                    goal_courses_window, text=f"{course_id}").grid(row=i + 1, column=2)
                Label(goal_courses_window, text=f"{degree_name}").grid(
                    row=i + 1, column=3)
                Label(goal_courses_window, text=f"{level}").grid(
                    row=i + 1, column=4)

        # Three buttons for each query
        Button(cg_query_window, text="Search Courses", command=lambda: search_courses(
            selected_degree.get())).grid(row=4, column=0)
        Button(cg_query_window, text="Search Goals", command=lambda: search_goals(
            selected_degree.get())).grid(row=4, column=1)
        Button(cg_query_window, text="Search Goals and Courses",
               command=lambda: search_goal_course(selected_degree.get())).grid(row=4, column=2)

    def section_query():
        global tracker
        if tracker != 'section' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'section'

        s_query_window = Tk()
        s_query_window.geometry("1400x400")
        window_l = Label(
            s_query_window, text="Section search", width=18)
        window_l.grid(row=0, column=1, pady=10)

        # Compartment for 'By Degree Search'
        degree_compartment = LabelFrame(
            s_query_window, text="Search by Degree", padx=10, pady=10)
        degree_compartment.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        degree_compartment_l = Label(degree_compartment, text="Degree")
        degree_compartment_l.grid(row=0, column=0, padx=5, pady=5)
        # Dropdown menu for degree
        all_degrees = get_degrees(context.cursor)
        degree_l = Label(degree_compartment, text='Degree',
                         anchor="e", width=18)
        degree_l.grid(row=0, column=1)
        selected_degree = StringVar(degree_compartment, value="")
        degree_dropdown = OptionMenu(
            degree_compartment, selected_degree, *all_degrees)
        degree_dropdown.grid(row=1, column=2)
        # Begin year
        year_begin_l = Label(degree_compartment, text="Year Begin")
        year_begin_l.grid(row=1, column=0, padx=5, pady=5)
        year_begin_e = Entry(degree_compartment, width=8)
        year_begin_e.grid(row=1, column=1, padx=5, pady=5)
        # End year
        year_end_l = Label(degree_compartment, text="Year End")
        year_end_l.grid(row=2, column=0, padx=5, pady=5)
        year_end_e = Entry(degree_compartment, width=8)
        year_end_e.grid(row=2, column=1, padx=5, pady=5)

        def search_by_degree(degree, begin, end):
            if not all([degree, begin, end]):
                return messagebox.showinfo("No Entry", "All field must be filled")
            name, level = degree.split(',')
            name = name.strip()
            level = level.strip()
            sections = return_all_sections_per_degree(
                context.cursor, name, level, begin, end)
            if sections:
                display_sections_by_degree(sections)
            else:
                messagebox.showinfo("No Results", "No Sections Found")

        def display_sections_by_degree(sections):
            sections_window = Toplevel()
            sections_window.title("Sections by Degree")
            sections_window.geometry("600x400")

            # Create Header Row
            columns = ["Section ID", "Course ID",
                       "Degree Name", "Level", "Year", "Semester"]
            for col, header in enumerate(columns):
                Label(sections_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(sections):
                sec_id, course_id, degree_name, level, year, semester = row
                Label(sections_window, text=f"{sec_id}").grid(
                    row=i + 1, column=0)
                Label(sections_window, text=f"{course_id}").grid(
                    row=i + 1, column=1)
                Label(
                    sections_window, text=f"{degree_name}").grid(row=i + 1, column=2)
                Label(sections_window, text=f"{level}").grid(
                    row=i + 1, column=3)
                Label(sections_window, text=f"{year}").grid(
                    row=i + 1, column=4)
                Label(sections_window, text=f"{semester}").grid(
                    row=i + 1, column=5)
        # Button for Search by Degree
        Button(degree_compartment, text="Search", command=lambda: search_by_degree(
            selected_degree.get(), year_begin_e.get(), year_end_e.get())).grid(row=3, column=1, pady=5)

        # Compartment for 'By Course Search'
        course_compartment = LabelFrame(
            s_query_window, text="Search by Course", padx=10, pady=10)
        course_compartment.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        Label(course_compartment, text="Course").grid(
            row=0, column=0, padx=5, pady=5)
        # Returns a list of course ids
        all_courses = get_courses(context.cursor)
        selected_course = StringVar(course_compartment, value="")
        course_dropdown = OptionMenu(
            course_compartment, selected_course, *all_courses)
        course_dropdown.grid(row=0, column=1, padx=5, pady=5)

        Label(course_compartment, text="Year Begin").grid(
            row=1, column=0, padx=5, pady=5)
        year_begin = Entry(course_compartment, width=10)
        year_begin.grid(row=1, column=1, padx=5, pady=5)

        Label(course_compartment, text="Year End").grid(
            row=2, column=0, padx=5, pady=5)
        year_end = Entry(course_compartment, width=10)
        year_end.grid(row=2, column=1, padx=5, pady=5)

        Label(course_compartment, text="Semester Begin").grid(
            row=3, column=0, padx=5, pady=5)
        semester_begin = StringVar(course_compartment, value="Spring")
        semester_dropdown_begin = OptionMenu(
            course_compartment, semester_begin, "Spring", "Summer", "Fall")
        semester_dropdown_begin.grid(row=3, column=1, padx=5, pady=5)

        Label(course_compartment, text="Semester End").grid(
            row=4, column=0, padx=5, pady=5)
        semester_end = StringVar(course_compartment, value="Fall")
        semester_dropdown_end = OptionMenu(
            course_compartment, semester_end, "Spring", "Summer", "Fall")
        semester_dropdown_end.grid(row=4, column=1, padx=5, pady=5)

        def search_by_course(course, begin_y, end_y, begin_s, end_s):
            if not all([course, begin_y, end_y, begin_s, end_s]):
                return messagebox.showinfo("No Entry", "All field must be filled")
            course_id, name = course.split(',')
            course_id = course_id.strip()
            sections = return_all_section_per_course(
                context.cursor, course_id, begin_y, end_y, begin_s, end_s)
            if sections:
                display_sections_by_courses(sections)
            else:
                messagebox.showinfo("No Results", "No Sections Found")

        def display_sections_by_courses(sections):
            sections_window = Toplevel()
            sections_window.title("Sections by Degree")
            sections_window.geometry("600x400")

            # Create Header Row
            columns = ["Section ID", "Course ID", "Year", "Semester"]
            for col, header in enumerate(columns):
                Label(sections_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(sections):
                sec_id, course_id, year, semester = row
                Label(sections_window, text=f"{sec_id}").grid(
                    row=i + 1, column=0)
                Label(sections_window, text=f"{course_id}").grid(
                    row=i + 1, column=1)
                Label(sections_window, text=f"{year}").grid(
                    row=i + 1, column=2)
                Label(sections_window, text=f"{semester}").grid(
                    row=i + 1, column=3)
        Button(course_compartment, text="Search", command=lambda: search_by_course(
            selected_course.get(), year_begin.get(), year_end.get(),
            semester_begin.get(), semester_end.get())).grid(row=5, column=1, pady=5)

        # Compartment for 'By Course Instructor'
        instructor_compartment = LabelFrame(
            s_query_window, text="Search by Instructor", padx=10, pady=10)
        instructor_compartment.grid(
            row=1, column=3, padx=10, pady=10, sticky="ew")

        Label(instructor_compartment, text="Instructor ").grid(
            row=0, column=0, padx=5, pady=5)

        # Returns a list of instructors
        all_instructors = get_instructors(context.cursor)
        selected_instructor = StringVar(instructor_compartment, value="")
        ins_dropdown = OptionMenu(
            instructor_compartment, selected_instructor, *all_instructors)
        ins_dropdown.grid(row=0, column=1, padx=5, pady=5)

        Label(instructor_compartment, text="Year Begin").grid(
            row=1, column=0, padx=5, pady=5)
        instructor_year_begin = Entry(instructor_compartment, width=10)
        instructor_year_begin.grid(row=1, column=1, padx=5, pady=5)

        Label(instructor_compartment, text="Year End").grid(
            row=2, column=0, padx=5, pady=5)
        instructor_year_end = Entry(instructor_compartment, width=10)
        instructor_year_end.grid(row=2, column=1, padx=5, pady=5)

        Label(instructor_compartment, text="Semester Begin").grid(
            row=3, column=0, padx=5, pady=5)
        instructor_semester_begin = StringVar(
            instructor_compartment, value="Spring")
        instructor_semester_dropdown_begin = OptionMenu(
            instructor_compartment, instructor_semester_begin, "Spring", "Summer", "Fall")
        instructor_semester_dropdown_begin.grid(
            row=3, column=1, padx=5, pady=5)

        Label(instructor_compartment, text="Semester End").grid(
            row=4, column=0, padx=5, pady=5)
        instructor_semester_end = StringVar(
            instructor_compartment, value="Fall")
        instructor_semester_dropdown_end = OptionMenu(
            instructor_compartment, instructor_semester_end, "Spring", "Summer", "Fall")
        instructor_semester_dropdown_end.grid(row=4, column=1, padx=5, pady=5)

        def search_by_instructor(instructor, begin_y, end_y, begin_s, end_s):
            if not all([instructor, begin_y, end_y, begin_s, end_s]):
                return messagebox.showinfo("No Entry", "All field must be filled")
            ins_id, name = instructor.split(',')
            ins_id = ins_id.strip()
            sections = return_all_sections_per_instructor(
                context.cursor, ins_id, begin_y, end_y, begin_s, end_s)
            if sections:
                display_sections_by_instructor(sections)
            else:
                messagebox.showinfo("No Results", "No Sections Found")

        def display_sections_by_instructor(sections):
            sections_window = Toplevel()
            sections_window.title("Sections by Degree")
            sections_window.geometry("600x400")

            # Create Header Row
            columns = ["Section ID", "Course ID", "Year", "Semester"]
            for col, header in enumerate(columns):
                Label(sections_window, text=header, font=(
                    "Arial", 10, "bold")).grid(row=0, column=col)

            # Populate Table with Data
            for i, row in enumerate(sections):
                sec_id, course_id, year, semester = row
                Label(sections_window, text=f"{sec_id}").grid(
                    row=i + 1, column=0)
                Label(sections_window, text=f"{course_id}").grid(
                    row=i + 1, column=1)
                Label(sections_window, text=f"{year}").grid(
                    row=i + 1, column=2)
                Label(sections_window, text=f"{semester}").grid(
                    row=i + 1, column=3)

        Button(instructor_compartment, text="Search", command=lambda: search_by_instructor(
            selected_instructor.get(), instructor_year_begin.get(), instructor_year_end.get(),
            instructor_semester_begin.get(), instructor_semester_end.get())).grid(row=5, column=1, pady=5)

    initializer()
