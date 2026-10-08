def keyword_score(resume_skills_set, job_skills_set):
    """Calculate keyword match score between resume and job requirements"""
    if not job_skills_set or not resume_skills_set:
        return 0.0
    
    intersection = resume_skills_set.intersection(job_skills_set)
    union = resume_skills_set.union(job_skills_set)
    
    if not union:
        return 0.0
    
    # Jaccard similarity * 100
    return (len(intersection) / len(union)) * 100

def semantic_score(resume_text, job_description):
    """Calculate semantic similarity between resume and job description"""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        docs = [resume_text, job_description]
        tfidf_matrix = vectorizer.fit_transform(docs)
        
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity * 100
    except Exception:
        # Fallback to simple word overlap
        resume_words = set(resume_text.lower().split())
        jd_words = set(job_description.lower().split())
        
        if not jd_words:
            return 0.0
            
        overlap = resume_words.intersection(jd_words)
        return (len(overlap) / len(jd_words)) * 100

def final_ats_score(keyword_score, semantic_score, experience=0):
    """Calculate final ATS score combining keyword, semantic, and experience"""
    return (keyword_score * 0.4) + (semantic_score * 0.4) + (experience * 0.2)
