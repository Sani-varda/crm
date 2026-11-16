import frappe

def run():
    frappe.init('crm.localhost')
    frappe.connect()

    print('Creating School Admission Custom Fields for IDPS Borivali...')

    custom_fields = {
        "CRM Lead": [
            {
                "fieldname": "admissions_section",
                "label": "Student & Admission Details",
                "fieldtype": "Section Break",
                "insert_after": "email"
            },
            {
                "fieldname": "student_name",
                "label": "Student Name",
                "fieldtype": "Data",
                "insert_after": "admissions_section"
            },
            {
                "fieldname": "child_dob",
                "label": "Child Date of Birth",
                "fieldtype": "Date",
                "insert_after": "student_name"
            },
            {
                "fieldname": "child_gender",
                "label": "Gender",
                "fieldtype": "Select",
                "options": "\nBoy\nGirl\nOther",
                "insert_after": "child_dob"
            },
            {
                "fieldname": "admission_column_break",
                "fieldtype": "Column Break",
                "insert_after": "child_gender"
            },
            {
                "fieldname": "grade_applying_for",
                "label": "Grade Applying For",
                "fieldtype": "Select",
                "options": "\nPlaygroup\nNursery\nJunior KG\nSenior KG\nGrade 1\nGrade 2\nGrade 3\nGrade 4\nGrade 5\nGrade 6\nGrade 7\nGrade 8\nGrade 9\nGrade 10\nGrade 11\nGrade 12",
                "insert_after": "admission_column_break"
            },
            {
                "fieldname": "academic_year",
                "label": "Academic Year",
                "fieldtype": "Select",
                "options": "\n2025-2026\n2026-2027\n2027-2028",
                "insert_after": "grade_applying_for"
            },
            {
                "fieldname": "previous_school",
                "label": "Previous School Attended",
                "fieldtype": "Data",
                "insert_after": "academic_year"
            }
        ],
        "CRM Deal": [
            {
                "fieldname": "admissions_section",
                "label": "Student & Admission Details",
                "fieldtype": "Section Break",
                "insert_after": "organization"
            },
            {
                "fieldname": "student_name",
                "label": "Student Name",
                "fieldtype": "Data",
                "insert_after": "admissions_section"
            },
            {
                "fieldname": "child_dob",
                "label": "Child Date of Birth",
                "fieldtype": "Date",
                "insert_after": "student_name"
            },
            {
                "fieldname": "child_gender",
                "label": "Gender",
                "fieldtype": "Select",
                "options": "\nBoy\nGirl\nOther",
                "insert_after": "child_dob"
            },
            {
                "fieldname": "admission_column_break",
                "fieldtype": "Column Break",
                "insert_after": "child_gender"
            },
            {
                "fieldname": "grade_applying_for",
                "label": "Grade Applying For",
                "fieldtype": "Select",
                "options": "\nPlaygroup\nNursery\nJunior KG\nSenior KG\nGrade 1\nGrade 2\nGrade 3\nGrade 4\nGrade 5\nGrade 6\nGrade 7\nGrade 8\nGrade 9\nGrade 10\nGrade 11\nGrade 12",
                "insert_after": "admission_column_break"
            },
            {
                "fieldname": "academic_year",
                "label": "Academic Year",
                "fieldtype": "Select",
                "options": "\n2025-2026\n2026-2027\n2027-2028",
                "insert_after": "grade_applying_for"
            },
            {
                "fieldname": "previous_school",
                "label": "Previous School Attended",
                "fieldtype": "Data",
                "insert_after": "academic_year"
            }
        ]
    }

    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(custom_fields, ignore_validate=True)
    frappe.db.commit()
    print('Successfully created Student & Admission custom fields on CRM Lead and CRM Deal!')

if __name__ == '__main__':
    run()

