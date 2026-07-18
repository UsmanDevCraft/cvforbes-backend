import pytest
from app.schemas.tailored_cv import (
    CandidateProfile,
    FinalTailoredOutput,
    TailoredCV,
    WorkExperience,
    Education,
    Project,
    Certification,
    Award,
    Publication,
    VolunteerExperience,
    Language,
    ResumeLink,
    ResumeAnalytics,
)


@pytest.fixture
def sample_candidate_profile() -> CandidateProfile:
    return CandidateProfile(
        full_name="John Doe",
        email="john@example.com",
        phone="123-456-7890",
        links=[
            ResumeLink(
                type="github", text="GitHub", url="https://github.com/johndoe"
            )
        ],
        professional_summary="Experienced Software Engineer with a focus on web apps.",
        skills=["Python", "FastAPI", "Docker"],
        technical_skills=["Python", "SQL", "Git"],
        soft_skills=["Communication", "Teamwork"],
        tools_and_technologies=["Jira", "VSCode"],
        experience=[
            WorkExperience(
                company="Company A",
                role="Software Developer",
                duration="June 2021 - Present",
                bullet_points=[
                    "Developed FastAPI services.",
                    "Maintained legacy apps.",
                ],
            )
        ],
        projects=[
            Project(
                name="Project Alpha",
                description="A cool backend project",
                technologies=["FastAPI", "Postgres"],
                duration="2 months",
                link="https://github.com/johndoe/alpha",
            )
        ],
        education=[
            Education(
                institution="University X",
                degree="BS Computer Science",
                duration="2016 - 2020",
            )
        ],
        certifications=[
            Certification(
                name="AWS Solutions Architect", issuer="AWS", year="2022"
            )
        ],
        awards=[Award(title="Best Innovator", issuer="Company A", year="2023")],
        publications=[
            Publication(
                title="Scaling APIs",
                publisher="Tech Journal",
                year="2023",
                link="https://journal.com/scaling",
            )
        ],
        volunteer_experience=[
            VolunteerExperience(
                organization="Code for Good",
                role="Mentor",
                duration="2021",
                bullet_points=["Mentored bootcamp students."],
            )
        ],
        languages=[Language(language="English", proficiency="Native")],
    )


@pytest.fixture
def sample_final_tailored_output() -> FinalTailoredOutput:
    return FinalTailoredOutput(
        cv=TailoredCV(
            full_name="John Doe",
            email="john@example.com",
            phone="123-456-7890",
            links=[
                ResumeLink(
                    type="github",
                    text="GitHub",
                    url="https://github.com/johndoe",
                )
            ],
            professional_summary=(
                "Tailored Summary: Highly qualified Backend Engineer specializing"
                " in Python and FastAPI."
            ),
            skills=["Python", "FastAPI", "Docker", "REST APIs"],
            technical_skills=["Python", "SQL", "Git", "Postgres"],
            soft_skills=["Communication", "Teamwork", "Problem Solving"],
            tools_and_technologies=["Jira", "VSCode"],
            experience=[
                WorkExperience(
                    company="Company A",
                    role="Software Developer",
                    duration="June 2021 - Present",
                    bullet_points=[
                        "Designed and optimized FastAPI microservices.",
                        "Collaborated with team on backend scaling.",
                    ],
                )
            ],
            projects=[
                Project(
                    name="Project Alpha",
                    description=(
                        "Designed and deployed a highly scalable FastAPI app."
                    ),
                    technologies=["FastAPI", "Postgres"],
                    duration="2 months",
                    link="https://github.com/johndoe/alpha",
                )
            ],
            education=[
                Education(
                    institution="University X",
                    degree="BS Computer Science",
                    duration="2016 - 2020",
                )
            ],
            certifications=[
                Certification(
                    name="AWS Solutions Architect", issuer="AWS", year="2022"
                )
            ],
            awards=[
                Award(title="Best Innovator", issuer="Company A", year="2023")
            ],
            publications=[
                Publication(
                    title="Scaling APIs",
                    publisher="Tech Journal",
                    year="2023",
                    link="https://journal.com/scaling",
                )
            ],
            volunteer_experience=[
                VolunteerExperience(
                    organization="Code for Good",
                    role="Mentor",
                    duration="2021",
                    bullet_points=["Mentored bootcamp students."],
                )
            ],
            languages=[Language(language="English", proficiency="Native")],
        ),
        cover_letter=(
            "Dear Hiring Manager,\n\nI am excited to apply for the Software"
            " Engineer position. My experience with Python and FastAPI aligns"
            " perfectly..."
        ),
        analytics=ResumeAnalytics(
            ats_score=85,
            resume_parse_rate=90,
            keyword_match=78,
            experience_relevance=80,
            overall_job_match=82,
        ),
    )
