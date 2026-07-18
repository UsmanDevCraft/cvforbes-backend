import re
from typing import List
from fastapi import HTTPException
from app.schemas.tailored_cv import CandidateProfile, FinalTailoredOutput, TailoredCV
from app.utils.logger import logger
from app.core.dependencies import llm_router
from app.services.prompts.ats_tailoring import TAILORING_PROMPT
from app.services.prompts.resume_parsing import PARSING_PROMPT


# 1. Cleanup Extracted Text
def cleanup_extracted_text(text: str) -> str:
    # First, handle hyphenated splits
    text = re.sub(r"(\w+)-\s*\n\s*([a-z]\w*)", r"\1\2", text)

    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        # Standardize multiple spaces into a single space
        cleaned_line = re.sub(r"[ \t]+", " ", line).strip()
        cleaned_lines.append(cleaned_line)

    merged_lines = []
    for line in cleaned_lines:
        if not line:
            if merged_lines and merged_lines[-1] != "":
                merged_lines.append("")
            continue

        if not merged_lines:
            merged_lines.append(line)
            continue

        prev = merged_lines[-1]
        if not prev:
            merged_lines.append(line)
            continue

        # Merge criteria:
        # - Previous line doesn't end with a sentence-ending punctuation (., !, ?, :, ;)
        # - Current line doesn't start with a bullet character (-, *, •, o, ▪, •)
        # - Current line starts with lowercase
        is_bullet = line.startswith(("-", "*", "•", "o", "▪", "•")) or bool(
            re.match(r"^\d+\.", line)
        )
        prev_ends_with_connective = prev[-1] in (",", ";") or prev[-1].isalnum()
        curr_starts_lowercase = line[0].islower()

        if prev_ends_with_connective and curr_starts_lowercase and not is_bullet:
            merged_lines[-1] = prev + " " + line
        else:
            merged_lines.append(line)

    final_lines = []
    for line in merged_lines:
        if line == "":
            if final_lines and final_lines[-1] != "":
                final_lines.append("")
        else:
            final_lines.append(line)

    return "\n".join(final_lines).strip()


# 2. Warning check for missing common sections
def validate_candidate_profile_missing_sections(profile: CandidateProfile) -> None:
    """
    Log warnings if common resume sections appear missing in the parsed profile.
    """
    if not profile.experience:
        logger.warning(
            "Common resume section 'Experience' appears to be missing in the extracted text."
        )
    if not profile.education:
        logger.warning(
            "Common resume section 'Education' appears to be missing in the extracted text."
        )
    if not profile.skills and not profile.technical_skills:
        logger.warning(
            "Common resume section 'Skills' appears to be missing in the extracted text."
        )
    if not profile.projects:
        logger.warning(
            "Common resume section 'Projects' appears to be missing in the extracted text."
        )
    if not profile.certifications:
        logger.warning(
            "Common resume section 'Certifications' appears to be missing in the extracted text."
        )
    if not profile.languages:
        logger.warning(
            "Common resume section 'Languages' appears to be missing in the extracted text."
        )


# 2.5 Sanitize Candidate Profile
def sanitize_candidate_profile(profile: CandidateProfile) -> CandidateProfile:
    """
    Sanitize the parsed CandidateProfile by stripping whitespace from strings
    and deduplicating elements in skill/link/experience lists.
    """
    # 1. Clean string fields
    profile.full_name = profile.full_name.strip()
    profile.email = profile.email.strip()
    profile.phone = profile.phone.strip()
    profile.professional_summary = profile.professional_summary.strip()

    # Helper function to deduplicate a list of strings case-insensitively while preserving order
    def clean_str_list(lst: List[str]) -> List[str]:
        seen = set()
        res = []
        for s in lst:
            s_clean = s.strip()
            if not s_clean:
                continue
            s_lower = s_clean.lower()
            if s_lower not in seen:
                seen.add(s_lower)
                res.append(s_clean)
        return res

    profile.skills = clean_str_list(profile.skills)
    profile.technical_skills = clean_str_list(profile.technical_skills)
    profile.soft_skills = clean_str_list(profile.soft_skills)
    profile.tools_and_technologies = clean_str_list(profile.tools_and_technologies)

    # Guard: If technical_skills is identical to skills, clear it to prevent duplication
    if set(s.lower() for s in profile.technical_skills) == set(
        s.lower() for s in profile.skills
    ):
        logger.info(
            "Detected technical_skills is a duplicate of skills — clearing technical_skills to prevent duplication."
        )
        profile.technical_skills = []

    # Guard: Remove any publication titles that were misclassified as projects
    if profile.publications:
        pub_titles = {pub.title.lower().strip() for pub in profile.publications}
        original_count = len(profile.projects)
        profile.projects = [
            proj
            for proj in profile.projects
            if proj.name.lower().strip() not in pub_titles
        ]
        removed = original_count - len(profile.projects)
        if removed:
            logger.info(
                f"Removed {removed} project(s) that were duplicates of publication entries."
            )

    # 2. Clean links
    unique_links = []
    seen_links = set()
    for link in profile.links:
        if link.url:
            url_clean = link.url.strip()
            if url_clean.lower() not in seen_links:
                seen_links.add(url_clean.lower())
                link.url = url_clean
                if link.type:
                    link.type = link.type.strip()
                if link.text:
                    link.text = link.text.strip()
                unique_links.append(link)
        elif link.text:
            text_clean = link.text.strip()
            if text_clean.lower() not in seen_links:
                seen_links.add(text_clean.lower())
                link.text = text_clean
                if link.type:
                    link.type = link.type.strip()
                unique_links.append(link)
    profile.links = unique_links

    # Deduplicate experience
    seen_exp = set()
    unique_exp = []
    for exp in profile.experience:
        exp.company = exp.company.strip()
        exp.role = exp.role.strip()
        if exp.duration:
            exp.duration = exp.duration.strip()
        exp.bullet_points = [bp.strip() for bp in exp.bullet_points if bp.strip()]

        key = (exp.company.lower(), exp.role.lower())
        if key not in seen_exp:
            seen_exp.add(key)
            unique_exp.append(exp)
    profile.experience = unique_exp

    # Deduplicate projects
    seen_proj = set()
    unique_proj = []
    for proj in profile.projects:
        proj.name = proj.name.strip()
        if proj.description:
            proj.description = proj.description.strip()
        if proj.technologies:
            proj.technologies = clean_str_list(proj.technologies)
        if proj.duration:
            proj.duration = proj.duration.strip()
        if proj.link:
            proj.link = proj.link.strip()

        key = proj.name.lower()
        if key not in seen_proj:
            seen_proj.add(key)
            unique_proj.append(proj)
    profile.projects = unique_proj

    # Deduplicate education
    seen_edu = set()
    unique_edu = []
    for edu in profile.education:
        edu.institution = edu.institution.strip()
        edu.degree = edu.degree.strip()
        if edu.duration:
            edu.duration = edu.duration.strip()

        key = (edu.institution.lower(), edu.degree.lower())
        if key not in seen_edu:
            seen_edu.add(key)
            unique_edu.append(edu)
    profile.education = unique_edu

    # Deduplicate certifications
    seen_cert = set()
    unique_cert = []
    for cert in profile.certifications:
        cert.name = cert.name.strip()
        if cert.issuer:
            cert.issuer = cert.issuer.strip()
        if cert.year:
            cert.year = cert.year.strip()

        key = cert.name.lower()
        if key not in seen_cert:
            seen_cert.add(key)
            unique_cert.append(cert)
    profile.certifications = unique_cert

    # Deduplicate awards
    seen_award = set()
    unique_award = []
    for award in profile.awards:
        award.title = award.title.strip()
        if award.issuer:
            award.issuer = award.issuer.strip()
        if award.year:
            award.year = award.year.strip()

        key = award.title.lower()
        if key not in seen_award:
            seen_award.add(key)
            unique_award.append(award)
    profile.awards = unique_award

    # Deduplicate publications
    seen_pub = set()
    unique_pub = []
    for pub in profile.publications:
        pub.title = pub.title.strip()
        if pub.publisher:
            pub.publisher = pub.publisher.strip()
        if pub.year:
            pub.year = pub.year.strip()
        if pub.link:
            pub.link = pub.link.strip()

        key = pub.title.lower()
        if key not in seen_pub:
            seen_pub.add(key)
            unique_pub.append(pub)
    profile.publications = unique_pub

    # Deduplicate volunteer experience
    seen_vol = set()
    unique_vol = []
    for vol in profile.volunteer_experience:
        if vol.organization:
            vol.organization = vol.organization.strip()
        if vol.role:
            vol.role = vol.role.strip()
        if vol.duration:
            vol.duration = vol.duration.strip()
        vol.bullet_points = [bp.strip() for bp in vol.bullet_points if bp.strip()]

        key = ((vol.organization or "").lower(), (vol.role or "").lower())
        if key not in seen_vol:
            seen_vol.add(key)
            unique_vol.append(vol)
    profile.volunteer_experience = unique_vol

    # Deduplicate languages
    seen_lang = set()
    unique_lang = []
    for lang in profile.languages:
        lang.language = lang.language.strip()
        if lang.proficiency:
            lang.proficiency = lang.proficiency.strip()

        key = lang.language.lower()
        if key not in seen_lang:
            seen_lang.add(key)
            unique_lang.append(lang)
    profile.languages = unique_lang

    return profile


def parse_candidate_profile(cleaned_text: str) -> CandidateProfile:
    """
    Invoke the LLM router to parse cleaned raw resume text into a structured CandidateProfile.
    """
    messages = PARSING_PROMPT.format_messages(cv_text=cleaned_text)
    result = llm_router.invoke_structured(prompt=messages, schema=CandidateProfile)
    return result


def tailor_profile_to_job(
    profile: CandidateProfile, job_desc: str
) -> FinalTailoredOutput:
    """
    Invoke the LLM router to tailor the candidate profile to the job description.
    """
    profile_json = profile.model_dump_json()
    messages = TAILORING_PROMPT.format_messages(
        profile_json=profile_json, job_desc=job_desc
    )
    result = llm_router.invoke_structured(prompt=messages, schema=FinalTailoredOutput)
    return result


# 5. Output Validation Layer
def validate_tailored_output(
    profile: CandidateProfile, tailored: TailoredCV
) -> List[str]:
    """
    Perform a bidirectional fact/existence verification check.
    Returns a list of error strings if any required original info was lost or omitted.
    """
    errors = []

    def is_present(target_name: str, tailored_list: List[str]) -> bool:
        target_lower = target_name.lower().strip()
        if not target_lower:
            return True
        for item in tailored_list:
            if target_lower in item.lower() or item.lower() in target_lower:
                return True
        return False

    # Check experiences (employers and job titles)
    tailored_employers = [exp.company for exp in tailored.experience]
    tailored_roles = [exp.role for exp in tailored.experience]

    for exp in profile.experience:
        if not is_present(exp.company, tailored_employers):
            errors.append(
                f"Employer '{exp.company}' was not preserved in the tailored CV."
            )
        if not is_present(exp.role, tailored_roles):
            errors.append(
                f"Job title '{exp.role}' was not preserved in the tailored CV."
            )

    # Check education
    tailored_institutions = [edu.institution for edu in tailored.education]
    for edu in profile.education:
        if not is_present(edu.institution, tailored_institutions):
            errors.append(
                f"Education institution '{edu.institution}' was not preserved in the tailored CV."
            )

    # Check projects
    tailored_projects = [proj.name for proj in tailored.projects]
    for proj in profile.projects:
        if not is_present(proj.name, tailored_projects):
            errors.append(
                f"Project '{proj.name}' was not preserved in the tailored CV."
            )

    # Check certifications
    tailored_certs = [cert.name for cert in tailored.certifications]
    for cert in profile.certifications:
        if not is_present(cert.name, tailored_certs):
            errors.append(
                f"Certification '{cert.name}' was not preserved in the tailored CV."
            )

    return errors


# 6. Main Orchestrator Pipeline
def generate_tailored_assets(
    extracted_cv_text: str, job_description: str
) -> FinalTailoredOutput:
    try:
        # Step A: Clean raw text
        cleaned_text = cleanup_extracted_text(extracted_cv_text)

        # Step B: Parse raw text into Structured Candidate Profile
        logger.info("Step 1: Parsing raw resume into structured candidate profile.")
        parsed_profile = parse_candidate_profile(cleaned_text)

        # Sanitize Candidate Profile
        parsed_profile = sanitize_candidate_profile(parsed_profile)

        # Step C: Log warnings for missing sections
        validate_candidate_profile_missing_sections(parsed_profile)

        # Step D: Tailor and Validate with Retry Logic
        max_retries = 3
        last_errors = []

        for attempt in range(max_retries):
            logger.info(
                f"Step 2: Tailoring candidate profile. Attempt {attempt + 1} of {max_retries}."
            )
            try:
                tailored_output = tailor_profile_to_job(parsed_profile, job_description)

                # Perform output validation check
                validation_errors = validate_tailored_output(
                    parsed_profile, tailored_output.cv
                )
                if not validation_errors:
                    logger.info("Validation passed successfully.")
                    return tailored_output

                last_errors = validation_errors
                logger.warning(
                    f"Validation failed on attempt {attempt + 1}. Errors: {validation_errors}. Retrying..."
                )
            except Exception as e:
                logger.exception(f"Error during tailoring attempt {attempt + 1}")
                last_errors = [str(e)]

        # If all retries fail
        error_details = "; ".join(last_errors)
        logger.error(
            f"All tailoring attempts failed validation. Last errors: {error_details}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate tailored CV while preserving all facts. Errors: {error_details}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in tailoring pipeline.")
        raise HTTPException(status_code=500, detail="Unexpected AI processing error.")
