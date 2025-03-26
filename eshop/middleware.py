import datetime
from django.utils.timezone import now
from django.contrib.auth import logout
from django.shortcuts import redirect


class AutoLogoutMiddleware:
    """
    Middleware to automatically log out users after 5 minutes of inactivity.
    """

    def __init__(self, get_response):
        self.get_response = get_response  # Store the next middleware or view

    def __call__(self, request):
        if request.user.is_authenticated:  # Check if user is logged in
            last_activity = request.session.get('last_activity')

            if last_activity:
                last_activity_time = datetime.datetime.fromisoformat(last_activity)  # Convert stored string to datetime
                current_time = now()  # Get current server time (in Kolkata timezone)

                # Calculate inactivity duration
                inactivity_duration = (current_time - last_activity_time).total_seconds()

                if inactivity_duration > 300:  # 300 seconds = 5 minutes
                    logout(request)  # Log out the user
                    request.session.flush()  # Clear the session
                    return redirect('login')  # Redirect to login page

            # Update last activity timestamp
            request.session['last_activity'] = now().isoformat()

        response = self.get_response(request)
        return response
