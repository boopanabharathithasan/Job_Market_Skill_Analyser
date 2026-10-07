from flask import Flask, request, jsonify
import csv
import random
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

app = Flask(__name__)

OUTPUT = Path(__file__).with_name("job_market_data.csv")

ROLE_SKILLS = {
    "Data Analyst": ["SQL", "Excel", "Python", "Power BI", "Tableau", "Statistics", "Pandas"],
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy", "SQL"],
    "Python Developer": ["Python", "Git", "SQL", "Docker", "AWS", "NumPy"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Git"],
    "Software Developer": ["Java", "Python", "SQL", "Git", "Docker", "JavaScript"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "NumPy", "Pandas", "AWS", "Docker"],
    "Backend Developer": ["Python", "Java", "SQL", "Node.js", "Docker", "AWS", "Git"],
    "Frontend Developer": ["JavaScript", "HTML", "CSS", "React", "Git"],
    "Full Stack Developer": ["JavaScript", "HTML", "CSS", "React", "Node.js", "SQL", "Git"],
    "Business Analyst": ["Excel", "SQL", "Power BI", "Tableau", "Statistics"],
}

ALL_SKILLS = sorted({skill for skills in ROLE_SKILLS.values() for skill in skills})
ROLES = list(ROLE_SKILLS)
ROLE_ALIASES = {
    "data science": "Data Scientist",
    "data scientist": "Data Scientist",
    "machine learning engineer": "Machine Learning Engineer",
    "ml engineer": "Machine Learning Engineer",
    "ai engineer": "Machine Learning Engineer",
    "artificial intelligence engineer": "Machine Learning Engineer",
    "frontend developer": "Frontend Developer",
    "front end developer": "Frontend Developer",
    "back end developer": "Backend Developer",
    "backend developer": "Backend Developer",
    "full stack developer": "Full Stack Developer",
    "fullstack developer": "Full Stack Developer",
    "software engineer": "Software Developer",
    "python engineer": "Python Developer",
    "web engineer": "Web Developer",
    "business analytics": "Business Analyst",
    "power bi analyst": "Business Analyst",
}
LOCATIONS = [
    "Coimbatore", "Chennai", "Bengaluru", "Hyderabad", "Mumbai",
    "Pune", "Delhi", "Kochi", "Remote",
]
EXPERIENCE = ["Fresher", "1-3 years", "3-5 years", "5+ years"]
EMPLOYMENT = ["Full-time", "Contract", "Internship"]
EDUCATION = ["Bachelor's degree", "Master's degree", "Any degree"]
COMPANIES = [
    "Aster Labs", "BluePeak Systems", "CloudNine Tech", "DataBridge",
    "Evergreen Digital", "FutureWorks", "Nova Solutions", "Orbit Analytics",
]

FIELDNAMES = [
    "Job ID", "Job Title", "Company", "Location", "Experience Level",
    "Employment Type", "Salary LPA", "Skills", "Education", "Posted Date", "Data Type"
]


def generate_dataset(rows=700):
    random.seed(42)
    records = []

    for number in range(1, rows + 1):
        role = random.choice(ROLES)
        core = ROLE_SKILLS[role]
        extras = [skill for skill in ALL_SKILLS if skill not in core]
        selected_skills = list(core)
        selected_skills += random.sample(extras, k=min(random.randint(0, 3), len(extras)))
        random.shuffle(selected_skills)

        records.append({
            "Job ID": f"JOB-{number:04d}",
            "Job Title": role,
            "Company": random.choice(COMPANIES),
            "Location": random.choice(LOCATIONS),
            "Experience Level": random.choice(EXPERIENCE),
            "Employment Type": random.choice(EMPLOYMENT),
            "Salary LPA": round(random.uniform(3.0, 24.0), 1),
            "Skills": ";".join(selected_skills),
            "Education": random.choice(EDUCATION),
            "Posted Date": (date.today() - timedelta(days=random.randint(0, 364))).isoformat(),
            "Data Type": "Synthetic demo data",
        })

    with OUTPUT.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(records)

    return records


def load_data():
    if not OUTPUT.exists():
        return generate_dataset()

    with OUTPUT.open("r", newline="", encoding="utf-8") as csv_file:
        return list(csv.DictReader(csv_file))


def normalize_skill(skill):
    return re.sub(r"[\s_-]+", " ", skill.strip().lower())


def normalize_role_name(role_name):
    return re.sub(r"[\s_-]+", " ", (role_name or "").strip().lower())


def resolve_role_requirements(role_name):
    normalized_target = normalize_role_name(role_name)
    if not normalized_target:
        return None, None

    alias_match = ROLE_ALIASES.get(normalized_target)
    if alias_match:
        return alias_match, ROLE_SKILLS[alias_match]

    for canonical_role, required_skills in ROLE_SKILLS.items():
        if normalize_role_name(canonical_role) == normalized_target:
            return canonical_role, required_skills

    target_tokens = set(normalized_target.split())
    best_canonical = None
    best_score = 0

    for canonical_role, required_skills in ROLE_SKILLS.items():
        canonical = normalize_role_name(canonical_role)
        canonical_tokens = set(canonical.split())
        score = len(target_tokens & canonical_tokens)
        if canonical.startswith(normalized_target) or normalized_target.startswith(canonical):
            score += 3
        if score > best_score:
            best_score = score
            best_canonical = canonical_role

    if best_canonical and best_score > 0:
        return best_canonical, ROLE_SKILLS[best_canonical]

    return None, []


def analyze_profile(role, provided_skills):
    jobs = load_data()
    role_name = (role or "").strip()
    canonical_role = role_name
    for known_role in ROLE_SKILLS:
        if normalize_role_name(known_role) == normalize_role_name(role_name):
            canonical_role = known_role
            break

    chosen_role, role_required = resolve_role_requirements(canonical_role)
    if not chosen_role or not role_required:
        return {
            "role": role_name,
            "user_skills": provided_skills,
            "required_skills": [],
            "matched_skills": [],
            "missing_skills": [],
            "match_percentage": 0,
            "required_count": 0,
            "matched_count": 0,
            "analysis_summary": "Role not recognized. Please choose a predefined role or type a familiar role such as Data Analyst, Python Developer, or AI Engineer.",
            "average_salary": 0,
            "min_salary": 0,
            "max_salary": 0,
            "suggested_upskills": [],
            "demanded_skills": [],
            "top_locations": [],
            "salary_by_location": [],
        }

    canonical_role = chosen_role

    normalized_required = [normalize_skill(skill) for skill in role_required]
    normalized_user = {normalize_skill(skill) for skill in provided_skills if skill.strip()}

    matched = sorted({skill for skill in normalized_required if skill in normalized_user})
    missing = [skill for skill in role_required if normalize_skill(skill) not in normalized_user]
    match_percentage = round((len(matched) / len(normalized_required)) * 100, 2) if normalized_required else 0

    role_jobs = [job for job in jobs if normalize_role_name(job["Job Title"]) == normalize_role_name(canonical_role)]
    if not role_jobs:
        role_jobs = jobs

    salaries = [float(job["Salary LPA"]) for job in role_jobs]
    avg_salary = round(sum(salaries) / len(salaries), 2) if salaries else 0
    min_salary = round(min(salaries), 2) if salaries else 0
    max_salary = round(max(salaries), 2) if salaries else 0

    skill_counter = Counter()
    for job in role_jobs:
        for skill in str(job.get("Skills", "")).split(";"):
            if skill.strip():
                skill_counter[skill.strip()] += 1

    demanded_skills = [
        {"skill": skill, "count": count}
        for skill, count in skill_counter.most_common(10)
    ]

    location_counter = Counter(job["Location"] for job in role_jobs)
    top_locations = [
        {"location": location, "jobs": count}
        for location, count in location_counter.most_common(5)
    ]

    salary_by_location = []
    for location, count in location_counter.most_common(5):
        loc_jobs = [float(job["Salary LPA"]) for job in role_jobs if job["Location"] == location]
        salary_by_location.append({
            "location": location,
            "avg_salary": round(sum(loc_jobs) / len(loc_jobs), 2) if loc_jobs else 0,
            "jobs": len(loc_jobs),
        })

    suggested_upskills = [
        item["skill"]
        for item in demanded_skills
        if normalize_skill(item["skill"]) not in normalized_user
    ][:5]

    if match_percentage >= 80:
        summary = "Strong alignment with the role requirements. Your current skills already match most of the market expectations."
    elif match_percentage >= 60:
        summary = "Good match, but a few priority skills still need strengthening to compete at the top of the market."
    elif match_percentage >= 40:
        summary = "Moderate match. You have a solid base, but can improve by building role-critical skills."
    else:
        summary = "Low match against the role. Focus on filling the biggest skill gaps to become competitive for this role."

    return {
        "role": canonical_role,
        "user_skills": provided_skills,
        "required_skills": role_required,
        "matched_skills": [skill for skill in role_required if normalize_skill(skill) in normalized_user],
        "missing_skills": missing,
        "match_percentage": round(match_percentage, 2),
        "required_count": len(role_required),
        "matched_count": len(matched),
        "analysis_summary": summary,
        "average_salary": avg_salary,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "suggested_upskills": suggested_upskills,
        "demanded_skills": demanded_skills,
        "top_locations": top_locations,
        "salary_by_location": salary_by_location,
    }


@app.route("/")
def home():
    role_options = "".join(f'<option value="{role}">{role}</option>' for role in ROLES)
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Job Market Skill Analyzer Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #eef6ff, #f8ecff 40%, #fff5ee);
                color: #1f2937;
            }
            .container { max-width: 1400px; margin: 0 auto; padding: 30px 20px 60px; }
            .header {
                background: linear-gradient(135deg, #2b3a55, #4a67a1, #7a5cf0);
                color: white; padding: 28px 30px; border-radius: 20px; box-shadow: 0 12px 30px rgba(50, 60, 100, 0.2);
                margin-bottom: 25px;
            }
            h1 { margin: 0; font-size: 2.2rem; }
            .subtitle { margin-top: 10px; color: #e5eeff; }
            .panel {
                background: rgba(255,255,255,0.9);
                border-radius: 18px;
                box-shadow: 0 8px 25px rgba(42,58,90,0.08);
                padding: 22px;
            }
            .form-grid {
                display: grid;
                grid-template-columns: 1.2fr 2fr 1fr auto;
                gap: 16px;
                align-items: end;
            }
            label { display: block; font-weight: bold; margin-bottom: 8px; color: #334155; }
            select, input, button {
                width: 100%; padding: 14px 16px; border-radius: 12px; border: 1px solid #cbd5e1; font-size: 1rem;
            }
            select, input { background: white; }
            button {
                border: none; cursor: pointer; background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white; font-weight: bold; font-size: 1.02rem; box-shadow: 0 8px 20px rgba(59,130,246,0.35);
            }
            .stats-grid {
                margin-top: 25px; display: grid; grid-template-columns: repeat(4, minmax(180px, 1fr)); gap: 18px;
            }
            .stat-card {
                background: linear-gradient(135deg, #ffffff, #f4f7ff);
                border-left: 6px solid #4f46e5; border-radius: 16px; padding: 18px; box-shadow: 0 8px 25px rgba(67, 84, 117, 0.08);
            }
            .stat-card h3 { margin: 0 0 10px; color: #475569; font-size: 0.95rem; }
            .stat-value { font-size: 2rem; font-weight: bold; color: #1e293b; }
            .chart-grid {
                margin-top: 28px; display: grid; grid-template-columns: repeat(2, minmax(300px, 1fr)); gap: 24px;
            }
            .chart-card {
                background: white; border-radius: 16px; padding: 18px; box-shadow: 0 8px 25px rgba(55,65,81,0.08);
            }
            .chart-card h3 { margin-top: 0; margin-bottom: 12px; }
            canvas { width: 100% !important; height: 300px !important; }
            .insights { margin-top: 28px; display: grid; grid-template-columns: 1.1fr 1fr; gap: 20px; }
            .badge-list { list-style: none; padding: 0; margin: 0; }
            .badge-list li { margin-bottom: 10px; padding: 10px 12px; border-radius: 10px; background: #f8fafc; border: 1px solid #e2e8f0; }
            .status-pill {
                display: inline-block; background: #eef2ff; color: #4338ca; padding: 6px 12px; border-radius: 999px; font-weight: bold; margin-bottom: 10px;
            }
            @media (max-width: 900px) {
                .form-grid, .stats-grid, .chart-grid, .insights { grid-template-columns: 1fr; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Skill Match Dashboard</h1>
                <div class="subtitle">Compare your role and skills against market demand.</div>
            </div>

            <div class="panel">
                <form id="analysisForm">
                    <div class="form-grid">
                        <div>
                            <label for="role">Select Role</label>
                            <select id="role" name="role">
                                __ROLE_OPTIONS__
                            </select>
                        </div>
                        <div>
                            <label for="skills">Skills</label>
                            <input id="skills" name="skills" type="text" placeholder="e.g. Python, SQL, Excel" value="Python, SQL, Excel" />
                        </div>
                        <div>
                            <button type="submit">Analyze profile</button>
                        </div>
                    </div>
                </form>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Skill match</h3>
                    <div id="matchValue" class="stat-value">0%</div>
                </div>
                <div class="stat-card">
                    <h3>Avg. salary</h3>
                    <div id="salaryValue" class="stat-value">₹0 LPA</div>
                </div>
                <div class="stat-card">
                    <h3>Top location</h3>
                    <div id="locationValue" class="stat-value">N/A</div>
                </div>
                <div class="stat-card">
                    <h3>Demand gap</h3>
                    <div id="gapValue" class="stat-value">0</div>
                </div>
            </div>

            <div class="chart-grid">
                <div class="chart-card">
                    <h3>Skill Match vs Gap</h3>
                    <canvas id="matchChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Top 10 Demanded Skills</h3>
                    <canvas id="demandChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Top Job Locations</h3>
                    <canvas id="locationChart"></canvas>
                </div>
                <div class="chart-card">
                    <h3>Salary by Location</h3>
                    <canvas id="salaryChart"></canvas>
                </div>
            </div>

            <div class="insights">
                <div class="panel">
                    <div class="status-pill" id="statusPill">Profile status</div>
                    <h3>Analysis Summary</h3>
                    <p id="summaryText">Select a role and enter your skills to review your match percentage and career recommendations.</p>
                </div>
                <div class="panel">
                    <h3>Suggested skills to build</h3>
                    <ul id="skillSuggestions" class="badge-list">
                        <li>Waiting for analysis...</li>
                    </ul>
                </div>
            </div>
        </div>

        <script>
            const chartStore = {};

            function buildChart(id, config) {
                if (chartStore[id]) chartStore[id].destroy();
                chartStore[id] = new Chart(document.getElementById(id), config);
            }

            function renderDashboard(result) {
                document.getElementById('matchValue').textContent = result.match_percentage + '%';
                document.getElementById('salaryValue').textContent = '₹' + result.average_salary + ' LPA';
                document.getElementById('gapValue').textContent = String(result.required_count - result.matched_count);

                const topLocation = result.top_locations && result.top_locations.length ? result.top_locations[0].location : 'N/A';
                document.getElementById('locationValue').textContent = topLocation;
                document.getElementById('summaryText').textContent = result.analysis_summary;

                let statusText = 'Needs improvement';
                if (result.match_percentage >= 80) {
                    statusText = 'Strong match';
                } else if (result.match_percentage >= 60) {
                    statusText = 'Good match';
                } else if (result.match_percentage >= 40) {
                    statusText = 'Moderate match';
                }
                document.getElementById('statusPill').textContent = statusText;

                const suggestions = result.suggested_upskills && result.suggested_upskills.length ? result.suggested_upskills : ['No missing high-priority skills found'];
                document.getElementById('skillSuggestions').innerHTML = suggestions.map(function(skill) {
                    return '<li>' + skill + '</li>';
                }).join('');

                buildChart('matchChart', {
                    type: 'doughnut',
                    data: {
                        labels: ['Matched', 'Missing'],
                        datasets: [{
                            data: [result.matched_count, Math.max(result.required_count - result.matched_count, 0)],
                            backgroundColor: ['#34d399', '#fca5a5'],
                            borderWidth: 0
                        }]
                    },
                    options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
                });

                const demandLabels = result.demanded_skills.map(function(item) { return item.skill; });
                const demandCounts = result.demanded_skills.map(function(item) { return item.count; });
                buildChart('demandChart', {
                    type: 'bar',
                    data: {
                        labels: demandLabels,
                        datasets: [{
                            label: 'Demand count',
                            data: demandCounts,
                            backgroundColor: ['#60a5fa', '#a78bfa', '#fbbf24', '#34d399', '#f472b6', '#fb7185', '#f59e0b', '#22c55e', '#38bdf8', '#c084fc'],
                            borderRadius: 8
                        }]
                    },
                    options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } }
                });

                buildChart('locationChart', {
                    type: 'bar',
                    data: {
                        labels: result.top_locations.map(function(item) { return item.location; }),
                        datasets: [{
                            label: 'Job count',
                            data: result.top_locations.map(function(item) { return item.jobs; }),
                            backgroundColor: ['#818cf8', '#f472b6', '#34d399', '#fbbf24', '#f87171'],
                            borderRadius: 8
                        }]
                    },
                    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
                });

                buildChart('salaryChart', {
                    type: 'line',
                    data: {
                        labels: result.salary_by_location.map(function(item) { return item.location; }),
                        datasets: [{
                            label: 'Avg salary (LPA)',
                            data: result.salary_by_location.map(function(item) { return item.avg_salary; }),
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.2)',
                            tension: 0.35,
                            fill: true
                        }]
                    },
                    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
                });
            }

            document.getElementById('analysisForm').addEventListener('submit', async function (event) {
                event.preventDefault();
                const form = new FormData(this);
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: form
                });
                const result = await response.json();
                renderDashboard(result);
            });

            renderDashboard({
                match_percentage: 0,
                average_salary: 0,
                required_count: 1,
                matched_count: 0,
                top_locations: [{ location: 'N/A', jobs: 0 }],
                analysis_summary: 'Select a role and enter your skills to review your match percentage and career recommendations.',
                suggested_upskills: ['No skills suggested yet'],
                demanded_skills: [{ skill: 'Python', count: 1 }],
                salary_by_location: [{ location: 'N/A', avg_salary: 0 }],
            });
        </script>
    </body>
    </html>
    """
    return template.replace('__ROLE_OPTIONS__', role_options)


@app.route("/analyze", methods=["POST"])
def analyze():
    role = request.form.get("role", "")
    skills_text = request.form.get("skills", "")
    skills = [skill.strip() for skill in skills_text.replace(";", ",").split(",") if skill.strip()]
    result = analyze_profile(role, skills)
    return jsonify(result)


if __name__ == "__main__":
    if not OUTPUT.exists():
        generate_dataset()
    app.run(debug=True)