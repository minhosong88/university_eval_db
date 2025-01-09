
# --------------------------------------------
#  Data Entry
#     Builds the window for data entry
# --------------------------------------------

from data_manipulate_func import enter_degree, enter_course, enter_degree_course, enter_goal, enter_instructor, enter_section
from tkinter import messagebox
from context import context
from tkinter import *
from query_func import get_courses, get_degree_info, get_degrees

tracker = 'empty'

# Reset the canvas and traker state
def reset():
    """
    Resets the canvas and tracker state by destroying the current canvas.
    """
    global canvas
    global tracker
    tracker = 'empty'
    canvas.destroy()

# Main function to initialize the Data Entry GUI
def data_entry():
    """
    Launches the data entry gui window where users can add or manage degrees, courses, instructors, sections, and goals.
    """
    rootData = Tk()
    rootData.geometry("1400x500")
    canvas = Canvas(rootData)
    canvas.pack(side='right', fill="both", expand=True)

    def initializer():
        """
        Initializes the canvas with buttons for various data entry options.
        """
        global canvas
        canvas = Canvas(rootData)
        canvas.pack(side='right', fill="both", expand=True)
        # Buttons for different data entry options
        degree = Button(canvas, text='Degree',
                        command=add_degree, width=18)
        degree.grid(row=0, column=1)

        courses = Button(canvas, text='Courses',
                         command=add_course, width=18)
        courses.grid(row=0, column=2)

        instructors = Button(canvas, text='Instructors',
                             command=add_instructor, width=18)
        instructors.grid(row=0, column=3)

        sections = Button(canvas, text='Sections',
                          command=add_section, width=18)
        sections.grid(row=0, column=4)

        goals = Button(canvas, text='Goals', command=add_goal, width=18)
        goals.grid(row=0, column=5)

        deg_course = Button(canvas, text='Deg_Course',
                            command=add_deg_course, width=18)
        deg_course.grid(row=0, column=6)

    def add_degree():
        """
        Opens a form to input details for adding a new degree.
        """
        global canvas, tracker

        if tracker != 'degree' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'degree'

        # Label and Entry
        nameL = Label(canvas, text='Degree Name', anchor="e", width=18)
        nameL.grid(row=1, column=1)
        nameE = Entry(canvas)
        nameE.grid(row=1, column=2)

        standard_levels = ['BA', 'BS', 'MS', 'Ph.D.', 'Cert', 'New Level']
        selected_level = StringVar(canvas, value=standard_levels[0])
        level_dropdown = OptionMenu(canvas, selected_level, *standard_levels)
        level_label = Label(canvas, text='Degree Level', anchor="e", width=18)
        level_label.grid(row=2, column=1)
        level_dropdown.grid(row=2, column=2)

       # Optional New Level Entry
        new_level_l = Label(canvas, text='New Level', anchor="e", width=18)
        new_level_e = Entry(canvas)

        def show_new_level_field(*args):
            """
            Displays the input field for a custom degree level if 'New Level' is selected.
            """
            if selected_level.get() == 'New Level':
                new_level_l.grid(row=3, column=1)
                new_level_e.grid(row=3, column=2)
            else:
                new_level_l.grid_remove()
                new_level_e.grid_remove()

        selected_level.trace('w', show_new_level_field)

        # Submit button to save the degree
        def submit_degree():
            """
            Saves the entered degree details to the database.
            """
            degree_name = nameE.get().strip().title()
            degree_level = new_level_e.get().strip().title() if selected_level.get(
            ) == 'New Level' else selected_level.get()
            result = enter_degree(context.cursor, degree_name, degree_level)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
                reset()
                initializer()
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_degree()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_degree, width=18)
        submit.grid(row=10, column=3)

    def add_course():
        """
        Opens a form to input details for adding a new course.
        """
        global canvas, tracker
        if tracker != 'degree' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'course'

        # Label and Entry
        nameL = Label(canvas, text='Course Name', anchor="e", width=18)
        nameL.grid(row=1, column=1)
        nameE = Entry(canvas)
        nameE.grid(row=1, column=2)

        idL = Label(canvas, text='Course ID', anchor="e", width=18)
        idL.grid(row=2, column=1)
        idE = Entry(canvas)
        idE.grid(row=2, column=2)

        # Submit button to save course
        def submit_course():
            """
            Saves the entered course details to the database.
            """
            course_name = nameE.get().strip()
            course_id = idE.get().strip()
            result = enter_course(context.cursor, course_name, course_id)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
                reset()
                initializer()
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_course()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_course, width=18)
        submit.grid(row=10, column=3)

    def add_instructor():
        """
        Opens a form to input details for adding a new instructor.
        """
        global canvas, tracker
        if tracker != 'inst' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'inst'

        # Label and Entry
        f_name_l = Label(canvas, text='First Name', anchor="e", width=18)
        f_name_l.grid(row=1, column=1)
        l_name_l = Label(canvas, text='Last Name', anchor="e", width=18)
        l_name_l.grid(row=2, column=1)
        f_name_e = Entry(canvas)
        f_name_e.grid(row=1, column=2)
        l_name_e = Entry(canvas)
        l_name_e.grid(row=2, column=2)

        idL = Label(canvas, text='Instructors ID', anchor="e", width=18)
        idL.grid(row=3, column=1)
        idE = Entry(canvas)
        idE.grid(row=3, column=2)

        # Submit button to save instructor
        def submit_instructor():
            """
            Saves the entered course details to the database.
            """
            first_name = f_name_e.get().strip()
            last_name = l_name_e.get().strip()
            full_name = f"{first_name} {last_name}"
            ins_id = idE.get().strip()
            if not first_name or not last_name:
                messagebox.showerror(
                    "Error", "Both first and last names are required")
                return
            result = enter_instructor(context.cursor, full_name, ins_id)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_instructor()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_instructor, width=18)
        submit.grid(row=10, column=3)

    def add_section():
        """
        Opens a form to input details for adding a new section.
        """
        global canvas, tracker
        if tracker != 'sect' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'sect'

        # Label and Entry
        idL = Label(canvas, text='Section ID', anchor="e", width=18)
        idL.grid(row=1, column=1)
        idE = Entry(canvas)
        idE.grid(row=1, column=2)

        yearL = Label(canvas, text='Year', anchor="e", width=18)
        yearL.grid(row=2, column=1)
        yearE = Entry(canvas)
        yearE.grid(row=2, column=2)

        # Semester Dropdown
        semesters = ['Spring', 'Summer', 'Fall']
        selected_semester = StringVar(canvas, value=semesters[0])
        semester_dropdown = OptionMenu(canvas, selected_semester, *semesters)
        semester_label = Label(canvas, text='Semester', anchor="e", width=18)
        semester_label.grid(row=3, column=1)
        semester_dropdown.grid(row=3, column=2)

        courseIDL = Label(canvas, text='Course ID',
                          anchor="e", width=18)
        courseIDL.grid(row=4, column=1)
        courseIDE = Entry(canvas)
        courseIDE.grid(row=4, column=2)

        instIDL = Label(canvas, text='Instructors ID',
                        anchor="e", width=18)
        instIDL.grid(row=5, column=1)
        intsIDE = Entry(canvas)
        intsIDE.grid(row=5, column=2)

        numStL = Label(canvas, text='Number of Students',
                       anchor="e", width=18)
        numStL.grid(row=6, column=1)
        numStE = Entry(canvas)
        numStE.grid(row=6, column=2)

        # Submit button to save section
        def submit_section():
            sec_id = idE.get().strip()
            year = yearE.get().strip()
            semester = selected_semester.get()
            course_id = courseIDE.get().strip()
            ins_id = intsIDE.get()
            num_std = numStE.get()
            result = enter_section(context.cursor, sec_id, year, semester,
                                   course_id, ins_id, num_std)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
                reset()
                initializer()
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_section()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_section, width=18)
        submit.grid(row=10, column=3)

    def add_goal():
        """
        Opens a form to input details for adding a new goal.
        """
        global canvas, tracker
        if tracker != 'goal' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'goal'
        degree_info = get_degree_info(context.cursor)
        degree_name_list = set()
        level_list = set()
        for items in degree_info:
            name, level = items
            degree_name_list.add(name)
            level_list.add(level)

        # Label and Entry
        deg_nameL = Label(canvas, text='Degree Name', anchor="e", width=18)
        degree_name_list = list(degree_name_list)
        selected_degree_name = StringVar(canvas, value="")
        degree_name_dropdown = OptionMenu(
            canvas, selected_degree_name, *degree_name_list)
        deg_nameL.grid(row=1, column=1)
        degree_name_dropdown.grid(row=1, column=2)

        level_list = list(level_list)
        selected_level = StringVar(canvas, value="")
        level_dropdown = OptionMenu(canvas, selected_level, *level_list)
        level_label = Label(canvas, text='Degree Level', anchor="e", width=18)
        level_label.grid(row=3, column=1)
        level_dropdown.grid(row=3, column=2)

        goal_code_l = Label(canvas, text='Goal Code', anchor="e", width=18)
        goal_code_l.grid(row=2, column=1)
        goal_code_e = Entry(canvas)
        goal_code_e.grid(row=2, column=2)

        desL = Label(canvas, text='Goal Description', anchor="e", width=18)
        desL.grid(row=4, column=1)
        desE = Entry(canvas)
        desE.grid(row=4, column=2)

        # Submit button to save goal
        def submit_goal():
            degree_name = selected_degree_name.get().strip()
            level = selected_level.get().strip()
            goal_code = goal_code_e.get().strip().upper()
            description = desE.get().strip()
            result = enter_goal(context.cursor, degree_name,
                                level, goal_code, description)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
                reset()
                initializer()
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_goal()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_goal, width=18)
        submit.grid(row=10, column=3)

    def add_deg_course():
        """
        Opens a form to connect a degree with a course.
        """
        global canvas, tracker
        if tracker != 'deg_course' or tracker != 'empty':
            reset()
            initializer()
        tracker = 'deg_course'

        # Label and Entry
        all_degrees = get_degrees(context.cursor)
        all_courses = get_courses(context.cursor)
        is_core_values = ['True', 'False']

        degree_l = Label(canvas, text='Degree', anchor="e", width=18)
        degree_l.grid(row=1, column=1)
        selected_degree = StringVar(canvas, value="")
        degree_dropdown = OptionMenu(canvas, selected_degree, *all_degrees)
        degree_dropdown.grid(row=1, column=2)

        course_l = Label(canvas, text='Course', anchor="e", width=18)
        course_l.grid(row=2, column=1)
        selected_course = StringVar(canvas, value="")
        course_dropdown = OptionMenu(canvas, selected_course, *all_courses)
        course_dropdown.grid(row=2, column=2)

        is_core_l = Label(canvas, text='Core', anchor="e", width=18)
        is_core_l.grid(row=3, column=1)
        selected_is_core = StringVar(canvas, value="False")
        is_core_dropdown = OptionMenu(
            canvas, selected_is_core, *is_core_values)
        is_core_dropdown.grid(row=3, column=2)

        # Submit button to save the deg_course
        def submit_deg_course():
            if not (selected_degree.get() and selected_course.get()):
                return messagebox.showerror("Error", "Both degree and course are required")
            degree_name, level = selected_degree.get().split(',')

            course_id, name = selected_course.get().split(',')
            is_core = selected_is_core.get() == "True"

            degree_name = degree_name.strip()
            level = level.strip()
            course_id = course_id.strip()
            result = enter_degree_course(context.cursor, degree_name,
                                         level, course_id, is_core)
            if "error" in result:
                messagebox.showerror("Error", result["error"])
                reset()
                initializer()
            elif "message" in result:
                messagebox.showinfo("Success", result["message"])
                add_deg_course()
        # Submit
        submit = Button(canvas, text='Submit',
                        command=submit_deg_course, width=18)
        submit.grid(row=10, column=3)

    initializer()

# End
