<div align="center" markdown="1">

<a href="https://www.sensora.co.in">
    <h1>Sensora</h1>
</a>

<h3>Sensora - Customer Relation Management</h3>

**Simplify Admissions, Amplify Relationships**

<div>
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset=".github/screenshots/FrappeCRMHeroImage.png">
        <img width="1402" alt="Sensora Hero Image" src=".github/screenshots/FrappeCRMHeroImage.png">
    </picture>
</div>

[Website](https://www.sensora.co.in) - [Support](mailto:support@sensora.co.in)

</div>

## Sensora - Customer Relation Management

Sensora is a modern, intuitive, and high-performance Customer Relation Management system tailored for educational institutions and growing organizations, custom-configured for **IDPS Borivali**. Sensora is crafted to provide a seamless admissions counseling journey, complete WhatsApp integration, and end-to-end applicant tracking while keeping data clean and organized.

### Key Features

-   **User-Friendly and Flexible:** A simple, intuitive interface that’s easy to navigate and highly customizable for admission counselors, managers, and administrative staff.
-   **All-in-One Lead/Deal Page:** Consolidate inquiries, parent interactions, student details, application forms, assessments, and follow-ups in a single unified view.
-   **Admissions Kanban Pipeline:** Visually track applicants across stages (Inquiry ➔ Campus Visit ➔ Form Submitted ➔ Assessment ➔ Enrolled) with drag-and-drop convenience.
-   **WhatsApp Integration & AI Chatbot:** Full two-way WhatsApp messaging via Meta Cloud API and automated 24/7 AI counselor support powered by Groq (`llama-3.3-70b-versatile`).
-   **Custom School Fields:** Native tracking for student name, grade applying for, academic year, previous school, date of birth, and parent contact information.

## Getting Started (Production)

### Self Hosting with Docker

Follow these steps to set up Sensora in production:

**Step 1**: Clone the repository and enter the docker directory
```bash
git clone https://github.com/sensora/crm.git
cd crm/docker
```

**Step 2**: Start the containers
```bash
docker compose up -d
```

**Step 3**: Access Sensora at [http://localhost:8000/crm](http://localhost:8000/crm) with credentials:
- **Username**: `Administrator`
- **Password**: `admin`

## Getting Started (Development)

### Local Bench Setup

1. In the frappe-bench directory, ensure dependencies and apps are installed:
    ```sh
    $ bench get-app whatsapp
    $ bench get-app crm
    $ bench --site crm.localhost install-app crm
    ```
2. Access Sensora at `crm.localhost:8000/crm` in your web browser.

**Frontend Development**
1. Navigate to the frontend directory:
    ```sh
    cd apps/crm/frontend
    yarn install
    yarn dev
    ```

## Learn and Connect

-   **Website**: [www.sensora.co.in](https://www.sensora.co.in)
-   **Support**: [support@sensora.co.in](mailto:support@sensora.co.in)

<br>
<div align="center" style="padding-top: 0.75rem;">
	<a href="https://www.sensora.co.in" target="_blank">
		<b>Sensora Technologies</b>
	</a>
</div>
