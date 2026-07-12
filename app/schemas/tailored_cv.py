from pydantic import BaseModel, Field, EmailStr
from typing import List


class WorkExperience(BaseModel):
    company: str = Field(min_length=2, max_length=100)
    role: str = Field(min_length=2, max_length=100)
    duration: str = Field(min_length=2, max_length=50)

    bullet_points: List[str] = Field(
        min_length=2, max_length=6, description="2-6 tailored bullet points."
    )


class Education(BaseModel):
    institution: str = Field(min_length=2, max_length=150)
    degree: str = Field(min_length=2, max_length=150)
    duration: str = Field(min_length=2, max_length=50)


class TailoredCV(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    phone: str = Field(
        min_length=7,
        max_length=20,
    )

    links: List[str] = Field(
        min_length=0, max_length=10, description="GitHub, LinkedIn, Portfolio, etc."
    )

    professional_summary: str = Field(
        min_length=100,
        max_length=800,
        description="ATS optimized professional summary.",
    )

    skills: List[str] = Field(
        min_length=1,
        max_length=50,
        description="Relevant technical and professional skills.",
    )

    experience: List[WorkExperience] = Field(
        min_length=1,
        max_length=20,
    )

    education: List[Education] = Field(
        min_length=1,
        max_length=10,
    )


class FinalTailoredOutput(BaseModel):
    cv: TailoredCV
    cover_letter: str = Field(
        min_length=300,
        max_length=5000,
        description="Professional ATS-optimized cover letter.",
    )
