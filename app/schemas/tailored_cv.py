from pydantic import BaseModel, EmailStr, Field


class WorkExperience(BaseModel):
    company: str = Field(
        ...,
        max_length=100,
        description="The name of the company or organization where the candidate worked.",
    )
    role: str = Field(
        ...,
        max_length=100,
        description="The official job title or role held by the candidate.",
    )
    duration: str | None = Field(
        None,
        max_length=50,
        description=(
            "The duration of employment (e.g., 'June 2021 - Present', '2018 - 2020'). If unknown, use 'Unknown'."
            "Return null if not explicitly present in the resume."
        ),
    )
    bullet_points: list[str] = Field(
        default_factory=list,
        description=(
            "Action-oriented, ATS-optimized bullet points describing accomplishments and duties. "
            "Incorporate strong verbs and metrics if present."
        ),
    )


class ResumeLink(BaseModel):
    type: str | None = Field(
        None,
        description=(
            "Type of link such as GitHub, LinkedIn, Portfolio, Dev Community, Personal Website. "
            "Return null if it cannot be determined."
        ),
    )

    text: str | None = Field(
        None,
        description=(
            "Visible label exactly as written in the resume. "
            "Return null if unavailable."
        ),
    )

    url: str | None = Field(
        None,
        description=(
            "Complete URL exactly as written in the resume. "
            "Return null if the resume only contains a label."
        ),
    )


class Project(BaseModel):
    name: str = Field(
        ...,
        max_length=100,
        description="The name of the project.",
    )
    description: str | None = Field(
        None,
        max_length=1000,
        description=(
            "A concise description of the project's purpose, details, and impact."
            "Return null if not explicitly present in the resume."
        ),
    )
    technologies: list[str] | None = Field(
        default=None,
        description="List of tools, languages, frameworks, or libraries used in the project. Return an empty array [] if none are known. Do NOT return null.",
    )
    duration: str | None = Field(
        None,
        description=(
            "The timeframe when the project was completed (e.g., 'Jan 2023 - Mar 2023')."
            "Return null if not explicitly present in the resume."
        ),
    )
    link: str | None = Field(
        None,
        description=(
            "URL to the project repository or live site, if present in the resume."
            "Return null if not explicitly present in the resume."
        ),
    )


class Education(BaseModel):
    institution: str = Field(
        ...,
        max_length=150,
        description="The name of the educational institution (school, college, university).",
    )
    degree: str = Field(
        ...,
        max_length=150,
        description="The degree or credential obtained, including major/field of study (e.g., 'Bachelor of Science in Computer Science').",
    )
    duration: str | None = Field(
        None,
        max_length=50,
        description=(
            "The years of attendance or graduation date (e.g., '2016 - 2020', 'Graduated May 2022')."
            "Return null if not explicitly present in the resume."
        ),
    )


class Certification(BaseModel):
    name: str = Field(
        ...,
        description="The official name of the certification (e.g., 'AWS Certified Solutions Architect').",
    )
    issuer: str | None = Field(
        None,
        description=(
            "Organization that issued the certification."
            "Return null if not explicitly present in the resume."
        ),
    )
    year: str | None = Field(
        None,
        description=(
            "The year the certification was earned or its validity period."
            "Return null if not explicitly present in the resume."
        ),
    )


class Award(BaseModel):
    title: str = Field(
        ...,
        description="The title of the award or honor.",
    )
    issuer: str | None = Field(
        None,
        description=(
            "The organization that bestowed the award."
            "Return null if not explicitly present in the resume."
        ),
    )
    year: str | None = Field(
        None,
        description=(
            "The year the award was received."
            "Return null if not explicitly present in the resume."
        ),
    )


class Publication(BaseModel):
    title: str = Field(
        ...,
        description="The title of the published paper, article, or book.",
    )
    publisher: str | None = Field(
        None,
        description=(
            "The journal, conference, publisher, or platform where it was published."
            "Return null if not explicitly present in the resume."
        ),
    )
    year: str | None = Field(
        None,
        description=(
            "The year of publication."
            "Return null if not explicitly present in the resume."
        ),
    )
    link: str | None = Field(
        None,
        description=(
            "URL to the online publication, if available."
            "Return null if not explicitly present in the resume."
        ),
    )


class VolunteerExperience(BaseModel):
    organization: str | None = Field(
        None,
        description="The name of the volunteer organization.",
    )
    role: str | None = Field(
        None,
        description="The role or title held during volunteering.",
    )
    duration: str | None = Field(
        None,
        description=(
            "The timeframe of the volunteering."
            "Return null if not explicitly present in the resume."
        ),
    )
    bullet_points: list[str] = Field(
        default_factory=list,
        description="Bullet points highlighting contributions and impact during volunteer service.",
    )


class Language(BaseModel):
    language: str = Field(
        ...,
        description="Name of the language (e.g., 'Spanish', 'Mandarin').",
    )
    proficiency: str | None = Field(
        None,
        description=(
            "The proficiency level (e.g., 'Native', 'Fluent', 'Professional Working', 'Conversational')."
            "Return null if not explicitly present in the resume."
        ),
    )


class CandidateProfile(BaseModel):
    full_name: str = Field(
        ...,
        max_length=100,
        description="Candidate's full name.",
    )
    email: EmailStr = Field(
        ...,
        description="Candidate's contact email address.",
    )
    phone: str = Field(
        ...,
        max_length=25,
        description="Candidate's phone number.",
    )
    links: list[ResumeLink] = Field(
        default_factory=list,
        description=(
            "All web links (GitHub, LinkedIn, portfolios, personal sites) present in the resume."
            "Return an empty list [] if no links are present."
        ),
    )
    professional_summary: str = Field(
        ...,
        description="Original professional summary or intro.",
    )
    skills: list[str] = Field(
        default_factory=list,
        description=(
            "The MASTER flat list of ALL skills from the resume — technical, soft, tools, everything combined. "
            "This is the single comprehensive skills list. Every skill mentioned anywhere in the resume belongs here."
        ),
    )
    technical_skills: list[str] = Field(
        default_factory=list,
        description=(
            "A SUBSET of 'skills' containing ONLY programming languages, frameworks, libraries, and databases "
            "(e.g., Python, React, MongoDB). Do NOT duplicate the entire 'skills' list here. "
            "If the resume does not clearly separate technical skills from other skills, leave this as an EMPTY list []. "
            "This must NEVER be a copy of the 'skills' field."
        ),
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="A SUBSET of 'skills' containing ONLY interpersonal/soft skills (e.g., Leadership, Communication). Leave empty [] if none are explicitly listed.",
    )
    tools_and_technologies: list[str] = Field(
        default_factory=list,
        description="A SUBSET of 'skills' containing ONLY standalone tools and platforms (e.g., Jira, Git, Docker, Figma, Postman). Leave empty [] if none are explicitly listed.",
    )
    experience: list[WorkExperience] = Field(
        default_factory=list,
        description="All work experience entries.",
    )
    projects: list[Project] = Field(
        default_factory=list,
        description=(
            "All PROJECT entries — software applications, tools, websites, or codebases the candidate BUILT. "
            "A project is something the candidate coded/developed/created. "
            "Do NOT put blog posts, articles, tutorials, or written publications here."
        ),
    )
    education: list[Education] = Field(
        default_factory=list,
        description="All education entries.",
    )
    certifications: list[Certification] = Field(
        default_factory=list,
        description="All certifications.",
    )
    awards: list[Award] = Field(
        default_factory=list,
        description="All awards.",
    )
    publications: list[Publication] = Field(
        default_factory=list,
        description=(
            "All PUBLICATION entries — blog posts, articles, tutorials, research papers, or written content the candidate AUTHORED. "
            "Items listed under a 'Publications' heading in the resume belong here, NOT in projects. "
            "Do NOT put software applications, tools, or codebases here."
        ),
    )
    volunteer_experience: list[VolunteerExperience] = Field(
        default_factory=list,
        description="All volunteer work.",
    )
    languages: list[Language] = Field(
        default_factory=list,
        description="All languages.",
    )


class TailoredCV(BaseModel):
    full_name: str = Field(
        ...,
        max_length=100,
        description="Candidate's full legal name.",
    )
    email: EmailStr = Field(
        ...,
        description="Candidate's contact email address.",
    )
    phone: str = Field(
        ...,
        max_length=25,
        description="Candidate's phone number.",
    )
    links: list[ResumeLink] = Field(
        default_factory=list,
        description=(
            "Professional links present in the resume such as GitHub, LinkedIn, portfolios, or personal website."
            "Return an empty list [] if no links are present."
        ),
    )
    professional_summary: str = Field(
        ...,
        max_length=800,
        description=(
            "ATS-optimized professional summary of 3-5 sentences. "
            "Tailored specifically for the target job description by naturally integrating "
            "critical keywords and qualifications. Maintain readability and flow."
        ),
    )
    skills: list[str] = Field(
        default_factory=list,
        description=(
            "The MASTER flat list of ALL skills relevant to the target role — technical, soft, tools, everything combined. "
            "This is the single comprehensive skills list."
        ),
    )
    technical_skills: list[str] = Field(
        default_factory=list,
        description=(
            "A SUBSET of 'skills' containing ONLY programming languages, frameworks, libraries, and databases "
            "(e.g., Python, React, MongoDB). Do NOT duplicate the entire 'skills' list here. "
            "If the original profile had an empty technical_skills list, keep this EMPTY []. "
            "This must NEVER be a copy of the 'skills' field."
        ),
    )
    soft_skills: list[str] = Field(
        default_factory=list,
        description="A SUBSET of 'skills' containing ONLY interpersonal/soft skills. Keep empty [] if the original profile had none.",
    )
    tools_and_technologies: list[str] = Field(
        default_factory=list,
        description="A SUBSET of 'skills' containing ONLY standalone tools and platforms (e.g., Jira, Git, Docker). Keep empty [] if the original profile had none.",
    )
    experience: list[WorkExperience] = Field(
        default_factory=list,
        description="List of candidate's professional work experience, starting with the most recent.",
    )
    projects: list[Project] = Field(
        default_factory=list,
        description=(
            "Software applications, tools, websites, or codebases the candidate BUILT. "
            "Do NOT put blog posts, articles, tutorials, or written publications here."
        ),
    )
    education: list[Education] = Field(
        default_factory=list,
        description="List of formal educational credentials, institutions, and degrees.",
    )
    certifications: list[Certification] = Field(
        default_factory=list,
        description="Professional certifications, licenses, or credentials obtained by the candidate.",
    )
    awards: list[Award] = Field(
        default_factory=list,
        description="Awards, achievements, honors, or scholarships received by the candidate.",
    )
    publications: list[Publication] = Field(
        default_factory=list,
        description=(
            "Blog posts, articles, tutorials, research papers, or written content the candidate AUTHORED. "
            "Items from the original profile's publications list belong here, NOT in projects."
        ),
    )
    volunteer_experience: list[VolunteerExperience] = Field(
        default_factory=list,
        description="Volunteer work, community service, or non-profit engagement.",
    )
    languages: list[Language] = Field(
        default_factory=list,
        description="Languages spoken by the candidate and their respective proficiency levels.",
    )


class ResumeAnalytics(BaseModel):
    ats_score: int = Field(ge=0, le=100)
    resume_parse_rate: int = Field(ge=0, le=100)
    keyword_match: int = Field(ge=0, le=100)
    experience_relevance: int = Field(ge=0, le=100)
    overall_job_match: int = Field(ge=0, le=100)


class FinalTailoredOutput(BaseModel):
    cv: TailoredCV
    cover_letter: str = Field(
        ...,
        max_length=5000,
        description="Professional ATS-optimized cover letter.",
    )
    analytics: ResumeAnalytics
