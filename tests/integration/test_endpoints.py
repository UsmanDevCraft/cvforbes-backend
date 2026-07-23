def test_tailor_cv_endpoint_invalid_file_extension(client, valid_pdf):
    """Test that uploading a file with a non-PDF extension is rejected with 400."""
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need an experienced developer."},
        files={"cv_file": ("resume.txt", b"Some text", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF files are allowed" in response.json()["detail"]


def test_tailor_cv_endpoint_invalid_mime_type(client, valid_pdf):
    """Test that uploading a PDF file but with an invalid MIME type is rejected with 400."""
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need an experienced developer."},
        files={"cv_file": ("resume.pdf", valid_pdf, "text/plain")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_tailor_cv_endpoint_empty_file(client):
    """Test that uploading an empty file is rejected with 400."""
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need an experienced developer."},
        files={"cv_file": ("resume.pdf", b"", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Uploaded file is empty" in response.json()["detail"]


def test_tailor_cv_endpoint_oversized_file(client):
    """Test that uploading a file exceeding 5 MB is rejected with 413."""
    oversized_data = b"0" * (5 * 1024 * 1024 + 1)
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need an experienced developer."},
        files={"cv_file": ("resume.pdf", oversized_data, "application/pdf")},
    )
    assert response.status_code == 413
    assert "Maximum allowed file size is 5 MB" in response.json()["detail"]


def test_tailor_cv_endpoint_job_desc_too_short(client, valid_pdf):
    """Test that job description less than 10 characters is rejected with 422."""
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "Short"},
        files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 422


def test_tailor_cv_endpoint_job_desc_too_long(client, valid_pdf):
    """Test that job description exceeding 3500 characters is rejected with 422."""
    long_desc = "A" * 3501
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": long_desc},
        files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 422
    assert (
        "Job description must be 3500 characters or fewer" in response.json()["detail"]
    )


def test_rate_limiting_triggers_429(client, valid_pdf, mocker):
    """Test that rate limiting blocks the 4th request from the same IP client."""
    # Mock LLM router calls to make it fast
    mocker.patch(
        "app.core.dependencies.llm_router.invoke_structured",
        side_effect=Exception("LLM mock not needed"),
    )

    # First 3 requests should NOT trigger 429 (they might return 500/errors due to LLM mock, but not 429)
    for _ in range(3):
        response = client.post(
            "/api/v1/tailor-cv",
            data={"job_description": "We need a Software Engineer."},
            files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
        )
        assert response.status_code != 429

    # The 4th request must return 429
    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need a Software Engineer."},
        files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.text


def test_e2e_pipeline_success(
    client,
    valid_pdf,
    sample_candidate_profile,
    sample_final_tailored_output,
    mocker,
):
    """Test the complete successful end-to-end pipeline with mocked LLM responses."""
    mock_invoke = mocker.patch("app.core.dependencies.llm_router.invoke_structured")
    # First call: Parse CandidateProfile
    # Second call: Tailor to FinalTailoredOutput
    mock_invoke.side_effect = [
        sample_candidate_profile,
        sample_final_tailored_output,
    ]

    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need a Software Engineer with Python."},
        files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 200

    data = response.json()
    assert "cv" in data
    assert data["cv"]["full_name"] == "John Doe"
    assert "cover_letter" in data
    assert "Dear Hiring Manager" in data["cover_letter"]

    assert mock_invoke.call_count == 2


def test_e2e_pipeline_retries_on_validation_failure_then_succeeds(
    client,
    valid_pdf,
    sample_candidate_profile,
    sample_final_tailored_output,
    mocker,
):
    """Test that the orchestrator retries tailoring if validation fails, and succeeds when output is valid."""
    mock_invoke = mocker.patch("app.core.dependencies.llm_router.invoke_structured")

    # Create an invalid tailored output by removing required work experience
    invalid_tailored_output = sample_final_tailored_output.model_copy(deep=True)
    invalid_tailored_output.cv.experience = []

    # Side effects:
    # 1. Parse (returns sample_candidate_profile)
    # 2. Tailoring Attempt 1 (returns invalid_tailored_output -> validation fails)
    # 3. Tailoring Attempt 2 (returns sample_final_tailored_output -> validation passes)
    mock_invoke.side_effect = [
        sample_candidate_profile,
        invalid_tailored_output,
        sample_final_tailored_output,
    ]

    response = client.post(
        "/api/v1/tailor-cv",
        data={"job_description": "We need a Software Engineer with Python."},
        files={"cv_file": ("resume.pdf", valid_pdf, "application/pdf")},
    )
    assert response.status_code == 200
    assert mock_invoke.call_count == 3  # 1 parse + 2 tailor attempts
