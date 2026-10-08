from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List
import io
import os
import uuid
import traceback
from PyPDF2 import PdfReader
import docx

from backend.app.services.analysis import analyze_resume_from_text

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Store results temporarily
analysis_results = {}
candidate_data = {}

def extract(file_bytes, ext):
    if ext == "pdf":
        reader = PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in reader.pages)
    if ext == "docx":
        d = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in d.paragraphs)
    return file_bytes.decode("utf-8")

@app.get("/")
async def root():
    return {"message": "Resume Analyzer API is running"}

@app.post("/analyze/")
async def analyze(files: List[UploadFile] = File(...), jd: str = "python aws django sql"):
    results = []
    for file in files:
        content = await file.read()
        ext = file.filename.split(".")[-1].lower()

        text = extract(content, ext)
        analysis = analyze_resume_from_text(text, jd)
        results.append({"filename": file.filename, **analysis})

    sorted_results = sorted(results, key=lambda x: x["ats_score"], reverse=True)
    return {"ranked_results": sorted_results}

@app.post("/analyze-all-resumes/")
async def analyze_all_resumes(files: List[UploadFile] = File(...)):
    """Analyze multiple resumes and return anonymized ranked results"""
    
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    results = []
    errors = []
    job_description = "python aws django sql machine learning data science software engineer"
    
    for i, file in enumerate(files):
        try:
            content = await file.read()
            ext = file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
            
            if ext not in ["pdf", "docx", "txt"]:
                errors.append(f"Skipped {file.filename}: Unsupported file type")
                continue
                
            text = extract(content, ext)
            if not text.strip():
                errors.append(f"Skipped {file.filename}: Empty content")
                continue
                
            analysis = analyze_resume_from_text(text, job_description)
            
            # Generate candidate ID
            candidate_id = f"candidate_{uuid.uuid4().hex[:8]}"
            
            # Ensure genai_suggestions is a string
            genai_sugg = analysis.get("genai_suggestions", "")
            if isinstance(genai_sugg, list):
                genai_sugg = "\n".join(genai_sugg)
            
            # Store detailed data
            candidate_data[candidate_id] = {
                **analysis,
                "genai_suggestions": genai_sugg,
                "original_filename": file.filename,
                "raw_text": text
            }
            
            # Create result for table
            result = {
                "candidate_id": candidate_id,
                "score": analysis["ats_score"],
                "rank": 0,  # Will be set after sorting
                "pass": analysis["ats_score"] >= 60  # Pass threshold
            }
            
            results.append(result)
            
        except Exception as e:
            error_msg = f"Error processing {file.filename}: {str(e)}"
            print(error_msg)
            print(traceback.format_exc())
            errors.append(f"Failed {file.filename}: {str(e)}")
            continue
    
    # Sort by score and assign ranks
    results.sort(key=lambda x: x["score"], reverse=True)
    for i, result in enumerate(results):
        result["rank"] = i + 1
    
    response_data = {
        "results": results,
        "count": len(results)
    }
    
    if errors:
        response_data["errors"] = errors
    
    # Return with explicit CORS headers
    return JSONResponse(
        content=response_data,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/get-candidate-details/{candidate_id}")
async def get_candidate_details(candidate_id: str):
    """Get detailed analysis for a specific candidate"""
    if candidate_id not in candidate_data:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    data = candidate_data[candidate_id]
    return {
        "summary": data["summary"],
        "skills_detected": data["skills_detected"],
        "experience_years": data["experience_years"],
        "ats_score": data["ats_score"],
        "semantic_score": data["semantic_score"],
        "keyword_score": data["keyword_score"],
        "genai_suggestions": data["genai_suggestions"]
    }

@app.get("/download/{candidate_id}/pdf")
async def download_candidate_pdf(candidate_id: str):
    """Download anonymized resume as text file (PDF generation would need additional libraries)"""
    if candidate_id not in candidate_data:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    data = candidate_data[candidate_id]
    
    # Create a temporary text file with anonymized content
    temp_filename = f"{candidate_id}_resume.txt"
    temp_path = os.path.join(os.getcwd(), temp_filename)
    
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(f"Candidate ID: {candidate_id}\n")
            f.write(f"ATS Score: {data['ats_score']}\n\n")
            f.write("ANONYMIZED RESUME CONTENT:\n")
            f.write("=" * 50 + "\n")
            f.write(data["anonymized_text"])
        
        return FileResponse(
            temp_path,
            media_type="text/plain",
            filename=temp_filename,
            headers={"Content-Disposition": f"attachment; filename={temp_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating file: {str(e)}")
