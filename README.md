# BookLit

![BookLit Home Page](images/home-page.png)

**BookLit** is a comprehensive library management system (e-library). The system is built using **Flask** for the backend and **Vue.js** for the frontend, providing a seamless and modern interface for both administrator and users.

## Features

Following are the features present in Booklit:

- **User Registration and Email Verification**: 
  - Users can register with their email addresses.
  - An email verification step is required before users can log in.

- **Admin and User Login**: 
  - Unified login interface and Role-based access controls for admins and users.

- **Admin Features**:
  - **CRUD Operations**: Admins can create, read, update, and delete sections and books.
  - **Manage User Access**: Admins can issue or revoke book access for users.
  - **Export Library Details**: Admins can export library data and reports.
  - **Monthly Performance Emails**: Automatic monthly emails summarizing library performance.


- **User Features**:
  - **Issue and Return Books**: Users can issue books and return them when done.
  - **Purchase and Download Books**: Users can purchase and download books directly from the library.
  - **Rate Books**: Users can rate books they have issued or purchased.
  - **Account Management**: Users have the ability to delete their accounts.
  - **Text-to-Speech**: Users can listen to a text-to-speech version of the e-books.
  - **Search Functionality**: Users can search for books, authors and sections within the library.

- **Notifications**:
  - **Daily Reminders**: If a user does not visit the site within a day, they receive a reminder and if they have an approaching return date.
  - **Revoke Overdue Access**: Automatically revokes access to books that have passed their return date and informs the users.

- **Modern Web Features**:
  - **Progressive Web App (PWA)**: It can be installed as web app on any device.
  - **Single Page Application (SPA)**: The application provides a seamless user experience with dynamic content updates without page reloads.
  - **Responsive Design**: It is fully responsive, ensuring a seamless user experience across desktops, tablets, and mobile devices.

## Database Schema Design

Below is the ER diagram representing the database schema for BookLit:

![BookLit ER Diagram](images/er-diagram.png)

## Technologies Used

### Backend (Flask):
- **Flask**: Backend framework to manage the server-side logic and routing.
- **Flask-Security-Too**: Handles user authentication, registration, and role-based access control.
- **Flask-Migrate**: Manages database migrations to handle schema changes over time.
- **Flask-SQLAlchemy**: Object-relational mapping (ORM) for managing database interactions.
- **Flask-WTF and WTForms**: Provides form handling and validation.
- **Flask-Caching**: Adds caching capabilities to the backend to improve performance.
- **Flask-Mailman**: Handles sending emails (e.g., for confirmation, reminders).
- **Celery**: Manages asynchronous tasks, batch jobs, and scheduled jobs.
- **Redis**: Used for caching and as a message broker for Celery tasks.
- **Pandas**: Used for creating CSV exports.
- **Jinja2 and pdfkit**: Used for generating PDFs from HTML templates.
- **SQLite**: Lightweight database used for data storage.

### Frontend (Vue.js):
- **Vue.js**: Frontend framework for building user interfaces.
- **Vue-Router**: Manages navigation between different views in the application.
- **Pinia**: State management library to handle application-wide state.
- **Yup**: Schema validation library used for form validation.
- **Vee-Validate**: Form validation library for Vue.js.
- **Vite**: Local development server for the front-end.
- **Google Charts**: Visualizes data in the form of charts and graphs.
- **Adobe PDF Embed API**: Embeds PDF viewer for displaying e-books.
- **PDF.js**: A JavaScript library used to read the pdfs.
- **Tween**: Animates integers for dynamic UI effects in dashboards.
- **HTML, CSS, and Bootstrap**: Used for structuring and styling the application.
- **Lottie-web**: Animates the play and pause button of pdf reader.

## Prerequisites

Before running the application, ensure that the following prerequisites are met:

1. The machine should be capable of emulating Linux.
2. Redis must be installed.
3. Node.js and Python should be installed on the machine.

## How to Run the Application

Follow these steps to get the BookLit application up and running:

### Step 1: Clone the Repository
Copy the repository to your local machine:
```bash
git clone https://github.com/shrasinh/booklitE-libraryV2.git
cd booklitE-libraryV2
```

### Step 2: Start Redis Server
Ensure the Redis server is running. If it's not started, restart/start the Redis server using:
```bash
sudo systemctl restart redis-server
```

### Step 3: Export Environment Variables
Open three terminal windows and export the following environment variables in all of them:
```bash
VITE_ADOBE_API_KEY=<your_adobe_api_key>
LIBRARIAN_EMAIL=<your-admin-email@example.com>
MAIL_SERVER=<smtp.example.com>
MAIL_PORT=<your-mail-port-number>
MAIL_USERNAME=<your-email@example.com>
MAIL_PASSWORD=<your-email-password>
```

### Step 4: Start the Backend Server
In the first terminal, navigate to the backend directory, install the necessary Python dependencies, and run the Flask application:
```bash
cd back-end
pip install -r requirements.txt
python main.py
```

### Step 5: Start the Celery Worker
In the second terminal, start the Celery worker and beat with the following command:
```bash
cd back-end
celery -A application.setup.celery worker --loglevel=INFO -B
```

### Step 6: Start the Frontend Development Server
In the third terminal, navigate to the frontend directory, install the necessary npm packages, and start the development server:
```bash
cd front-end
npm install
npm run dev
```

### Step 7: Access the Application
Open a web browser and navigate to the following URL to access the application:
```
http://localhost:5173/
```

## Project Structure

### `back-end` folder
The `back-end` folder contains all the files and folders necessary for the backend of the BookLit application.

- **`instance` folder**: 
  - Contains the SQLite database file, `library.sqlite3`. This will be created if not present when the back-end starts for the first time.

- **`application` folder**: 
  - Houses the Python files such as models, forms, and setup needed by the controllers.

- **`controllers` folder**: 
  - Includes the controllers and Celery functions of the application.

- **`static` folder**: 
  - Stores thumbnails of the books and CSS files used for the monthly report.

- **`files` folder**: 
  - Stores the PDF files of the books.

- **`templates` folder**: 
  - Contains HTML templates for the monthly report.

- **`main.py`**: 
  - The main Python file that contains the run method of the application.



### `front-end` folder
The `front-end` folder contains all the files and folders necessary for the frontend of the BookLit application.

- **`index.html`**: 
  - The main HTML file.

- **`vite.config.js`**: 
  - Configuration file for Vite.

- **`src` folder**: 
  - Contains all the Vue-related files.
  - **`components`**: Reusable Vue components.
  - **`router`**: Different views and routes.
  - **`stores`**: Pinia stores for state management.
  - **`App.vue`**: The main Vue component.
  - **`main.js`**: The entry point file to mount the Vue application.
  - **`assets`**: Contains main CSS and manifest.json files.

## Note:

- **Default Admin Login Credentials**:
  - Username: `librarian`
  - Password: `pass#word12`
  - These credentials can be changed in the `back-end/application/setup.py` file.

- **Adobe PDF Embed API**:
  - An API key is required for using Adobe PDF Embed API. You can create a free API key [here](https://acrobatservices.adobe.com/dc-integration-creation-app-cdn/main.html?api=pdf-embed-api).

- **Mail Configuration**:
  - Mail is sent using SSL. This setting can be modified in the `back-end/application/setup.py` file.

- **Version 1 of the project**:
  - Version 1 of the project can be found [here](https://github.com/shrasinh/booklitE-library). Version 1 focuses more on the backend and does Server-Side Rendering with Jinja template.
