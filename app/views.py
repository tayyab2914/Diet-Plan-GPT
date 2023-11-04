from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import openai
import json
from decouple import config
from django.conf import settings
from app.models import *



openai.api_key = settings.OPENAI_API_KEY

# Create your views here.

def index(request):
    return render(request, 'index.html')

def signup(request):
    if request.method=="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exsit!")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            login(request, user)
            return redirect('/saveddiets')
    return render(request, 'signup.html')

def signin(request):
    if request.user.is_authenticated:
        return redirect('/saveddiets')
    elif request.method=="POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=email, password=password)
        if user is None:
            messages.error(request, "Invalid username or password!")
        else:
            login(request, user)
            return redirect('/saveddiets')
    return render(request, 'signin.html')

@login_required(login_url='/signin')
def signout(request):
    logout(request)
    return redirect('/')


@login_required(login_url='/signin')
def saveddiets(request):
    dietplans = DietPlan.objects.filter(user=request.user)
    return render(request, 'saveddiets.html', context={'dietplans':dietplans})

@login_required(login_url='/signin')
def creatediet(request):
    if request.method=="POST":
        weight = request.POST.get('weight')
        age = request.POST.get('age')
        height = request.POST.get('height')
        restrictions = request.POST.get('restrictions')
        preferences = request.POST.get('preferences')
        slug = generate_diet_plan(request, weight, age, height, restrictions, preferences)
        return redirect(f'dietplan/{slug}')
    return render(request, 'creatediet.html')

@login_required(login_url='/signin')
def dietplan(request, slug):
  dietplan = DietPlan.objects.filter(slug=slug)
  if dietplan.exists():
    dietplan = dietplan[0]
    dietplan = get_json_format(dietplan)
    return render(request, 'dietplan.html', context={'dietplan':dietplan})
  else:
    return redirect('/creatediet')
  
def get_json_format(dietplan):
  json_diet_plan={}
  json_diet_plan['name']=dietplan.name
  days = Day.objects.filter(diet_plan=dietplan)
  day_list=[]
  for day in days:
    days_dict={}
    days_dict['day_number']=day.day_number
    meals_list=[]
    meals = Meal.objects.filter(day=day)
    for meal in meals:
      meals_dict={}
      meals_dict['meal_type']=meal.meal_type
      meals_dict['description']=meal.description
      meals_list.append(meals_dict)
    days_dict['meals']=meals_list
    day_list.append(days_dict)
  json_diet_plan['days']=day_list
  print(json_diet_plan)
  return json_diet_plan



def generate_diet_plan(request, weight, age, height, restrictions, preferences):
    input_format = f'''
    Age: {age}
    Weight: {weight}
    Height: {height} cm
    Restrictions: {restrictions}
    preferences: {preferences}
    Give me a personalized diet plan that helps me to acheive my fitness goal.
    Give me output according to given output earlier. Dont use irrelevant words.
    Give only basic diet which is easily available and common.
    Only give meals according to given input.
    '''
    diet_plan = get_gpt_result(input_format)
    print(diet_plan)
    diet_plan_obj = DietPlan.objects.create(user=request.user, name=diet_plan['diet_plan']['name'])
    for days in diet_plan['diet_plan']['days']:
      day_obj = Day.objects.create(diet_plan=diet_plan_obj, day_number=days['day_number'])
      for meals in days['meals']:
        meal_obj = Meal.objects.create(day=day_obj, meal_type=meals['meal_type'], description=meals['description'])
    return diet_plan_obj.slug

def get_gpt_result(message):
    prompt = []
    prompt.append({"role": "system", "content": SYSTEM_ROLE})
    prompt.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=prompt)
    reply = response["choices"][0]["message"]["content"]
    reply = json.loads(reply)
    return reply

SYSTEM_ROLE = '''
You are my fitness trainer. Provide personalized diet plans based on my data for 7 days.
Make sure to have look on restriction and prefrences.
Your output format for diet plan:
{
  "diet_plan": {
    "name": "Sample Diet Plan",
    "days": [
      {
        "day_number": 1,
        "meals": [
          {
            "meal_type": "breakfast",
            "description": "Oatmeal with fruits and yogurt"
          },
          {
            "meal_type": "lunch",
            "description": "Grilled chicken salad"
          },
          {
            "meal_type": "dinner",
            "description": "Baked salmon with steamed vegetables"
          }
        ]
      },
      {
        "day_number": 2,
        "meals": [
          {
            "meal_type": "breakfast",
            "description": "Scrambled eggs with spinach and whole wheat toast"
          },
          {
            "meal_type": "lunch",
            "description": "Quinoa and black bean bowl"
          },
          {
            "meal_type": "dinner",
            "description": "Stir-fried tofu with brown rice"
          }
        ]
      },
      // ... Repeat for all 7 days
    ]
  }
}

'''