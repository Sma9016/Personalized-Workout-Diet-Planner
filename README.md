# **Personalized Workout & Diet Planner (Mock AI)**

This project is a full-stack, two-part application designed to generate personalized 7-day workout and meal plans based on user inputs like fitness goals, equipment availability, budget, and cuisine preferences. The backend simulates AI generation using structured JSON mock data and includes CRUD functionality for saving and retrieving generated plans.

## **✨ Features**

* **Dual Architecture:** Separated frontend (Streamlit) and backend (Flask) for professional deployment practice.  
* **Structured Planning:** Generates detailed 7-day plans, including daily workouts (sets/reps/notes) and budget-friendly meal schedules (cost estimation, recipe).  
* **Dynamic Inputs (Mocked):** The mock data logic dynamically changes the workout and meal plans based on user selections for Goal, Level, Equipment, Intensity, Budget (in INR), and Cuisine.  
* **Data Persistence (CRUD):** Plans are saved upon generation to a local JSON file (plans\_data.json) via the Flask backend, and a "History of Plans" tab allows users to retrieve and review past plans (Read/Save functionality).  
* **Responsive UI:** Built with Streamlit for a fast, clean, and interactive user experience.

## **🛠️ Tech Stack**

* **Frontend:** [Streamlit](https://streamlit.io/) (for rapid UI development)  
* **Backend:** [Flask](https://flask.palletsprojects.com/) (for REST API and business logic)  
* **API (Mocked):** Designed for integration with the Gemini API (gemini-2.5-flash), currently using static mock data.  
* **Persistence:** Local File Storage (plans\_data.json)

## **⚙️ Setup and Installation**

### **Prerequisites**

You need **Python 3.8+** installed on your system.

### **1\. Clone the Repository (Assuming you have your project files)**

If you are using this as a template, clone the project:

git clone \<your-repo-url\>  
cd \<project-directory\>

### **2\. Install Dependencies**

Install all required packages for both the frontend and backend using the requirements.txt file:

pip install \-r requirements.txt

### **3\. Configure the Flask Backend (app.py)**

The application is currently configured in **Mock Mode**, meaning it does not require a Gemini API Key to run. However, if you wish to switch to live AI generation later, you would need to replace the placeholder:

\# In app.py (Line \~9)  
GEMINI\_API\_KEY \= os.environ.get("GEMINI\_API\_KEY", "YOUR\_API\_KEY\_HERE")

For now, the Mock Mode is sufficient for testing.

## **▶️ How to Run the Application**

This application requires **two separate terminal windows** to run simultaneously: one for the Flask backend and one for the Streamlit frontend.

### **Terminal 1: Start the Flask Backend**

In your first terminal, navigate to the project directory and run the Flask application:

python app.py

You should see output indicating the server is running on http://127.0.0.1:5000.

### **Terminal 2: Start the Streamlit Frontend**

In your second terminal, navigate to the project directory and run the Streamlit application:

streamlit run streamlit\_app.py

This will automatically open the web application in your default browser.

### **Usage**

1. Use the **sidebar controls** to set your fitness goal, equipment, intensity, weekly budget (INR), and cuisine focus.  
2. Click the **"Generate Plans With AI"** button.  
3. The application will connect to the Flask backend, generate the mock plan, and display the results in the **"Current Plan"** tab.  
4. Check the **"History of Plans"** tab to see your generated plan saved via the CRUD endpoint.