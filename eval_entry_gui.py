# --------------------------------------------
#  Eval Entry
#     Builds the window for Eval entry
# --------------------------------------------
from tkinter import messagebox
from data_manipulate_func import update_evaluation, enter_evaluation
from query_func import get_source_evaluation, return_sections_over_percentage, check_evaluation_status, return_all_goals
from context import context
from tkinter import *

tracker = 'empty'


def reset():
    global canvas
    global tracker
    tracker = 'empty'
    canvas.destroy()


def eval_search_update_duplicate():
    rootData = Tk()
    rootData.geometry("1400x400")
    canvas = Canvas(rootData)
    canvas.pack(side='right', fill="both", expand=True)

    def initializer():
        global canvas
        canvas = Canvas(rootData)
        canvas.pack(side='right', fill="both", expand=True)
        instL = Label(canvas, text='Instructor ID', width=18)
        instL.grid(row=0, column=1)
        instE = Entry(canvas, width=18)
        instE.grid(row=0, column=2)

        semesters = ['Spring', 'Summer', 'Fall']
        selected_semester = StringVar(canvas, value=semesters[0])
        semester_dropdown = OptionMenu(canvas, selected_semester, *semesters)
        semester_label = Label(canvas, text='Semester', anchor="e", width=18)
        semester_label.grid(row=0, column=3)
        semester_dropdown.grid(row=0, column=4)

        year_l = Label(canvas, text='Year', width=18)
        year_l.grid(row=0, column=5)
        year_e = Entry(canvas, width=18)
        year_e.grid(row=0, column=6)

        search = Button(canvas, text='Search',
                        command=lambda: search_evaluations(instE.get().strip(), selected_semester.get(), year_e.get().strip()))
        search.grid(row=0, column=7)

        # Section Over Percentage Query Inputs
        percent_l = Label(canvas, text="Percentage", width=18)
        percent_l.grid(row=1, column=1, padx=5, pady=5)
        percent_e = Entry(canvas, width=18)
        percent_e.grid(row=1, column=2, padx=5, pady=5)

        percent_search_btn = Button(canvas, text="Search Over Percentage",
                                    command=lambda: search_sections_over_percentage(year_e.get().strip(), selected_semester.get(), percent_e.get().strip()))
        percent_search_btn.grid(row=1, column=3, padx=5, pady=5)

    # Search classes function
    def search_evaluations(ins_id, semester, year):
        # Fetch evaluation status
        results = check_evaluation_status(
            context.cursor, semester=semester, year=year, ins_id=ins_id)
        display_evaluations(results)

    # Function to display evaluation results
    def display_evaluations(results):
        rootClasses = Tk()
        rootClasses.geometry("1400x600")

        # Create Header Row
        columns = ["Degree Name", "Level", "Course Section",
                   "Status", "Missing Fields", "Actions"]
        for col, header in enumerate(columns):
            Label(rootClasses, text=header, font=(
                "Arial", 10, "bold")).grid(row=0, column=col)

        # Populate Table with Data
        for i, evaluation in enumerate(results):
            Label(rootClasses, text=f"{evaluation['degree_name']}").grid(
                row=i + 1, column=0)
            Label(rootClasses, text=f"{evaluation['level']}").grid(
                row=i + 1, column=1)
            Label(
                rootClasses, text=f"{evaluation['course_id']} - {evaluation['sec_id']}").grid(row=i + 1, column=2)
            Label(rootClasses, text=f"{evaluation['status']}").grid(
                row=i + 1, column=3)
            Label(rootClasses, text=f"{', '.join(evaluation['missing_fields'])}").grid(
                row=i + 1, column=4)
            Button(rootClasses, text="Edit", command=lambda evaluation=evaluation: edit_evaluation(
                evaluation, rootClasses)).grid(row=i + 1, column=6)
            Button(rootClasses, text="Duplicate", command=lambda evaluation=evaluation: duplicate_eval(
                evaluation)).grid(row=i + 1, column=7)

    # Edit evaluation function triggered with edit button
    def edit_evaluation(evaluation, rootClasses):
        # Pop a window for edit
        editWindow = Tk()
        editWindow.geometry("1400x500")
        editWindow.title("Edit Evaluation")

        degree_name = evaluation.get('degree_name')
        level = evaluation.get('level')
        course_id = evaluation.get('course_id')
        sec_id = evaluation.get('sec_id')
        year = evaluation.get('year')
        semester = evaluation.get('semester')

        # Check if all fields have default or NULL values
        isInsert = all([
            evaluation.get('improvement') is None,
            evaluation.get('grade_a') is None,
            evaluation.get('grade_b') is None,
            evaluation.get('grade_c') is None,
            evaluation.get('grade_f') is None,
            evaluation.get('measure_type') in [None, '']
        ])

        # Display course-section details
        Label(editWindow, text=f"Editing Evaluation for:", anchor="w").pack()
        Label(editWindow, text=f"Course: {course_id} - {sec_id}").pack()
        Label(
            editWindow, text=f"Degree: {degree_name} (Level: {level})").pack()
        Label(
            editWindow, text=f"Year: {year}, Semester: {semester}").pack()

        # Goal selection for goal specific evaluation entry
        goals = return_all_goals(context.cursor, degree_name, level)
        goals_list = [f"{goal} - {description} - {degree} - {level}" for goal,
                      description, degree, level in goals]
        selected_goal = StringVar(editWindow, value=goals_list[0])
        goal_label = Label(editWindow, text="Goal").pack()
        goals_dropdown = OptionMenu(
            editWindow, selected_goal, *goals_list).pack()
        Label(editWindow, text="Improvement").pack()
        improvement = StringVar(
            editWindow, value=evaluation.get('improvement', ''))
        Entry(editWindow, textvariable=improvement).pack()
        grade_a = IntVar(editWindow, value=evaluation.get('grade_a') or 0)
        Label(editWindow, text="Grade A:").pack()
        Entry(editWindow, textvariable=grade_a).pack()

        grade_b = IntVar(editWindow, value=evaluation.get('grade_b') or 0)
        Label(editWindow, text="Grade B:").pack()
        Entry(editWindow, textvariable=grade_b).pack()

        grade_c = IntVar(editWindow, value=evaluation.get('grade_c') or 0)
        Label(editWindow, text="Grade C:").pack()
        Entry(editWindow, textvariable=grade_c).pack()

        grade_f = IntVar(editWindow, value=evaluation.get('grade_f') or 0)
        Label(editWindow, text="Grade F:").pack()
        Entry(editWindow, textvariable=grade_f).pack()

        standard_methods = ["Homework", "Project", "Quiz",
                            "Oral Presentation", "Report", "Mid-term", "Final Exam", "New Method"]
        selected_measure = StringVar(
            editWindow, value=evaluation.get('measure_type') or "")
        measure_l = Label(editWindow, text='Measurement').pack()
        measure_dropdown = OptionMenu(
            editWindow, selected_measure, *standard_methods).pack()
        # Not placing the new lavel entry yet
        new_measure_l = Label(editWindow, text='New Method')
        new_measure_e = Entry(editWindow)

        def show_new_measure_field(*args):
            if selected_measure.get() == 'New Method':
                new_measure_l.pack()
                new_measure_e.pack()
            else:
                new_measure_l.pack_forget()
                new_measure_e.pack_forget()

        selected_measure.trace('w', show_new_measure_field)

        # Save Button
        Button(editWindow, text="Save", command=lambda: submit_update_evaluation(
            evaluation, selected_goal.get(), improvement.get(), grade_a.get(), grade_b.get(), grade_c.get(), grade_f.get(), selected_measure.get(),         rootClasses=rootClasses,
            editWindow=editWindow, isInsert=isInsert)).pack()

        def submit_update_evaluation(evaluation, goal, improvement, grade_a, grade_b, grade_c, grade_f, measure_type, rootClasses, editWindow, isInsert):
            measure_type = new_measure_e.get().strip().title(
            ) if selected_measure.get() == "New Method" else selected_measure.get()

            goal_code, description, degree_name, level = goal.split(" - ")
            goalcode = goal_code.strip()
            update_values = {"improvement": improvement, "grade_a": grade_a,
                             "grade_b": grade_b, "grade_c": grade_c, "grade_f": grade_f, "measure_type": measure_type}
            if not isInsert:
                result = update_evaluation(context.cursor, evaluation['sec_id'], evaluation['semester'], evaluation['year'],
                                           evaluation['course_id'], goalcode, evaluation['degree_name'], evaluation['level'], **update_values)
                if "error" in result:
                    messagebox.showerror("Error", result["error"])
                    reset()
                    initializer()
                elif "message" in result:
                    messagebox.showinfo("Success", result["message"])
                    editWindow.destroy()  # Close the edit window
                    rootClasses.destroy()
            else:
                result = enter_evaluation(context.cursor, evaluation['sec_id'], evaluation['semester'], evaluation['year'],
                                          evaluation['course_id'], goalcode, evaluation['degree_name'], evaluation['level'], **update_values)

                if "error" in result:
                    messagebox.showerror("Error", result["error"])
                    reset()
                elif "message" in result:
                    messagebox.showinfo("Success", result["message"])

    def duplicate_eval(evaluation):

        # Pop a window for duplication
        duplicateWindow = Tk()
        duplicateWindow.geometry("400x300")
        duplicateWindow.title("Duplicate Evaluation")

        degree_name = evaluation.get('degree_name')
        level = evaluation.get('level')
        course_id = evaluation.get('course_id')
        sec_id = evaluation.get('sec_id')
        year = evaluation.get('year')
        semester = evaluation.get('semester')

        source_evaluation = get_source_evaluation(
            context.cursor, sec_id, semester, year, course_id)
        if "error" in source_evaluation:
            messagebox.showerror("Error", source_evaluation["error"])
            duplicateWindow.destroy()
            return
        source_dict = {
            "improvement": source_evaluation[0].strip(),
            "grade_a": source_evaluation[1],
            "grade_b": source_evaluation[2],
            "grade_c": source_evaluation[3],
            "grade_f": source_evaluation[4],
            "measure_type": source_evaluation[5],
        }

        # Display course-section details
        Label(duplicateWindow, text=f"Editing Evaluation for:", anchor="w").pack()
        Label(duplicateWindow, text=f"Course: {course_id} - {sec_id}").pack()
        Label(
            duplicateWindow, text=f"Degree: {degree_name} (Level: {level})").pack()
        Label(
            duplicateWindow, text=f"Year: {year}, Semester: {semester}").pack()

        # Goal selection for goal specific evaluation entry
        goals = return_all_goals(context.cursor, degree_name, level)
        goals_list = [f"{goal} - {description} - {degree} - {level}" for goal,
                      description, degree, level in goals]
        selected_goal = StringVar(duplicateWindow, value=goals_list[0])
        goal_label = Label(duplicateWindow, text="Goal").pack()
        goals_dropdown = OptionMenu(
            duplicateWindow, selected_goal, *goals_list).pack()
        improvement = StringVar(
            duplicateWindow, value=source_dict.get('improvement', ''))
        Label(duplicateWindow,
              text=f"Improvement: {improvement.get()}").pack()
        grade_a = IntVar(
            duplicateWindow, value=source_dict.get('grade_a') or 0)
        Label(duplicateWindow, text=f"Grade A: {grade_a.get()}").pack()

        grade_b = IntVar(
            duplicateWindow, value=source_dict.get('grade_b') or 0)
        Label(duplicateWindow, text=f"Grade B: {grade_b.get()}").pack()

        grade_c = IntVar(
            duplicateWindow, value=source_dict.get('grade_c') or 0)
        Label(duplicateWindow, text=f"Grade C: {grade_c.get()}").pack()

        grade_f = IntVar(
            duplicateWindow, value=source_dict.get('grade_f') or 0)
        Label(duplicateWindow, text=f"Grade F: {grade_f.get()}").pack()
        measure_type = StringVar(
            duplicateWindow, value=source_dict.get('measure_type', ''))
        Label(duplicateWindow,
              text=f"Measure Type: {measure_type.get()}").pack()

        # Confirm Duplication
        Button(duplicateWindow, text="Confirm",
               command=lambda: confirm_duplicate(context.cursor, sec_id, semester, year, course_id, selected_goal.get(), degree_name, level, improvement.get(), grade_a.get(), grade_b.get(), grade_c.get(), grade_f.get(), measure_type.get())).pack()

    def confirm_duplicate(cur, sec_id, semester, year, course_id, goal, degree_name, level, improvement, grade_a, grade_b, grade_c, grade_f, measure_type):
        confirm = messagebox.askyesno(
            "Warning", "Do you want to proceed duplication of the record?")
        if not confirm:
            return
        goal_code, description, deg_name, lev = goal.split(" - ")
        goal = goal_code.strip()
        result = enter_evaluation(context.cursor, sec_id, semester, year, course_id, goal,
                                  degree_name, level, grade_a, grade_b, grade_c, grade_f, improvement, measure_type)

        if "error" in result:
            messagebox.showerror(
                "Error", result["error"])
            reset()
            return
        elif "message" in result:
            messagebox.showinfo("Message", result["message"])

    def search_sections_over_percentage(year, semester, percentage: str):
        if not year or not semester or not percentage:
            messagebox.showwarning(
                "Input Error", "Year, Semester, Percentage are required")
            return
        # Check if percentage is positive integer
        try:
            percentage = int(percentage)
            if percentage <= 0:
                messagebox.showwarning(
                    "Input Error", "Percentage must be a positive integer")
                return
        except ValueError:
            messagebox.showwarning(
                "Input Error", "Percentage must be a positive integer")
            return

        year = year.strip()
        sections = return_sections_over_percentage(
            context.cursor, year, semester, percentage)
        if sections:
            display_section_over_percentage(
                sections)
        else:
            messagebox.showinfo("No Results", "No Courses Found")

    def display_section_over_percentage(sections):
        sections_window = Toplevel()
        sections_window.geometry("1400x600")

        # Create Header Row
        columns = ["Section_id", "Course_id", "Year",
                   "Semester", "Num_student", "Percentage"]
        for col, header in enumerate(columns):
            Label(sections_window, text=header, font=(
                "Arial", 10, "bold")).grid(row=0, column=col)

        for idx, row in enumerate(sections):
            sec_id, course_id, year, semester, num_std, percentage = row
            Label(sections_window, text=f"{sec_id}").grid(
                row=idx + 1, column=0)
            Label(sections_window, text=f"{course_id}").grid(
                row=idx + 1, column=1)
            Label(
                sections_window, text=f"{year}").grid(row=idx + 1, column=2)
            Label(sections_window, text=f"{semester}").grid(
                row=idx + 1, column=3)
            Label(sections_window, text=f"{num_std}").grid(
                row=idx + 1, column=4)
            Label(sections_window, text=f"{percentage}").grid(
                row=idx + 1, column=5)

    initializer()
# End
