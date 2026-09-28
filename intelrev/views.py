from django.shortcuts import render, redirect
from django.contrib import messages
from intelrev.models.dynamo_user_profile import DynamoUserProfile
from intelrev.services.cognito_service import CognitoService
from intelrev.forms import RegisterForm
from intelrev.decorators import login_required_custom
from intelrevenue.services.revenue_services import RevenueService
from intelrevenue.services.sns_subscription import subscribe_admin_to_alerts
from intelroom.models.dynamo_rooms import Room
from intellodge_core.logger import get_logger
import jwt
from intelrev.services.utility_cognito_jwt_token import verify_cognito_token

log = get_logger(__name__)
user_service = DynamoUserProfile()

def home_redirect(request):
    """Redirect root '/' depending on login state."""
    if request.session.get('is_authenticated'):
        return redirect('home_dashboard')
    return redirect('login')

def register(request):
    form = RegisterForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data['username']
        firstname = form.cleaned_data['firstname']
        lastname = form.cleaned_data['lastname']
        gender = form.cleaned_data['gender']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        role = form.cleaned_data.get("role", "staff").lower()

        cognito = CognitoService()

        # Create Cognito user
        signup_resp = cognito.sign_up(username, password, email)
        if not signup_resp['success']:
            messages.error(request, f"Cognito signup failed: {signup_resp['error']}")
            return redirect('register')

        cognito_sub = signup_resp['user_sub']
        
        confirm_resp = cognito.admin_confirm_sign_up(username)
        if not confirm_resp["success"]:
            messages.warning(request, f"User created but confirmation failed")
            return render(request, 'intelrev/register.html', {'form': form})
        
        # Create DynamoDB profile linked to Cognito
        try:
            profile = user_service.create(
                    cognito_sub=cognito_sub,
                    username=username,
                    firstname=firstname,
                    lastname=lastname,
                    gender=gender,
                    email=email,
                    role=role,
                    )
            
            # Only subscribe admins to SNS alerts
            if role == "admin":
                sns_resp = subscribe_admin_to_alerts(profile)
                if sns_resp.get("success"):
                    messages.info(request, "Admin alert email subscription activated.")
                else:
                    messages.warning(request, "Could not subscribe admin to SNS alerts.")
            
            messages.success(request, f"User created successfully with user id {username}")
            log.info(f"DynamoDB user created: {username}")
            return redirect('login')
                
        except Exception as e:
            log.error(f"Failed to create DynamoDB user: {e}")
            messages.error(request, f"Failed to create user profile in DynamoDB: {e}")
            return render(request, 'intelrev/register.html', {'form': form})
            
    return render(request, 'intelrev/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            cognito = CognitoService()
            login_resp = cognito.sign_in(username, password)

            if not login_resp['success']:
                messages.error(request, f"Login failed: User Not Found")
                log.warning(f"Login failed for {username}: {login_resp.get('error')}")
                return redirect('login')

            # Decode the token
            try:
                id_token = login_resp['id_token']
                claims = verify_cognito_token(id_token)
                cognito_sub = claims["sub"]
            except Exception as e:
                log.error(f"Token verification failed for {username}: {e}", exc_info=True)
                messages.error(request, "Invalid Cognito token.")
                return redirect('login')

            # Get user profile from DynamoDB
            profile = user_service.get_by_cognito_sub(cognito_sub)
            if not profile:
                messages.error(request, "User profile not found in DynamoDB.")
                log.error(f"No DynamoDB profile found for Cognito sub {cognito_sub}")
                return redirect('login')

            # setting the session
            request.session['is_authenticated'] = True
            request.session['username'] = profile['username']
            request.session['email'] = profile['email']
            request.session['role'] = profile.get('role', 'user')
            
            log.info(f"User {username} logged in successfully")
            messages.success(request, f"Welcome, {profile['username']}!")
            
            return redirect('home_dashboard')
        
        except Exception as e:
            log.error(request, f"Login error for user {username}: {e}")
            messages.error(request, f" Login failed: {e}")
            return redirect('login')

    if request.session.get('is_authenticated'):
        return redirect('home_dashboard')

    return render(request, 'intelrev/login.html')


def user_logout(request):
    """Destroy session and redirect to login"""
    try:
        username = request.session.get('username', 'Unknown')
        request.session.flush()
        messages.success(request, "You have been logged out.")
        log.info(f"User {username} logged out successfully")
    except Exception as e:
        log.error(f"Logout error: {e}")
        messages.error(request, "Error logging out")
    return redirect('login')


revenue = RevenueService()

@login_required_custom
def home_dashboard(request):
    room_service = Room()
    rooms_list = room_service.list_all()
    rooms_count = len(rooms_list)
    occupied = len([r for r in rooms_list if r.get("status") == "Occupied"])
    occupancy = round((occupied / rooms_count) * 100, 2) if rooms_count else 0
    
    summary = revenue.revenue_summary()

    context = {
        "username": request.session.get("username"),
        "role": request.session.get("role", "Unknown"),
        "total_rooms": rooms_count,
        "occupied_rooms": occupied,
        "occupancy_rate": occupancy,
        "revenue": summary["total_revenue"],
        "total_bookings": summary["bookings_count"],
    }
    return render(request, "intelrev/dashboard.html", context)