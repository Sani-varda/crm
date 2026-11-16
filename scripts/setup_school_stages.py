import frappe

def run():
    frappe.init('crm.localhost')
    frappe.connect()

    print('Setting up IDPS Borivali School Admission Stages...')

    # 1. Lead Statuses (Inquiries)
    lead_stages = [
        {"lead_status": "New Inquiry", "type": "Open", "color": "gray", "position": 1},
        {"lead_status": "Contacted / Counseling", "type": "Ongoing", "color": "orange", "position": 2},
        {"lead_status": "Campus Visit Planned", "type": "Ongoing", "color": "blue", "position": 3},
        {"lead_status": "Follow-up Needed", "type": "Ongoing", "color": "yellow", "position": 4},
        {"lead_status": "Qualified for Admission", "type": "Won", "color": "green", "position": 5},
        {"lead_status": "Not Eligible / Dropped", "type": "Lost", "color": "red", "position": 6},
    ]

    for stage in lead_stages:
        name = stage["lead_status"]
        if frappe.db.exists("CRM Lead Status", name):
            doc = frappe.get_doc("CRM Lead Status", name)
            doc.update(stage)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "CRM Lead Status",
                "name": name,
                **stage
            })
            doc.insert(ignore_permissions=True)
        print(f"  + Lead Stage: {name}")

    # 2. Deal Statuses (Admission Pipeline)
    deal_stages = [
        {"deal_status": "Inquiry In Review", "type": "Ongoing", "position": 1, "probability": 10.0, "color": "blue"},
        {"deal_status": "Campus Visit Scheduled", "type": "Ongoing", "position": 2, "probability": 30.0, "color": "orange"},
        {"deal_status": "Campus Tour Done", "type": "Ongoing", "position": 3, "probability": 50.0, "color": "yellow"},
        {"deal_status": "Application Form Submitted", "type": "Ongoing", "position": 4, "probability": 70.0, "color": "purple"},
        {"deal_status": "Student Assessment / Interaction", "type": "Ongoing", "position": 5, "probability": 85.0, "color": "teal"},
        {"deal_status": "Admission Offered", "type": "Ongoing", "position": 6, "probability": 95.0, "color": "cyan"},
        {"deal_status": "Enrolled / Fees Paid", "type": "Won", "position": 7, "probability": 100.0, "color": "green"},
        {"deal_status": "Application Withdrawn", "type": "Lost", "position": 8, "probability": 0.0, "color": "red"},
    ]

    for stage in deal_stages:
        name = stage["deal_status"]
        if frappe.db.exists("CRM Deal Status", name):
            doc = frappe.get_doc("CRM Deal Status", name)
            doc.update(stage)
            doc.save(ignore_permissions=True)
        else:
            doc = frappe.get_doc({
                "doctype": "CRM Deal Status",
                "name": name,
                **stage
            })
            doc.insert(ignore_permissions=True)
        print(f"  + Deal Stage: {name}")

    # 3. Lead Sources for School Admissions
    school_sources = [
        "WhatsApp",
        "School Website",
        "Walk In / Campus Visit",
        "Parent Referral",
        "Google Ads / SEO",
        "Social Media (Instagram/Facebook)",
        "Education Fair / Hoarding",
        "Siblings / Alumni"
    ]

    for src in school_sources:
        if not frappe.db.exists("CRM Lead Source", src):
            frappe.get_doc({
                "doctype": "CRM Lead Source",
                "source_name": src
            }).insert(ignore_permissions=True)
            print(f"  + Source: {src}")

    frappe.db.commit()
    print('Successfully configured IDPS Borivali School Admission Stages!')

if __name__ == '__main__':
    run()

