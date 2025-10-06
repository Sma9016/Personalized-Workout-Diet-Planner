import json
import time
import requests
import os 
import random 
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURATION (MOCK MODE) ---
PLANS_FILE = 'plans_data.json'

app = Flask(__name__)
# Enable CORS for Streamlit running on a different port/origin
CORS(app)

# --- MOCK RESPONSE DATA (UPDATED FOR DYNAMIC MEALS AND WORKOUTS) ---

def get_mock_plan_data(data):
    """
    Returns a structured plan for testing purposes. The content changes 
    dynamically based on ALL user inputs (Budget, Goal, Cuisine, etc.).
    
    A random variation is introduced here to prevent the output from being 
    identical on every generation.
    """
    goal = data.get('goal', 'Healthy Maintenance')
    budget = data.get('budget', 500) # Daily budget in INR
    cuisine = data.get('cuisine', 'Any/Global')
    level = data.get('level', 'Intermediate')
    equipment = data.get('equipment', 'Bodyweight Only')
    intensity = data.get('intensity', 'Busy Student (45 min max)')
    
    # Randomly select a variation for non-repetition in Workouts
    workout_variation = random.choice([1, 2])
    # Randomly select a variation for non-repetition in Meals
    meal_variation = random.choice([1, 2])
    
    # --- DYNAMIC BUDGET CALCULATIONS ---
    
    weekly_budget_cap = budget * 7
    total_meals = 21 # 7 days * 3 meals
    
    target_avg_meal_cost = weekly_budget_cap / total_meals 
    
    # Weighted cost targets (using a safe margin for 21 meals)
    low_cost_target = int(target_avg_meal_cost * 0.45) # Used heavily for staples/budget
    med_cost_target = int(target_avg_meal_cost * 0.75) # Used for standard dishes
    high_cost_target = int(target_avg_meal_cost * 1.5)  # Used sparingly for premium/protein
    
    # Ensure reasonable minimum costs
    low_cost_target = max(35, low_cost_target) 
    med_cost_target = max(70, med_cost_target)
    high_cost_target = max(180, high_cost_target) 
    
    # Create output string ranges for cost estimates
    cost_low_str = f"₹{low_cost_target-5}-₹{low_cost_target+5}"
    cost_med_str = f"₹{med_cost_target-10}-₹{med_cost_target+10}"
    cost_high_str = f"₹{high_cost_target-25}-₹{high_cost_target+25}"

    # Determine Budget Tier for recipe descriptions
    if budget <= 400:
        budget_tier = "Extreme Savings"
        budget_adj_note = "Focus on simple staples (rice, lentils, minimal spices)."
    elif budget <= 700:
        budget_tier = "Moderate Spending"
        budget_adj_note = "Balanced portions with standard variety and ingredients."
    else:
        budget_tier = "Premium Quality"
        budget_adj_note = "Focus on lean protein, fresh produce, and wider variety."
        
    budget_detail = f"Budget: ₹{budget}/day ({budget_tier}). {budget_adj_note}"
    
    # --- GOAL AND INTENSITY NOTES ---
    
    intensity_note = {
        'Extremely Limited (15 min/day)': "15-minute quick session",
        'Busy Student (45 min max)': "40-minute focused routine",
        'Flexible (up to 90 min)': "75-minute detailed routine"
    }.get(intensity)
    
    if goal == 'Weight Loss':
        goal_note = "Low Calorie Focus, Smaller Portions"
        workout_goal_note = "Primary goal is calorie burn and maintaining muscle mass. (Higher Reps/Circuits)"
        WL_Reps_H = "15-20"
        WL_Reps_L = "10-12"
        WL_Sets = 3
    elif goal == 'Muscle Gain':
        goal_note = "High Protein Focus, Adequate Carbs"
        workout_goal_note = "Primary goal is progressive overload and muscle hypertrophy. (Lower Reps/Heavy)"
        WL_Reps_H = "8-10"
        WL_Reps_L = "6-8"
        WL_Sets = 4
    else:
        goal_note = "Balanced Maintenance Focus"
        workout_goal_note = "Primary goal is general fitness and endurance. (Moderate Reps/Sets)"
        WL_Reps_H = "12-15"
        WL_Reps_L = "8-10"
        WL_Sets = 3


    # --- WORKOUT LOGIC (USING VARIATION FROM PREVIOUS STEP) ---

    workout_key = (level, equipment)
    
    # Simplified workout logic to demonstrate variation functionality
    if workout_key == ('Beginner', 'Bodyweight Only'):
        frequency_note = "3x Week Bodyweight Plan"
        
        # Variation 1
        plan_v1 = [
            {"day": "Monday", "focus": f"Beginner Total Body A (Var {workout_variation}) | {goal}", "exercises": [{"name": "Wall Push-ups", "sets": WL_Sets, "reps": WL_Reps_H, "notes": f"Controlled descent. Total time: {intensity_note}. Goal: {workout_goal_note}"}, {"name": "Bodyweight Squats", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Maintain an upright chest."}]},
            {"day": "Tuesday", "focus": "Rest / Active Recovery", "exercises": [{"name": "Walking/Stretching", "sets": 1, "reps": "30 mins", "notes": "Light pace outside."}]},
            {"day": "Wednesday", "focus": f"Beginner Core/Conditioning (Var {workout_variation}) | {goal}", "exercises": [{"name": "Plank", "sets": WL_Sets, "reps": "45-60 seconds", "notes": "Engage the core tightly."}, {"name": "Glute Bridges", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Squeeze glutes at the top."}]},
            {"day": "Thursday", "focus": "Rest", "exercises": []},
            {"day": "Friday", "focus": f"Beginner Total Body B (Var {workout_variation}) | {goal}", "exercises": [{"name": "Incline Push-ups (on counter)", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Use a stable counter/chair."}, {"name": "Reverse Lunges", "sets": WL_Sets, "reps": f"{WL_Reps_L} per leg", "notes": "Step back slowly."}]},
            {"day": "Saturday", "focus": "Cardio/Stretching", "exercises": [{"name": "Jumping Jacks / High Knees", "sets": 1, "reps": "20 mins", "notes": "Steady interval pace."}]},
            {"day": "Sunday", "focus": "Rest", "exercises": []}
        ]
        
        # Variation 2 - Slightly different exercises/order
        plan_v2 = [
            {"day": "Monday", "focus": f"Beginner Core Focus (Var {workout_variation}) | {goal}", "exercises": [{"name": "Crunches", "sets": WL_Sets, "reps": "20", "notes": f"Focus on core squeeze. Total time: {intensity_note}. Goal: {workout_goal_note}"}, {"name": "Mountain Climbers", "sets": WL_Sets, "reps": "45 seconds", "notes": "Maintain a straight back."}]},
            {"day": "Tuesday", "focus": f"Beginner Total Body A (Var {workout_variation}) | {goal}", "exercises": [{"name": "Assisted Squats (Holding Chair)", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Focus on range of motion."}, {"name": "Push-up on Knees", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Keep core engaged."}]},
            {"day": "Wednesday", "focus": "Active Recovery", "exercises": [{"name": "Yoga/Mobility Flow", "sets": 1, "reps": "25 mins", "notes": "Gentle stretching."}]},
            {"day": "Thursday", "focus": f"Beginner Total Body B (Var {workout_variation}) | {goal}", "exercises": [{"name": "Pike Push-ups (for shoulders)", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Aim butt high in the air."}, {"name": "Step-ups", "sets": WL_Sets, "reps": f"{WL_Reps_H} per leg", "notes": "Use a low, stable step."}]},
            {"day": "Friday", "focus": "Rest", "exercises": []},
            {"day": "Saturday", "focus": "Cardio/Stretching", "exercises": [{"name": "High Knees", "sets": 1, "reps": "15 mins", "notes": "Increase intensity."}]},
            {"day": "Sunday", "focus": "Full Rest", "exercises": []}
        ]
        
        workout_plan = plan_v1 if workout_variation == 1 else plan_v2

    # Fallback/Other Workouts logic (simplified)
    else: 
         frequency_note = "4x Week Hybrid Plan (Advanced/Equipment)"
         
         # Variation 1 (Fallback/Gym)
         plan_v1 = [
            {"day": "Monday", "focus": f"Hybrid Mix A (Var {workout_variation}) | {goal}", "exercises": [{"name": "Barbell Rows", "sets": WL_Sets, "reps": WL_Reps_L, "notes": f"Heavy lift focus. Goal: {workout_goal_note}"}, {"name": "Dumbbell Press", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Focus on controlled tempo."}]},
            {"day": "Tuesday", "focus": "Lower Body", "exercises": [{"name": "Barbell Squats", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Prioritize depth."}, {"name": "Leg Extensions", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Focus on quad isolation."}]},
            {"day": "Wednesday", "focus": "Rest / Active Recovery", "exercises": [{"name": "Walking/Stretching", "sets": 1, "reps": "45 mins", "notes": "Light pace."}]},
            {"day": "Thursday", "focus": f"Hybrid Circuit Training (Var {workout_variation}) | {goal}", "exercises": [{"name": "Overhead Press (DB)", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Keep core tight."}, {"name": "Weighted Step-ups", "sets": WL_Sets, "reps": f"{WL_Reps_H} per leg", "notes": "Use a low, stable box."}]},
            {"day": "Friday", "focus": "Core & Cardio", "exercises": [{"name": "Plank with DB Drag", "sets": WL_Sets, "reps": "10 per side", "notes": "Minimize hip rotation."}, {"name": "Jump Rope (Mock)", "sets": 1, "reps": "20 mins", "notes": "Light, steady pace."}]},
            {"day": "Saturday", "focus": "Full Body Finishers", "exercises": [{"name": "Burpees (Modified)", "sets": WL_Sets, "reps": WL_Reps_L, "notes": "Reduce jumps if needed."}, {"name": "Calf Raises (Bodyweight)", "sets": WL_Sets, "reps": WL_Reps_H, "notes": "Hold onto a wall for balance."}]},
            {"day": "Sunday", "focus": "Rest", "exercises": []}
        ]
         
         # Variation 2 (Fallback/Gym - PPL Focus)
         plan_v2 = [
            {"day": "Monday", "focus": f"PULL Day (Var {workout_variation}) | {goal}", "exercises": [{"name": "Lat Pulldowns", "sets": 4, "reps": WL_Reps_L, "notes": f"Squeeze the back. Goal: {workout_goal_note}"}, {"name": "Bicep Curls (Cable)", "sets": 3, "reps": WL_Reps_H, "notes": "Controlled tempo."}]},
            {"day": "Tuesday", "focus": f"PUSH Day (Var {workout_variation}) | {goal}", "exercises": [{"name": "Incline DB Press", "sets": 4, "reps": WL_Reps_L, "notes": "Target upper chest."}, {"name": "Tricep Pushdowns", "sets": 3, "reps": WL_Reps_H, "notes": "Full extension."}]},
            {"day": "Wednesday", "focus": f"LEGS Day (Var {workout_variation}) | {goal}", "exercises": [{"name": "Leg Press", "sets": 4, "reps": WL_Reps_L, "notes": "Use moderate weight."}, {"name": "Romanian Deadlifts (DB)", "sets": 3, "reps": WL_Reps_H, "notes": "Stretch hamstrings."}]},
            {"day": "Thursday", "focus": "Rest", "exercises": []},
            {"day": "Friday", "focus": f"Upper Body Volume (Var {workout_variation}) | {goal}", "exercises": [{"name": "Seated Cable Rows", "sets": 3, "reps": WL_Reps_H, "notes": "Focus on stretch and contraction."}, {"name": "Lateral Raises (DB)", "sets": 3, "reps": WL_Reps_H, "notes": "Focus on slow, controlled movement."}]},
            {"day": "Saturday", "focus": f"Lower Body Conditioning (Var {workout_variation}) | {goal}", "exercises": [{"name": "Box Jumps/Step-ups (Plyo)", "sets": 3, "reps": "15-20", "notes": "Focus on explosive power (if able)."}, {"name": "Abdominal Machine Crunches", "sets": 3, "reps": WL_Reps_H, "notes": "Squeeze abs hard."}]},
            {"day": "Sunday", "focus": "Full Rest", "exercises": []}
        ]

         workout_plan = plan_v1 if workout_variation == 1 else plan_v2


    # --- MEAL LOGIC (UPDATED WITH VARIATIONS) ---
    
    if cuisine == 'South Asian':
        # Variation 1: Focus on classic dal/rice and convenience
        plan_v1 = [
            {"day": "Monday", "meals": [{"name": "B: Poha/Upma (V1)", "recipe": f"Quick Poha ({budget_detail} | {goal_note})", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Simple Dal", "recipe": "Yellow Dal and 2 rotis. Maximize cheap protein source.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Khichdi", "recipe": "Vegetable Khichdi with curd. Light and easy on the budget.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Eggs/Banana", "recipe": f"Boiled Eggs (2) and a banana ({goal_note}).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Chana Masala", "recipe": "Chana Masala (chickpeas) with less rice/1 roti. High fiber.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Mung Soup (V1)", "recipe": f"Mung bean soup, very light. ({budget_adj_note})", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Oats", "recipe": "Salty/Sweet Oats (High Fiber).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Chana", "recipe": "Leftover Chana Masala with 1 roti (Budget Day).", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Mock Paneer/Tofu", "recipe": f"High quality Paneer/Tofu dish with 2 rotis (Premium Protein).", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Toast/Peanut", "recipe": "Toast with peanut butter (protein boost).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Curd Rice (V1)", "recipe": "Curd Rice or simple vegetable sandwich.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Sambar/Rice", "recipe": "Lentil soup (Sambar) with steamed rice.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Friday", "meals": [{"name": "B: Smoothie", "recipe": f"Banana and water/milk smoothie ({goal_note} focus).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Rajma", "recipe": "Rajma (Kidney beans) curry with plain rice (High Protein).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftover Rajma", "recipe": "Leftover Rajma (Kidney beans) with curd.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Poha/Upma (V1)", "recipe": "Rava Upma or Poha with peanuts.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Deluxe Mock Meat Curry", "recipe": f"Small portion of high-quality mock meat curry ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Veg Stir-fry", "recipe": "Mixed vegetable stir-fry with rice.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Paratha", "recipe": "Plain Paratha or 2 plain rotis with pickle.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Veg Biryani", "recipe": "Simple vegetable pulao/biryani.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftovers", "recipe": f"Light dinner of fruit or leftovers ({budget_detail}).", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        # Variation 2: Focus on variety like Dosa/Idli (Mock), and different bean types
        plan_v2 = [
            {"day": "Monday", "meals": [{"name": "B: Idli/Sambar (V2)", "recipe": f"Idli (2) with Sambar/Chutney ({budget_detail} | {goal_note})", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Moong Dal", "recipe": "Moong Dal (split) and rice. Light and easy.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Mixed Bean Curry", "recipe": "Mixed beans (like lobia/white chhole) curry and 1 roti.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Whole Wheat Toast", "recipe": f"Toast (2 slices) with light spread ({goal_note}).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Bean Curry", "recipe": "Leftover Mixed Bean Curry.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Paneer Bhurji", "recipe": f"Scrambled paneer (Bhurji) with fresh salad. ({budget_adj_note})", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Eggs/Vegetables", "recipe": "Scrambled eggs (2) with sautéed vegetables.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Vegetable Curry", "recipe": "Seasonal vegetable curry with 2 rotis.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Curd/Fruit", "recipe": f"Large bowl of curd/yogurt with seasonal fruit (Light Dinner).", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Dosa (Mock)", "recipe": "Simple dosa/cheela made from lentil batter.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Dal Fry", "recipe": "Simple Dal Fry with rice.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Vegetable Stew", "recipe": "Thick vegetable stew (Ishtu) and 1 roti.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Friday", "meals": [{"name": "B: Sprouts Salad", "recipe": f"Sprouted Mung beans salad (High Protein) ({goal_note} focus).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Chhole", "recipe": "Chhole (Garbanzo beans) with 1 roti.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftover Chhole", "recipe": "Leftover Chhole (Garbanzo beans) as a light soup.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Sweet Potato", "recipe": "Boiled sweet potato with a dash of spice.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Mock Chicken Curry", "recipe": f"Mock chicken/meat curry ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Raita/Rice", "recipe": "Light vegetable Raita (curd mix) with rice.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Paratha", "recipe": "Aloo Paratha (potato filling) or Onion Paratha.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Veg Pulao", "recipe": "Simple vegetable pulao/biryani.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftovers (V2)", "recipe": f"Light dinner of fruit or leftover Dal ({budget_detail}).", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        meal_plan = plan_v1 if meal_variation == 1 else plan_v2

    elif cuisine == 'Latino':
        # Variation 1: Focus on classic beans, rice, and simple tacos/bowls
        plan_v1 = [
            {"day": "Monday", "meals": [{"name": "B: Huevos (Mock) (V1)", "recipe": f"Scrambled eggs with a dash of salsa ({budget_adj_note}).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Rice & Beans", "recipe": "Simple Rice and Black Beans (Staple, {budget_tier}).", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Burrito Bowl", "recipe": f"Budget burrito bowl (high protein beans, less rice).", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Oatmeal", "recipe": "Oatmeal with cinnamon and milk.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Beans", "recipe": "Leftover Rice and Black Beans.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Tacos (Veg)", "recipe": f"Simple corn tacos (3) with potato/bean filling ({goal_note}).", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Toast/Avocado", "recipe": f"Toast with mock guacamole (mashed avocado - {budget_adj_note}).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Budget Chili", "recipe": "Lentil/bean chili (protein source).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftover Chili", "recipe": "Leftover chili with a side of rice.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Fruit & Yogurt", "recipe": "Simple fruit (banana) and curd/yogurt.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Veggie Soup", "recipe": "Budget Latin-style vegetable soup.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Mock Empanadas", "recipe": f"2 Mock empanadas (baked, potato/bean filling - {goal_note}).", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Friday", "meals": [{"name": "B: Toast/Peanut", "recipe": "Toast with peanut butter and banana (Energy).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Rice & Beans", "recipe": "Fresh batch of Rice and Black Beans.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Mock Tostadas", "recipe": "Fried flat corn tortillas with beans.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Pancakes", "recipe": "Simple pancakes (budget flour/water).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Beans", "recipe": "Leftover Rice and Black Beans.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Premium Mock Tacos", "recipe": f"4 Mock Chicken or Beef Tacos ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Eggs/Toast", "recipe": "Scrambled Eggs (2) and toast.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Protein Bowl", "recipe": f"High Protein Bowl with mock fish/steak ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Leftovers", "recipe": "Light dinner of fruit or leftovers.", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        # Variation 2: Focus on soups, sweet potato, and different preparations
        plan_v2 = [
            {"day": "Monday", "meals": [{"name": "B: Arepas (Mock) (V2)", "recipe": f"2 simple corn meal arepas (budget-friendly corn base).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Lentil Soup", "recipe": "Big bowl of spicy lentil soup with vegetables.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Chicken Fajita Bowl (Mock)", "recipe": f"Mock chicken strips with peppers and onions.", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Fruit/Nuts", "recipe": "Banana and a small handful of peanuts.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Fajita Mix", "recipe": "Leftover Fajita mix served over rice.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Quesadillas (Mock)", "recipe": f"2 corn tortillas with budget cheese/bean filling ({goal_note}).", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Eggs/Black Beans", "recipe": f"2 scrambled eggs with a scoop of black beans ({budget_adj_note}).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Refried Beans", "recipe": "Refried beans (canned/homemade) with plain rice.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Fish Tacos (Mock)", "recipe": "2 Mock Fish Tacos with light cabbage slaw.", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Oatmeal", "recipe": "Oatmeal with mock milk and brown sugar.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Sweet Potato", "recipe": "Baked sweet potato with a dash of spice.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Chicken Soup (Mock)", "recipe": "Large bowl of mock chicken and rice soup.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Friday", "meals": [{"name": "B: Toast/Avocado", "recipe": "Toast with mock guacamole (mashed avocado).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Budget Chili (V2)", "recipe": "Red kidney bean chili with a small side of corn chips.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Leftover Chili", "recipe": "Leftover chili (no chips).", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Fruit & Yogurt", "recipe": "Simple fruit (apple) and curd/yogurt.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Black Bean Burger (Mock)", "recipe": f"Mock black bean burger on a simple bun ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Tortilla Soup (Mock)", "recipe": "Light vegetable tortilla soup.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Pancakes/Waffles", "recipe": "Simple pancakes (budget flour/water).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Deluxe Mock Meat", "recipe": f"Mock steak/fish with grilled vegetables ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Light Salad", "recipe": "Simple green salad with vinaigrette.", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        meal_plan = plan_v1 if meal_variation == 1 else plan_v2
    else:
        # Any/Global (Default) / American/Comfort
        # Variation 1: Focus on classic comfort and convenience
        plan_v1 = [
            {"day": "Monday", "meals": [{"name": "B: Cereal (V1)", "recipe": "Budget brand cereal with milk (Low Sugar).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: PB&J", "recipe": f"Peanut butter and jelly sandwich ({goal_note}, {budget_adj_note})", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Budget Pasta", "recipe": f"Pasta with simple tomato sauce ({budget_adj_note}).", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Eggs/Toast", "recipe": f"Scrambled Eggs (2) and whole-wheat toast ({goal_note}).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Leftover Pasta", "recipe": "Leftover pasta from Monday.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Simple Soup", "recipe": "Canned vegetable soup (mock equivalent, light).", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Oatmeal", "recipe": "Oatmeal with sugar/honey.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Tuna Sandwich", "recipe": f"Tuna salad sandwich (high protein, {budget_adj_note}).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Mock Pizza", "recipe": f"Slice of frozen pizza (budget brand, comfort food). ({budget_detail})", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Toast/Jam", "recipe": "Toast with butter and jam.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Tuna", "recipe": "Leftover tuna salad with crackers.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Rice & Veg", "recipe": "Simple rice and frozen vegetable mix.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Friday", "meals": [{"name": "B: Pancakes", "recipe": "Pancakes/Waffles (budget flour/water).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Grilled Cheese", "recipe": "Grilled cheese sandwich (low-cost cheese).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Chicken/Salmon (Mock)", "recipe": f"Mock baked lean chicken or salmon fillet ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Fruit Smoothie", "recipe": "Fruit smoothie (banana and water/milk).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Chicken Salad", "recipe": f"Mock chicken/paneer salad (Protein source - {goal_note}).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Tacos (Global)", "recipe": "Simple soft tacos with ground filling and beans.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Eggs/Bacon Mock", "recipe": "Scrambled eggs and mock bacon/sausage (e.g., soy).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Premium Burger (Mock)", "recipe": f"Mock grass-fed burger on a quality bun ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Leftovers (V1)", "recipe": "Light dinner of fruit or leftovers.", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        # Variation 2: Focus on stir-fries, hummus, and quick, healthy options
        plan_v2 = [
            {"day": "Monday", "meals": [{"name": "B: Yogurt Parfait (V2)", "recipe": "Yogurt with budget granola and fruit.", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Hummus & Pita (Mock)", "recipe": f"Budget hummus with pita bread/crackers ({goal_note}, {budget_adj_note})", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Chicken Stir-fry (Mock)", "recipe": f"Mock chicken stir-fry with rice and low-cost veg.", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Tuesday", "meals": [{"name": "B: Hard-Boiled Eggs", "recipe": f"Hard-boiled eggs (3) and an apple ({goal_note}).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Leftover Stir-fry", "recipe": "Leftover stir-fry from Monday.", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Grilled Cheese & Soup", "recipe": "Grilled cheese sandwich and canned vegetable soup.", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Wednesday", "meals": [{"name": "B: Peanut Butter Toast", "recipe": "Whole-wheat toast with peanut butter (high energy).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Chickpea Salad", "recipe": "Chickpea and vegetable salad (mayo-free).", "cost_estimate_in_inr": cost_med_str}, {"name": "D: Lentil Soup & Bread", "recipe": f"Big bowl of lentil soup with a slice of bread. ({budget_detail})", "cost_estimate_in_inr": cost_low_str}]},
            {"day": "Thursday", "meals": [{"name": "B: Cereal (V2)", "recipe": "Oatmeal or budget muesli.", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Leftover Soup", "recipe": "Leftover lentil soup.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Turkey Sandwich (Mock)", "recipe": "Mock turkey/chicken slices on whole wheat.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Friday", "meals": [{"name": "B: Fruit Smoothie", "recipe": "Banana and spinach smoothie (hidden veg).", "cost_estimate_in_inr": cost_med_str}, {"name": "L: Mock Chicken Wrap", "recipe": "Mock chicken salad wrap in a tortilla.", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Pasta & Veg", "recipe": "Pasta with mock ground meat and frozen veg.", "cost_estimate_in_inr": cost_high_str}]},
            {"day": "Saturday", "meals": [{"name": "B: Eggs/Sausage Mock", "recipe": "Scrambled eggs and mock sausage (e.g., soy).", "cost_estimate_in_inr": cost_high_str}, {"name": "L: Leftover Pasta", "recipe": f"Leftover pasta for lunch.", "cost_estimate_in_inr": cost_low_str}, {"name": "D: Baked Potato", "recipe": "Baked potato with beans/budget cheese topping.", "cost_estimate_in_inr": cost_med_str}]},
            {"day": "Sunday", "meals": [{"name": "B: Pancakes/Waffles (V2)", "recipe": "Waffles with syrup (treat day).", "cost_estimate_in_inr": cost_low_str}, {"name": "L: Classic Burger (Mock)", "recipe": f"Classic Mock Beef Burger on a bun ({budget_detail}).", "cost_estimate_in_inr": cost_high_str}, {"name": "D: Light Salad", "recipe": "Simple mixed green salad.", "cost_estimate_in_inr": cost_low_str}]}
        ]
        
        meal_plan = plan_v1 if meal_variation == 1 else plan_v2


    return {
        "workoutPlan": workout_plan,
        "mealPlan": meal_plan
    }

# --- CRUD HELPER FUNCTIONS (UNCHANGED) ---

def load_plans():
    """Loads plans from the JSON file."""
    if os.path.exists(PLANS_FILE):
        with open(PLANS_FILE, 'r') as f:
            try:
                # Load existing data. Return empty list if file is empty or corrupted.
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_plans_to_file(plans):
    """Saves plans to the JSON file."""
    # Ensure the directory exists if needed, though for a local file it's usually fine
    with open(PLANS_FILE, 'w') as f:
        json.dump(plans, f, indent=4)

# --- AI SCHEMA AND PROMPT FUNCTIONS (REMOVED for brevity and mock use) ---

def call_gemini_api(prompt):
    """
    ***MOCK MODE ACTIVE***: This function now returns structured data for testing 
    instead of calling the external Gemini API.
    """
    
    # In mock mode, we use the user inputs to make the mock response seem dynamic
    data = request.json
    time.sleep(1) # Simulate a short delay to show the loading screen works
    return get_mock_plan_data(data)

# --- FLASK ROUTES ---

@app.route('/generate_plan', methods=['POST'])
def generate_plan():
    """Endpoint to receive user data, generate the plan via AI MOCK, and SAVE the result (C - Create)."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # 2. Generate Plan using MOCK
        plan_data = call_gemini_api(None) # Call the mock function
        
        # 3. Save the generated structured plan (CRUD LOGIC)
        plans = load_plans()
        plan_id = int(time.time() * 1000)
        new_plan = {
            "id": plan_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "inputs": data,
            "plan": plan_data
        }
        plans.append(new_plan)
        save_plans_to_file(plans)

        # 4. Return the full saved object
        return jsonify(new_plan)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({
            "error": f"Internal Server Error. The mock service failed. Error: {e}",
            "status": "500 Internal Server Error"
        }), 500

@app.route('/get_plans', methods=['GET'])
def get_plans():
    """Endpoint to read all saved plans (R - Read)."""
    try:
        plans = load_plans()
        # Returns all plans in the file
        return jsonify(plans)
    except Exception as e:
        print(f"Failed to retrieve plans: {e}")
        return jsonify({"error": f"Failed to retrieve plans: {e}"}), 500


@app.route('/', methods=['GET'])
def home():
    """Simple check to ensure the server is running."""
    return "Flask Backend is running! (MOCK MODE ACTIVE)"

if __name__ == '__main__':
    # Flask is set to run on port 5000 by default
    app.run(host='127.0.0.1', port=5000)
