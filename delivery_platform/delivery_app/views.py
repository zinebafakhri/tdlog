from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .algorithm import optimize_routes_based_on_selection
import json
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')

        try:
            User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('signup')

    return render(request, 'signup.html')  # Chargez votre fichier `signup.html`

@csrf_exempt
def finalize_routes(request):
    """
    Handle user-selected delivery points and optimize routes.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            selected_points = data.get('selectedPoints', [])  # Expecting lat/lng pairs

            # Validate input
            if not all(isinstance(point, list) and len(point) == 2 for point in selected_points):
                return JsonResponse({'error': 'Invalid points format'}, status=400)

            # Optimize routes
            routes = optimize_routes_based_on_selection(selected_points)
            return JsonResponse({'routes': routes}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def home_view(request):
    """
    Render the home page.
    """
    return render(request, 'home.html')

@csrf_exempt
def login_view(request):
    """
    Handle user login. If the credentials are correct, redirect to the itinerary page.
    """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('itinerary')  # Redirect to the itinerary page after login
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

@login_required
def itinerary_view(request):
    """
    Render the itinerary page with default routes.
    """
    routes = optimize_routes_based_on_selection(selected_points=[
        [33.5731, -7.5898],  # Example coordinates for initial points
        [33.5741, -7.5908],
        [33.5751, -7.5918],
        [33.5761, -7.5928],
        [33.5771, -7.5938],
    ])
    routes_json = json.dumps(routes)
    return render(request, 'itinerary.html', {'routes_json': routes_json})

@login_required
@csrf_exempt
def recalculate_routes(request):
    """
    Handle user-added delivery points and recalculate routes dynamically.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Adjust the data structure to convert [{'lat': x, 'lng': y}, ...] into [[x, y], ...]
            raw_points = data.get('points', [])
            selected_points = [[point['lat'], point['lng']] for point in raw_points if 'lat' in point and 'lng' in point]

            logger.info(f"Received new delivery points: {selected_points}")

            # Validate selected points
            if not all(isinstance(point, list) and len(point) == 2 for point in selected_points):
                return JsonResponse({'error': 'Points must be a list of [latitude, longitude] pairs.'}, status=400)

            # Optimize routes based on new points
            routes = optimize_routes_based_on_selection(selected_points)
            logger.info(f"Recalculated routes: {routes}")
            return JsonResponse({'routes': routes})
        except Exception as e:
            logger.error(f"Error recalculating routes: {str(e)}", exc_info=True)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def update_routes(request):
    """
    API endpoint to update routes dynamically based on personnel count.
    """
    try:
        personnel_count = int(request.GET.get('personnel_count', 1))
        if personnel_count <= 0:
            return JsonResponse({'error': 'Invalid personnel count'}, status=400)

        logger.info(f"Personnel count received: {personnel_count}")
        routes = optimize_routes_based_on_selection(delivery_limit=10 // personnel_count)
        return JsonResponse({'routes': routes})
    except Exception as e:
        logger.error(f"Error updating routes: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Failed to update routes. Please try again.'}, status=500)