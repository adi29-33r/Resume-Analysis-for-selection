def keyword_score(job_description, resume_text):
    # temporary working implementation
    return 50

def semantic_score(job_description, resume_text):
    return 30

def final_ats_score(keyword, semantic):
    return 0.6 * keyword + 0.4 * semantic
