"""Generate sample test resumes as DOCX files for AutoResume Filter testing."""
import os, sys

BASE_DIR = r"C:\Users\Avinash Shukla\.gemini\antigravity\playground\infrared-granule"
sys.path.insert(0, os.path.join(BASE_DIR, ".venv", "Lib", "site-packages"))
from docx import Document

OUTPUT_DIR = os.path.join(BASE_DIR, "test_resumes")
os.makedirs(OUTPUT_DIR, exist_ok=True)

resumes = [
    {
        "filename": "Priya_Sharma_Python_Dev.docx",
        "content": """Priya Sharma
priya.sharma@email.com
+91-9876543210
Bangalore, India
linkedin.com/in/priyasharma

PROFESSIONAL SUMMARY
Senior Python Developer with 6+ years of experience in building scalable backend systems, REST APIs, and data pipelines. Expertise in Django, Flask, FastAPI, PostgreSQL, Redis, and AWS. Strong background in microservices architecture and CI/CD pipelines.

EXPERIENCE

Senior Python Developer | TechCorp India | Jan 2021 - Present
- Designed and built microservices architecture serving 50M+ requests/day using FastAPI and PostgreSQL
- Implemented real-time data processing pipelines using Apache Kafka and Celery
- Reduced API response times by 40% through query optimization and Redis caching
- Mentored 5 junior developers and conducted code reviews
- Set up CI/CD pipelines using GitHub Actions and Docker

Python Developer | DataSoft Solutions | Jun 2018 - Dec 2020
- Built RESTful APIs using Django REST Framework for e-commerce platform
- Developed automated testing suite with pytest achieving 90% code coverage
- Integrated third-party payment gateways (Razorpay, Stripe)
- Worked with MongoDB and Elasticsearch for search functionality

Junior Developer | StartupXYZ | Jan 2017 - May 2018
- Developed backend services using Flask and SQLAlchemy
- Built data scraping tools using Beautiful Soup and Scrapy
- Assisted in database migration from MySQL to PostgreSQL

EDUCATION
B.Tech Computer Science | VIT University | 2013 - 2017

SKILLS
Python, Django, Flask, FastAPI, PostgreSQL, MySQL, MongoDB, Redis, Docker, Kubernetes, AWS (EC2, S3, Lambda), Git, Linux, REST APIs, GraphQL, Celery, Kafka, pytest, CI/CD"""
    },
    {
        "filename": "Rahul_Verma_Frontend.docx",
        "content": """Rahul Verma
rahul.verma@gmail.com
+91-8765432109
Mumbai, India
linkedin.com/in/rahulverma

PROFESSIONAL SUMMARY
Frontend Developer with 4 years of experience in React.js, Next.js, and modern JavaScript. Passionate about creating responsive, accessible web applications with beautiful user interfaces.

EXPERIENCE

Frontend Developer | WebAgency | Mar 2020 - Present
- Built responsive web applications using React.js and Next.js
- Implemented component libraries using Storybook and styled-components
- Optimized Core Web Vitals scores achieving 95+ on all metrics
- Collaborated with UX designers to implement pixel-perfect designs
- Worked with REST APIs and GraphQL endpoints

Junior Frontend Developer | DigitalFirst | Jun 2018 - Feb 2020
- Developed landing pages and marketing sites using HTML, CSS, JavaScript
- Built interactive dashboards using D3.js and Chart.js
- Implemented responsive designs using CSS Grid and Flexbox

EDUCATION
B.Sc Computer Science | Mumbai University | 2015 - 2018

SKILLS
JavaScript, TypeScript, React.js, Next.js, HTML5, CSS3, Tailwind CSS, Node.js, GraphQL, Git, Figma, Storybook, Jest, Cypress"""
    },
    {
        "filename": "Anita_Kumar_DataScientist.docx",
        "content": """Anita Kumar
anita.kumar@outlook.com
+91-7654321098
Hyderabad, India
linkedin.com/in/anitakumar

PROFESSIONAL SUMMARY
Data Scientist with 5 years of experience in machine learning, NLP, and statistical analysis. Proficient in Python, TensorFlow, PyTorch, and scikit-learn. Experience building production ML models and deploying them at scale.

EXPERIENCE

Senior Data Scientist | AI Labs India | Apr 2021 - Present
- Built NLP models for sentiment analysis and text classification using BERT and GPT-based architectures
- Developed recommendation engine serving 10M+ users, increasing engagement by 25%
- Created automated ML pipelines using MLflow and Kubeflow
- Published 2 research papers on transfer learning for low-resource languages
- Led a team of 3 data scientists on customer churn prediction project

Data Scientist | Analytics Corp | Jul 2019 - Mar 2021
- Built predictive models using scikit-learn, XGBoost, and Random Forests
- Performed A/B testing and statistical analysis for product features
- Created data visualization dashboards using Plotly and Tableau
- Processed large datasets using PySpark and SQL

Data Analyst | InfoTech | Jan 2018 - Jun 2019
- Analyzed business data using Python (pandas, numpy) and SQL
- Built automated reporting pipelines using Python and Airflow
- Created executive dashboards in Tableau

EDUCATION
M.Tech Data Science | IIIT Hyderabad | 2016 - 2018
B.Tech Computer Science | NIT Warangal | 2012 - 2016

SKILLS
Python, TensorFlow, PyTorch, scikit-learn, NLP, BERT, GPT, Hugging Face, pandas, numpy, SQL, PySpark, MLflow, Docker, AWS SageMaker, Tableau, A/B Testing, Statistical Analysis"""
    },
    {
        "filename": "Vikram_Singh_DevOps.docx",
        "content": """Vikram Singh
vikram.singh@protonmail.com
+91-6543210987
Delhi, India
linkedin.com/in/vikramsingh

PROFESSIONAL SUMMARY
DevOps Engineer with 3 years of experience in cloud infrastructure, CI/CD, and container orchestration. Skilled in AWS, Terraform, Docker, Kubernetes, and monitoring tools.

EXPERIENCE

DevOps Engineer | CloudFirst | Sep 2021 - Present
- Managed AWS infrastructure using Terraform and CloudFormation
- Set up Kubernetes clusters for microservices deployment
- Implemented CI/CD pipelines using Jenkins and GitHub Actions
- Configured monitoring using Prometheus, Grafana, and ELK stack
- Reduced deployment time by 60% through automation

Junior DevOps Engineer | ServerStack | Jun 2020 - Aug 2021
- Managed Linux servers and Docker containers
- Set up automated backups and disaster recovery
- Configured Nginx reverse proxy and load balancing
- Wrote Bash and Python scripts for system automation

EDUCATION
B.Tech IT | DTU Delhi | 2016 - 2020

SKILLS
AWS, Terraform, Docker, Kubernetes, Jenkins, GitHub Actions, Linux, Bash, Python, Prometheus, Grafana, Nginx, Ansible, CI/CD, ELK Stack"""
    },
    {
        "filename": "Meera_Patel_FullStack_Python.docx",
        "content": """Meera Patel
meera.patel@email.com
+91-9988776655
Pune, India
linkedin.com/in/meerapatel

PROFESSIONAL SUMMARY
Full Stack Python Developer with 7+ years of experience building web applications, APIs, and data-driven solutions. Deep expertise in Python, Django, React, PostgreSQL, and cloud deployment. Strong advocate for clean code, TDD, and agile methodologies.

EXPERIENCE

Lead Python Developer | FinTech Solutions | Feb 2020 - Present
- Architected and built a payment processing platform handling 1M+ daily transactions using Django and Celery
- Designed RESTful APIs consumed by mobile and web clients (200+ endpoints)
- Implemented real-time fraud detection system using Python ML models (scikit-learn, XGBoost)
- Led migration from monolith to microservices architecture on AWS ECS
- Managed a team of 8 developers, conducted architecture reviews
- Reduced infrastructure costs by 35% through AWS optimization

Senior Python Developer | E-Commerce Corp | Apr 2017 - Jan 2020
- Built inventory management system using Django and PostgreSQL
- Developed async task processing with Celery and RabbitMQ
- Created data analytics dashboards using Python, pandas, and Plotly
- Implemented OAuth2 authentication and role-based access control
- Set up automated testing with pytest (95% coverage)

Python Developer | WebWorks | Jun 2015 - Mar 2017
- Developed web applications using Flask and SQLAlchemy
- Built REST APIs for mobile applications
- Integrated ElasticSearch for full-text search functionality
- Worked with Redis for session management and caching

EDUCATION
M.Tech Software Engineering | COEP Pune | 2013 - 2015
B.Tech Computer Science | MIT Pune | 2009 - 2013

SKILLS
Python, Django, Flask, FastAPI, React, PostgreSQL, MySQL, Redis, Celery, RabbitMQ, Docker, AWS (ECS, Lambda, S3, RDS), Git, CI/CD, pytest, scikit-learn, pandas, Elasticsearch, GraphQL, Microservices, System Design, Team Leadership"""
    },
]

for resume in resumes:
    doc = Document()
    for paragraph in resume["content"].strip().split("\n"):
        p = paragraph.strip()
        if p:
            doc.add_paragraph(p)
    filepath = os.path.join(OUTPUT_DIR, resume["filename"])
    doc.save(filepath)
    print(f"Created: {filepath}")

print(f"\nDone! {len(resumes)} test resumes created in {OUTPUT_DIR}")
