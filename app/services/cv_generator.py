import os
from fastapi import HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.schemas.tailored_cv import FinalTailoredOutput

def generate_tailored_assets(extracted_cv_text: str, job_description: str) -> FinalTailoredOutput:
    # Initialize Gemini Model - 3.5-flash is extremely fast, free-tier friendly, and accurate
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash",
        temperature=0.3, # Low temperature for factual, grounded alignments
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    # Enforce Pydantic Structured Output
    structured_llm = llm.with_structured_output(FinalTailoredOutput)
    
    # Write an explicit, bulletproof prompt engineering template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", (
            "You are an elite, ATS-optimized Executive Resume Writer and Career Coach.\n"
            "Your objective is to review the candidate's Raw CV and re-write/re-structure it alongside a premium Cover Letter to perfectly align with the provided Target Job Description.\n\n"
            "CRITICAL RULES:\n"
            "1. Maintain strict factual honesty. Never fabricate completely false experiences, titles, or graduation certificates. Focus instead on framing existing experiences, technologies, and achievements to perfectly spotlight what the Target Job seeks.\n"
            "2. Optimize bullet points using the X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z]) containing explicit keywords from the job description.\n"
            "3. Ensure the cover letter is professional, structurally sound, and tailored specifically to the requirements listed."
        )),
        ("human", (
            "--- CANDIDATE RAW CV TEXT ---\n"
            "{cv_text}\n\n"
            "--- TARGET JOB DESCRIPTION ---\n"
            "{job_desc}\n\n"
            "Please generate the optimized structured CV and custom cover letter based on the rules specified above."
        ))
    ])
    
    # Build LangChain Expression Language (LCEL) chain
    chain = prompt_template | structured_llm
    
    try:
        result = chain.invoke({
            "cv_text": extracted_cv_text,
            "job_desc": job_description
        })
        return result
    except Exception as e:
        error_msg = str(e)
        # Catch rate limits cleanly
        if "429" in error_msg or "ResourceExhausted" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="Gemini API Free Tier limit reached. Please wait 60 seconds before trying again."
            )
        raise HTTPException(status_code=500, detail=f"AI processing engine error: {error_msg}")
    
    return result