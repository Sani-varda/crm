import frappe
import json

def run():
    frappe.init('crm.localhost')
    frappe.connect()

    print('Configuring School Admission Layouts for IDPS Borivali...')

    # 1. Lead Quick Entry Layout
    lead_qe_layout = [
        {
            "name": "parent_section",
            "label": "Parent / Guardian Details",
            "columns": [
                {
                    "name": "col_parent_1",
                    "fields": ["salutation", "first_name", "last_name"]
                },
                {
                    "name": "col_parent_2",
                    "fields": ["mobile_no", "email"]
                }
            ]
        },
        {
            "name": "student_admission_section",
            "label": "Student & Admission Details",
            "columns": [
                {
                    "name": "col_student_1",
                    "fields": ["student_name", "grade_applying_for", "academic_year"]
                },
                {
                    "name": "col_student_2",
                    "fields": ["child_dob", "child_gender", "previous_school"]
                }
            ]
        },
        {
            "name": "inquiry_section",
            "label": "Inquiry Details & Assignment",
            "columns": [
                {
                    "name": "col_inquiry_1",
                    "fields": ["status", "source"]
                },
                {
                    "name": "col_inquiry_2",
                    "fields": ["lead_owner", "territory"]
                }
            ]
        }
    ]

    # 2. Lead Side Panel Layout
    lead_sp_layout = [
        {
            "label": "Student & Admission",
            "name": "student_section",
            "opened": True,
            "columns": [
                {
                    "name": "col_sp_student",
                    "fields": [
                        "student_name",
                        "grade_applying_for",
                        "academic_year",
                        "child_dob",
                        "child_gender",
                        "previous_school"
                    ]
                }
            ]
        },
        {
            "label": "Parent Contact",
            "name": "parent_section",
            "opened": True,
            "columns": [
                {
                    "name": "col_sp_parent",
                    "fields": [
                        "salutation",
                        "first_name",
                        "last_name",
                        "mobile_no",
                        "email"
                    ]
                }
            ]
        },
        {
            "label": "Inquiry Info",
            "name": "inquiry_info_section",
            "opened": True,
            "columns": [
                {
                    "name": "col_sp_inquiry",
                    "fields": [
                        "status",
                        "source",
                        "lead_owner",
                        "territory"
                    ]
                }
            ]
        }
    ]

    # 3. Deal Quick Entry Layout
    deal_qe_layout = [
        {
            "name": "student_deal_section",
            "label": "Student & Admission Details",
            "columns": [
                {
                    "name": "col_deal_s1",
                    "fields": ["deal_name", "student_name", "grade_applying_for"]
                },
                {
                    "name": "col_deal_s2",
                    "fields": ["academic_year", "child_dob", "child_gender"]
                }
            ]
        },
        {
            "name": "pipeline_section",
            "label": "Stage & Counselor",
            "columns": [
                {
                    "name": "col_deal_p1",
                    "fields": ["status", "deal_owner"]
                },
                {
                    "name": "col_deal_p2",
                    "fields": ["lead", "expected_closing"]
                }
            ]
        }
    ]

    # 4. Deal Side Panel Layout
    deal_sp_layout = [
        {
            "label": "Student & Admission",
            "name": "student_deal_section",
            "opened": True,
            "columns": [
                {
                    "name": "col_sp_deal_s",
                    "fields": [
                        "student_name",
                        "grade_applying_for",
                        "academic_year",
                        "child_dob",
                        "child_gender",
                        "previous_school"
                    ]
                }
            ]
        },
        {
            "label": "Stage & Details",
            "name": "stage_section",
            "opened": True,
            "columns": [
                {
                    "name": "col_sp_deal_stage",
                    "fields": [
                        "status",
                        "deal_owner",
                        "lead",
                        "expected_closing",
                        "probability"
                    ]
                }
            ]
        }
    ]

    layouts = {
        "CRM Lead-Quick Entry": lead_qe_layout,
        "CRM Lead-Side Panel": lead_sp_layout,
        "CRM Deal-Quick Entry": deal_qe_layout,
        "CRM Deal-Side Panel": deal_sp_layout
    }

    for name, layout_obj in layouts.items():
        if frappe.db.exists("CRM Fields Layout", name):
            doc = frappe.get_doc("CRM Fields Layout", name)
            doc.layout = json.dumps(layout_obj)
            doc.save(ignore_permissions=True)
            print(f"  + Updated layout: {name}")

    frappe.db.commit()
    print('Successfully applied School Admission layouts to Sensora!')

if __name__ == '__main__':
    run()

