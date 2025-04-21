from django.shortcuts import render, get_object_or_404, redirect
from .models import Job, Application
from .forms import ApplicationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required 
from django.http import HttpResponseForbidden
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import logout
from .forms import ApplicationForm
from .forms import ApplicationStatusForm
from django.views.decorators.http import require_POST
from django.http import HttpResponseRedirect
from .forms import JobForm
from django.core.paginator import Paginator
from .models import UserProfile
from .forms import UserProfileForm

# Job Listing View
def job_list(request):
    jobs = Job.objects.all()

    # Search filter (optional)
    search_query = request.GET.get('q', '')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    # Pagination
    paginator = Paginator(jobs, 5)  # Show 5 jobs per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {'page_obj': page_obj, 'search_query': search_query})

# Job Detail and Application View
def job_detail(request, job_id):
    job = get_object_or_404(Job, pk=job_id)
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()
            return redirect('job_list')  # Redirect to job listing after applying
    else:
        form = ApplicationForm()
    return render(request, 'jobs/job_detail.html', {'job': job, 'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_login')
        else:
            print(form.errors)  # 🔍 Print errors to terminal
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('job_list')
        else:
            return render(request, 'registration/login.html', {'error': 'Invalid credentials'})
    return render(request, 'registration/login.html')

@login_required  # This ensures that only logged-in users can access this view
def user_applications(request):
    # Get the applications for the current logged-in user
    applications = Application.objects.filter(user=request.user)
    
    # Return a template that lists the user's applications
    return render(request, 'jobs/user_applications.html', {'applications': applications})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm

@login_required
def user_profile(request):
    # Get the user's profile, or create it if it doesn't exist
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle the form submission
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()  # Save the UserProfile instance (profile_picture, bio, etc.)
            
            # Save the updated username and email from the form (if needed)
            user = request.user
            if 'username' in request.POST:
                user.username = request.POST['username']
            if 'email' in request.POST:
                user.email = request.POST['email']
            user.save()
            
            return redirect('user_profile')  # Redirect to the profile page after saving
    else:
        form = UserProfileForm(instance=user_profile)

    # Get the user's job applications
    applications = user_profile.user.application_set.all()

    return render(request, 'jobs/user_profile.html', {
        'form': form,
        'applications': applications
    })


def send_application_confirmation(user, job):
    subject = f"Application Confirmation: {job.title}"
    message = f"Dear {user.username},\n\nYou have successfully applied for the job '{job.title}' at {job.company_name}. We will notify you once we review your application."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def user_logout(request):
    logout(request)
    return redirect('user_login')


@login_required
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if the user has already applied
    if Application.objects.filter(job=job, user=request.user).exists():
        return render(request, 'jobs/already_applied.html', {'job': job})

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.job = job
            application.save()
            return redirect('user_applications')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply_to_job.html', {'job': job, 'form': form})

@login_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if job.owner != request.user:
        return HttpResponseForbidden("You don't have permission to manage this job's applications.")

    applications = job.applications.all()

    # Handle status update if form is submitted
    if request.method == 'POST':
        app_id = request.POST.get('app_id')
        application = get_object_or_404(Application, id=app_id)
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect('job_applications', job_id=job.id)

    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications,
        'status_form': ApplicationStatusForm(),  # Blank form for each row
    })

@require_POST
@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    new_status = request.POST.get('status')
    if new_status in dict(Application.STATUS_CHOICES):
        application.status = new_status
        application.save()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.owner = request.user  # Assign the logged-in user as the job owner
            job.save()
            return redirect('job_list')  # Redirect to job list after saving
    else:
        form = JobForm()

    return render(request, 'jobs/create_job.html', {'form': form})