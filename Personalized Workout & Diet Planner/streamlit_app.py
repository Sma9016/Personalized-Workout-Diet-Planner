import streamlit as st
import requests
import json
import time

# --- CONFIGURATION ---
FLASK_URL = "http://127.0.0.1:5000"
GENERATE_ENDPOINT = "/generate_plan"
FETCH_PLANS_ENDPOINT = "/get_plans"

# --- PAGE SETUP ---
st.set_page_config(
    page_title="Personalized Workout & Diet Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STYLE ---
st.markdown(
    """
    <style>
    /* Center the main title and set text color to white */
    .stApp > header {
        display: none;
    }
    .centered-title {
        text-align: center;
        color: white; 
        font-size: 2.5rem; 
        font-weight: bold;
        padding: 20px 0;
    }
    .plan-header {
        text-align: center;
        color: #4CAF50; /* Green highlight for plan name */
        font-size: 2rem;
        margin-top: 20px;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size:1.1rem;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown('<div class="centered-title">Personalized Workout & Diet Planner</div>', unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---

@st.cache_data(ttl=120)
def fetch_plans_history():
    """Fetches all previously saved plans from the backend (R - Read)."""
    try:
        # NOTE: Using a long timeout for the mock server to complete its generation work
        response = requests.get(FLASK_URL + FETCH_PLANS_ENDPOINT, timeout=125) 
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching historical plans: {e}")
        return []

def render_workout_plan(plan):
    """
    Renders the workout plan in an expandable accordion.
    FIXED: Corrected the loop structure and ensured safe access to 'exercises' and exercise properties.
    """
    for day_plan in plan:
        # Use .get() to safely retrieve the 'focus' or default to 'Rest/Recovery'
        focus_text = day_plan.get('focus', 'Rest/Recovery') 
        
        # Safely get the list of exercises, defaulting to an empty list
        exercises = day_plan.get('exercises', []) 

        with st.expander(f"**{day_plan.get('day', 'Unknown Day')}** | Focus: {focus_text}", expanded=False):
            
            if exercises:
                for exercise in exercises:
                    # Safely retrieve all exercise properties
                    name = exercise.get('name', 'N/A')
                    sets = exercise.get('sets', 'N/A')
                    reps = exercise.get('reps', 'N/A')
                    # New field 'notes' is safely accessed
                    notes = exercise.get('notes', 'No specific notes.') 
                    
                    st.markdown(
                        f"""
                        <div style="padding: 10px 0 5px 10px; border-bottom: 1px dashed #444;">
                            **{name}**
                            <br>Sets: `{sets}` | Reps: `{reps}`
                            <br><small>Notes: {notes}</small>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.info("Rest day or active recovery!")

def render_meal_plan(plan):
    """Renders the meal plan with cost estimates in a table-like format."""
    st.subheader("Budget Meal Schedule")
    for day_meal in plan:
        st.markdown(f"#### 🗓️ Day {day_meal.get('day', 'N/A')}")
        
        # Safely iterate over meals list
        for meal in day_meal.get('meals', []):
            # Safely access meal properties
            meal_name = meal.get('name', 'Meal Item')
            cost = meal.get('cost_estimate_in_inr', 'N/A')
            recipe = meal.get('recipe', 'Recipe details unavailable.')
            
            st.markdown(
                f"""
                <div style="border: 1px solid #333; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #4CAF50;">{meal_name}</span>
                    <span style="float: right; font-weight: bold;">Cost: {cost}</span>
                    <br><small>{recipe}</small>
                </div>
                """, 
                unsafe_allow_html=True
            )

# --- SIDEBAR INPUTS ---

with st.sidebar:
    st.header("✨ Personalize Your Plan")
    
    # Inputs (Same as previous versions)
    goal = st.selectbox("Primary Goal", ['Weight Loss', 'Muscle Gain', 'Healthy Maintenance'], index=0, key='goal')
    level = st.selectbox("Current Fitness Level", ['Beginner', 'Intermediate', 'Advanced'], index=1, key='level')
    equipment = st.selectbox("Available Workout Equipment", ['Bodyweight Only', 'Light Weights/Bands', 'Full Gym Access'], index=0, key='equipment')
    intensity = st.selectbox("Schedule Intensity", ['Extremely Limited (15 min/day)', 'Busy Student (45 min max)', 'Flexible (up to 90 min)'], index=1, key='intensity')
    
    st.markdown("---")
    
    budget = st.slider("Weekly Food Budget (INR)", min_value=100, max_value=2000, value=500, step=50, key='budget')
    cuisine = st.selectbox("Cultural/Cuisine Focus", ['Any/Global', 'South Asian', 'Latino', 'American/Comfort'], index=0, key='cuisine')
    workouts_per_week = st.number_input("Workouts Per Week", min_value=1, max_value=6, value=3, step=1, key='workouts_per_week')

    # Data to send to Flask
    payload = {
        "goal": goal,
        "level": level,
        "equipment": equipment,
        "intensity": intensity,
        "budget": budget,
        "cuisine": cuisine,
        "workouts_per_week": workouts_per_week
    }
    
    st.markdown("---")
    generate_button = st.button("✨ Generate Plans With AI", type="primary")

# --- MAIN CONTENT TABS ---

tab1, tab2 = st.tabs(["Current Plan", "History of Plans"])

with tab1:
    if generate_button:
        try:
            with st.status("Connecting to Flask backend...", expanded=True) as status:
                st.write("Analyzing your constraints...")
                
                # Use Streamlit's cache clearing mechanism to immediately update the history tab after generation
                fetch_plans_history.clear() 

                st.write("Sending request to Mock Generator...")
                # POST request to Flask backend
                response = requests.post(FLASK_URL + GENERATE_ENDPOINT, json=payload, timeout=125)
                
                status.update(label="Awaiting structured plan (Simulating delay)...", state="running")
                time.sleep(1) # Simulate the time it takes the mock function to return
                
                response.raise_for_status()
                
                # If successful, response.json() will be the structured plan object
                plan_object = response.json()
                
                # Plan data is nested under 'plan' key in the saved object
                current_plan = plan_object.get('plan')
                
                status.update(label="✅ Plan successfully generated and saved!", state="complete")
            
            # Display the result
            if current_plan:
                st.markdown(f'<h3 class="plan-header">Your 7-Day Personalized Plan</h3>', unsafe_allow_html=True)
                col_workout, col_meal = st.columns(2)
                
                with col_workout:
                    st.subheader("🏋️ Workout Plan")
                    # Check if 'workoutPlan' exists before rendering
                    if 'workoutPlan' in current_plan:
                        render_workout_plan(current_plan['workoutPlan'])
                    else:
                        st.error("Workout plan data is missing.")
                
                with col_meal:
                    st.subheader("🍽️ Meal Plan")
                    # Check if 'mealPlan' exists before rendering
                    if 'mealPlan' in current_plan:
                        render_meal_plan(current_plan['mealPlan'])
                    else:
                        st.error("Meal plan data is missing.")

        except requests.exceptions.RequestException as e:
            st.error(f"Failed to connect to Flask Backend or received a server error: {e}")
            st.warning("Please ensure the Flask backend is running in a separate terminal: `python app.py`")
        except json.JSONDecodeError:
            st.error("Received an invalid response from the backend (not JSON).")
        except Exception as e:
            st.error(f"An unexpected error occurred during generation: {e}")
    
    else:
        st.info("👈 Set your preferences in the sidebar and click 'Generate Plans with AI' to begin!")

with tab2:
    st.subheader("Plan History")
    
    # Fetch and display historical data
    history = fetch_plans_history()
    
    if history:
        st.info(f"Showing {len(history)} saved plans.")
        
        # Display plans in reverse chronological order
        for plan_entry in sorted(history, key=lambda x: x['id'], reverse=True):
            inputs = plan_entry.get('inputs', {})
            plan = plan_entry.get('plan', {'workoutPlan': [], 'mealPlan': []})

            # Format timestamp for better display
            try:
                timestamp_display = time.strftime('%Y-%m-%d %H:%M', time.strptime(plan_entry.get('timestamp', ''), '%Y-%m-%d %H:%M:%S.%f'))
            except ValueError:
                 timestamp_display = plan_entry.get('timestamp', 'N/A')

            expander_label = f"Plan ID {plan_entry.get('id', 'N/A')} | Goal: {inputs.get('goal', 'N/A')} | Budget: ₹{inputs.get('budget', 'N/A')} | Date: {timestamp_display}"
            
            with st.expander(expander_label, expanded=False):
                st.markdown(f"**Inputs Used:** Level={inputs.get('level')}, Equipment={inputs.get('equipment')}, Intensity={inputs.get('intensity')}, Cuisine={inputs.get('cuisine')}")
                
                col_h_workout, col_h_meal = st.columns(2)
                
                with col_h_workout:
                    st.markdown("##### Workout Summary")
                    render_workout_plan(plan.get('workoutPlan', []))
                
                with col_h_meal:
                    st.markdown("##### Meal Summary")
                    render_meal_plan(plan.get('mealPlan', []))
    else:
        st.warning("No plans found in history. Generate a plan first!")
