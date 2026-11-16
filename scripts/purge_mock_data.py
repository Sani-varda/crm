import os
import frappe

def purge():
    frappe.init(site="crm.localhost", sites_path="sites")
    frappe.connect()

    print("--- Purging Mock Data ---")

    # 1. Purge WA Messages
    count_wa_msg = frappe.db.count("WA Message")
    frappe.db.sql("DELETE FROM `tabWA Message`")
    print(f"Deleted {count_wa_msg} WA Messages")

    # 2. Purge WA Profiles
    count_wa_prof = frappe.db.count("WA Profile")
    frappe.db.sql("DELETE FROM `tabWA Profile`")
    print(f"Deleted {count_wa_prof} WA Profiles")

    # 3. Clean WA Accounts - reset to clean state ready for Meta Cloud API
    count_wa_acc = frappe.db.count("WA Account")
    frappe.db.sql("DELETE FROM `tabWA Account`")
    print(f"Deleted {count_wa_acc} WA Accounts")

    # 4. Reset WA Settings
    settings = frappe.get_single("WA Settings")
    settings.default_account = ""
    token = os.environ.get("WHATSAPP_VERIFY_TOKEN")
    if token:
        settings.webhook_verify_token = token
    settings.webhook_secret = ""
    settings.save(ignore_permissions=True)
    print("Reset WA Settings to clean state")

    # 5. Purge Sample Leads & Deals
    leads = frappe.get_all("CRM Lead", pluck="name")
    for l in leads:
        frappe.delete_doc("CRM Lead", l, force=True, ignore_permissions=True)
    print(f"Deleted {len(leads)} CRM Leads")

    deals = frappe.get_all("CRM Deal", pluck="name")
    for d in deals:
        frappe.delete_doc("CRM Deal", d, force=True, ignore_permissions=True)
    print(f"Deleted {len(deals)} CRM Deals")

    # 6. Purge Notes, Tasks, Call Logs
    for dt in ["FCRM Note", "CRM Task", "CRM Call Log"]:
        if frappe.db.exists("DocType", dt):
            items = frappe.get_all(dt, pluck="name")
            for item in items:
                frappe.delete_doc(dt, item, force=True, ignore_permissions=True)
            print(f"Deleted {len(items)} {dt} records")

    # 7. Clean up orphaned comments
    frappe.db.sql("DELETE FROM `tabComment` WHERE reference_doctype IN ('CRM Lead', 'CRM Deal', 'WA Message')")
    print("Cleaned up comments")

    frappe.db.commit()
    print("--- Database is clean: Zero Mock Data! ---")

if __name__ == "__main__":
    purge()
