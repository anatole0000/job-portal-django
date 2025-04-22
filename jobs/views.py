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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .forms import JobSearchForm
from .models import Job, SavedJob

# Job Listing View
# views.py
from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Job
from .forms import JobSearchForm

def job_list(request):
    jobs = Job.objects.all()

    # Search filter (optional)
    search_query = request.GET.get('q', '')
    if search_query:
        jobs = jobs.filter(title__icontains=search_query)

    # Filter by location
    location_filter = request.GET.get('location', '')
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)

    # Filter by salary range
    salary_min = request.GET.get('salary_min', None)
    salary_max = request.GET.get('salary_max', None)
    if salary_min:
        jobs = jobs.filter(salary_min__gte=salary_min)
    if salary_max:
        jobs = jobs.filter(salary_max__lte=salary_max)

    # Filter by experience level
    experience_level = request.GET.get('experience_level', '')
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)

    # Filter by job type
    job_type = request.GET.get('job_type', '')
    if job_type:
        jobs = jobs.filter(job_type=job_type)

    # Pagination
    paginator = Paginator(jobs, 5)  # Show 5 jobs per page
    page_number = request.GET.get('page')  # Get the current page number from the URL
    page_obj = paginator.get_page(page_number)

    return render(request, 'jobs/job_list.html', {
        'page_obj': page_obj, 
        'search_query': search_query,
        'location_filter': location_filter,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'experience_level': experience_level,
        'job_type': job_type
    })


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

@login_required
def job_matching(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_skills = user_profile.skills.split(',')  # assuming skills are stored as comma-separated values
    
    # Get all jobs and filter by keyword match
    jobs = Job.objects.all()
    matched_jobs = []

    for job in jobs:
        job_skills = job.skills_required.split(',')  # assuming job skills are stored as comma-separated values
        match_count = sum(1 for skill in user_skills if skill.strip().lower() in [s.lower() for s in job_skills])
        
        # If there is at least one match, add to matched_jobs
        if match_count > 0:
            matched_jobs.append((job, match_count))
    
    # Sort jobs by the number of matches (highest match first)
    matched_jobs.sort(key=lambda x: x[1], reverse=True)

    return render(request, 'jobs/job_matching.html', {'matched_jobs': matched_jobs})

@login_required
def recommend_jobs(request):
    user_profile = UserProfile.objects.get(user=request.user)
    user_skills = user_profile.skills  # Assuming skills are stored as a string of keywords

    # Get all jobs and their descriptions
    jobs = Job.objects.all()
    job_descriptions = [job.description for job in jobs]

    # Combine user skills into a document for comparison
    documents = job_descriptions + [user_skills]  # Add user skills as the last document

    # Use TF-IDF to vectorize the job descriptions and user skills
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(documents)

    # Compute cosine similarity between the user profile and each job
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

    # Sort the jobs by similarity score
    similar_jobs = [(jobs[i], cosine_similarities[0][i]) for i in range(len(jobs))]
    similar_jobs.sort(key=lambda x: x[1], reverse=True)

    return render(request, 'jobs/job_recommendations.html', {'similar_jobs': similar_jobs})

def save_application(request, job_id):
    job = Job.objects.get(id=job_id)
    if request.method == 'POST':
        # Save the application with 'pending' status
        application, created = Application.objects.get_or_create(user=request.user, job=job, status='pending')
        return redirect('job_list')  # Redirect to job list after saving
    return render(request, 'jobs/save_application.html', {'job': job})


@login_required
def save_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Check if the job is already saved by the user
    if not SavedJob.objects.filter(user=request.user, job=job).exists():
        SavedJob.objects.create(user=request.user, job=job)

    return redirect('job_list')  # Redirect back to the job list page