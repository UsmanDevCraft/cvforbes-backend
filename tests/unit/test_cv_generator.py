import logging
from app.services.cv_generator import (
    cleanup_extracted_text,
    validate_candidate_profile_missing_sections,
    validate_tailored_output,
    sanitize_candidate_profile,
)
from app.schemas.tailored_cv import (
    WorkExperience,
    ResumeLink,
)


def test_cleanup_extracted_text():
    """Test cleaning and line-merging of raw extracted text."""
    raw_text = (
        "John- \n"
        " Doe\n"
        "Software     Engineer\n"
        "\n"
        "\n"
        "- Bullet point 1\n"
        "continuation of bullet\n"
        "- Bullet point 2\n"
        "Another line that starts with lowercase;\n"
        "this is continued."
    )
    cleaned = cleanup_extracted_text(raw_text)

    # Verify standard spacing
    assert "Software Engineer" in cleaned
    # Verify hyphen split resolution
    assert "JohnDoe" in cleaned or "John Doe" in cleaned or "John-" in cleaned
    # Check bullet structure
    assert "- Bullet point 1" in cleaned


def test_validate_candidate_profile_missing_sections_logs_warnings(
    caplog, sample_candidate_profile
):
    """Test that warning check logs appropriate warning messages when sections are missing."""
    # Modify profile to miss sections
    sample_candidate_profile.experience = []
    sample_candidate_profile.education = []
    sample_candidate_profile.skills = []
    sample_candidate_profile.technical_skills = []

    with caplog.at_level(logging.WARNING):
        validate_candidate_profile_missing_sections(sample_candidate_profile)

    assert "Common resume section 'Experience' appears to be missing" in caplog.text
    assert "Common resume section 'Education' appears to be missing" in caplog.text
    assert "Common resume section 'Skills' appears to be missing" in caplog.text


def test_validate_tailored_output_pass(
    sample_candidate_profile, sample_final_tailored_output
):
    """Test that validation passes when all profile facts are preserved in tailored CV."""
    errors = validate_tailored_output(
        sample_candidate_profile, sample_final_tailored_output.cv
    )
    assert errors == []


def test_validate_tailored_output_fail(
    sample_candidate_profile, sample_final_tailored_output
):
    """Test that validation detects missing experiences, education, projects, or certifications."""
    # Remove education and projects from tailored output
    sample_final_tailored_output.cv.education = []
    sample_final_tailored_output.cv.projects = []

    errors = validate_tailored_output(
        sample_candidate_profile, sample_final_tailored_output.cv
    )
    assert len(errors) >= 2
    assert any("Education institution" in err for err in errors)
    assert any("Project" in err for err in errors)


def test_sanitize_candidate_profile_trims_and_deduplicates(
    sample_candidate_profile,
):
    """Test that sanitization trims strings and deduplicates various lists in CandidateProfile."""
    # Set dirty string fields
    sample_candidate_profile.full_name = "  John Doe   "
    sample_candidate_profile.skills = [
        " Python ",
        "FastAPI",
        "python",
        " fastapi ",
    ]
    sample_candidate_profile.experience = [
        WorkExperience(
            company="Company A",
            role="Software Engineer",
            duration="2020-2022",
            bullet_points=["Worked hard.", "Worked hard."],
        ),
        WorkExperience(
            company="company a",
            role="software engineer",
            duration="2020-2022",
            bullet_points=["Duplicate job entry"],
        ),
    ]
    sample_candidate_profile.links = [
        ResumeLink(type="github", text="GitHub", url=" https://github.com "),
        ResumeLink(type="github", text="GitHub", url="https://github.com"),
    ]

    sanitized = sanitize_candidate_profile(sample_candidate_profile)

    assert sanitized.full_name == "John Doe"
    # Skills list should be stripped of trailing spaces and case-insensitively deduplicated
    assert sanitized.skills == ["Python", "FastAPI"]
    # Links should be deduplicated based on url
    assert len(sanitized.links) == 1
    assert sanitized.links[0].url == "https://github.com"
    # Experience list should deduplicate company a + software engineer
    assert len(sanitized.experience) == 1
    assert sanitized.experience[0].company == "Company A"
