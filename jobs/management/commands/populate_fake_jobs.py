import random
from django.core.management.base import BaseCommand
from jobs.models import Job

class Command(BaseCommand):
    help = 'Populates the Job model with fake job listings.'

    def handle(self, *args, **kwargs):
        job_titles = ['Software Developer', 'Data Scientist', 'Web Developer', 'Product Manager', 'UX/UI Designer']
        companies = ['TechCorp', 'DataSoft', 'WebSolutions', 'Innovate Ltd', 'DesignPro']
        locations = ['New York', 'San Francisco', 'Austin', 'Los Angeles', 'Chicago']
        descriptions = [
            'Work with cutting-edge technologies to develop innovative software solutions.',
            'Analyze complex data and help businesses make data-driven decisions.',
            'Develop and maintain websites with modern technologies.',
            'Lead product development efforts and define project roadmaps.',
            'Design user-friendly interfaces with a focus on usability and aesthetics.'
        ]
        salary_range = [(70000, 120000), (80000, 130000), (90000, 140000), (100000, 150000), (110000, 160000)]

        # Generate 10 fake jobs
        for _ in range(10):
            title = random.choice(job_titles)
            company_name = random.choice(companies)
            location = random.choice(locations)
            description = random.choice(descriptions)
            salary_min, salary_max = random.choice(salary_range)
            salary = random.randint(salary_min, salary_max)

            job = Job.objects.create(
                title=title,
                company_name=company_name,
                location=location,
                description=description,
                salary=salary
            )

            self.stdout.write(self.style.SUCCESS(f'Created job: {job.title} at {job.company_name}'))
