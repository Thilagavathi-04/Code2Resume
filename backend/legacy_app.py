import os
import httpx
import ollama
import asyncio
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Any, Union, Optional
import json
from urllib.parse import urlparse
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.database import engine, get_db, Base
from backend.models.user import User
from backend.services.rag_service import RAGService
from backend.services.agent_service import AgentService

# Create tables
Base.metadata.create_all(bind=engine)

# Auth Configuration
SECRET_KEY = "your-secret-key-keep-it-secret" # In production, use env var
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # Removed due to passlib incompatibility
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI()

# Job tracking for background tasks
analysis_jobs = {}

# Initialize Services
rag_service = RAGService()
agent_service = AgentService()

# Job tracking for background tasks
analysis_jobs = {}

# Enable CORS - Allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Backend itself
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Models & Helpers ---

class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(BaseModel):
    username: str
    password: str
    github_url: str
    github_token: str
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    gmail: Optional[str] = None
    mobile_number: Optional[str] = None

class UserUpdate(BaseModel):
    github_url: Optional[str] = None
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    gmail: Optional[str] = None
    mobile_number: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    username: str
    github_url: str
    linkedin_id: Optional[str] = None
    leetcode_id: Optional[str] = None
    gmail: Optional[str] = None
    mobile_number: Optional[str] = None

import bcrypt

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# --- Auth Endpoints ---

@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Verify GitHub Token
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"token {user.github_token}"}
        resp = await client.get("https://api.github.com/user", headers=headers)
        if resp.status_code != 200:
             raise HTTPException(status_code=400, detail="Invalid GitHub Token")
        
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        hashed_password=hashed_password,
        github_url=user.github_url,
        github_token=user.github_token,
        linkedin_id=user.linkedin_id,
        leetcode_id=user.leetcode_id,
        gmail=user.gmail,
        mobile_number=user.mobile_number
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        username=current_user.username,
        github_url=current_user.github_url,
        linkedin_id=current_user.linkedin_id,
        leetcode_id=current_user.leetcode_id,
        gmail=current_user.gmail,
        mobile_number=current_user.mobile_number
    )

@app.put("/auth/me", response_model=UserResponse)
async def update_user(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Update user details (except GitHub token which is read-only)"""
    # Update fields if provided
    if user_update.github_url is not None:
        current_user.github_url = user_update.github_url
    if user_update.linkedin_id is not None:
        current_user.linkedin_id = user_update.linkedin_id
    if user_update.leetcode_id is not None:
        current_user.leetcode_id = user_update.leetcode_id
    if user_update.gmail is not None:
        current_user.gmail = user_update.gmail
    if user_update.mobile_number is not None:
        current_user.mobile_number = user_update.mobile_number
    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        username=current_user.username,
        github_url=current_user.github_url,
        linkedin_id=current_user.linkedin_id,
        leetcode_id=current_user.leetcode_id,
        gmail=current_user.gmail,
        mobile_number=current_user.mobile_number
    )

# --- Application Logic ---

class RepoRequest(BaseModel):
    url: Optional[str] = None # Optional now, defaults to user's URL

class AskRequest(BaseModel):
    query: str

class ResumeRequest(BaseModel):
    query: str
    domain: Optional[str] = None

class JobStatus(BaseModel):
    job_id: str
    status: str  # 'processing', 'completed', 'failed'
    progress: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/ask")
async def ask_agent(request: AskRequest, current_user: User = Depends(get_current_user)):
    try:
        response = await asyncio.to_thread(
            agent_service.ask, request.query, username=current_user.username
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/stream")
async def ask_agent_stream(request: AskRequest, current_user: User = Depends(get_current_user)):
    from fastapi.responses import StreamingResponse
    try:
        async def generate():
            # Run the synchronous stream in a thread and yield tokens
            def _stream():
                return list(agent_service.ask_stream(request.query, username=current_user.username))

            tokens = await asyncio.to_thread(_stream)
            for token in tokens:
                yield f"data: {json.dumps({'token': token})}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repos")
async def get_user_repos(current_user: User = Depends(get_current_user)):
    """
    Gets all analyzed repositories for the current user
    """
    try:
        repos = rag_service.get_user_repos(current_user.username)
        return repos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-resume")
async def generate_resume_file(request: ResumeRequest, current_user: User = Depends(get_current_user)):
    """
    Generates a LaTeX resume file and saves it to resumes/ directory
    Returns the filename for download
    """
    try:
        # Generate resume content using agent service
        latex_content = agent_service.generate_resume(
            request.query, 
            username=current_user.username, 
            model="mistral:latest"
        )
        
        if latex_content.startswith("Error"):
            raise HTTPException(status_code=500, detail=latex_content)
        
        # Create resumes directory if it doesn't exist
        resumes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "resumes")
        if not os.path.exists(resumes_dir):
            os.makedirs(resumes_dir)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{current_user.username}_{timestamp}.tex"
        filepath = os.path.join(resumes_dir, filename)
        
        # Save LaTeX content to file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)
        
        print(f"Resume saved: {filepath}")
        
        return {
            "success": True,
            "filename": filename,
            "message": "Resume generated successfully! Click below to download."
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{filename}")
async def download_file(filename: str, current_user: User = Depends(get_current_user)):
    """
    Downloads a generated resume file
    """
    try:
        # Security check: ensure filename doesn't contain path traversal
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp")
        filepath = os.path.join(tmp_dir, filename)
        
        # Check if file exists
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Verify file belongs to this user (filename contains username)
        if current_user.username not in filename:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/x-tex",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/resumes")
async def list_resumes(current_user: User = Depends(get_current_user)):
    """
    List all resumes generated by the current user
    """
    try:
        # Check both tmp and resumes directories
        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes")
        ]
        
        user_files = []
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            # Get all files for this user
            for filename in os.listdir(directory):
                if filename.startswith(f"resume_{current_user.username}_") and filename.endswith(".tex"):
                    filepath = os.path.join(directory, filename)
                    stats = os.stat(filepath)
                    
                    # Try to extract query from filename (after timestamp)
                    # Format: resume_username_timestamp_query.tex
                    parts = filename[:-4].split('_', 3)
                    query = parts[3].replace('_', ' ') if len(parts) > 3 else "Resume"
                    
                    user_files.append({
                        "filename": filename,
                        "query": query,
                        "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        "size": stats.st_size,
                        "directory": directory
                    })
        
        # Sort by creation time (newest first)
        user_files.sort(key=lambda x: x['created_at'], reverse=True)
        
        return user_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download-resume/{filename}")
async def download_resume(filename: str, current_user: User = Depends(get_current_user)):
    """
    Download a specific resume file
    """
    try:
        # Security check
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Verify file belongs to this user
        if not filename.startswith(f"resume_{current_user.username}_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check both tmp and resumes directories
        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes")
        ]
        
        filepath = None
        for directory in directories:
            potential_path = os.path.join(directory, filename)
            if os.path.exists(potential_path):
                filepath = potential_path
                break
        
        if not filepath:
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/x-tex",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-resume/{filename}")
async def delete_resume(filename: str, current_user: User = Depends(get_current_user)):
    """
    Delete a specific resume file
    """
    try:
        # Security check
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Verify file belongs to this user
        if not filename.startswith(f"resume_{current_user.username}_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check both tmp and resumes directories
        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes")
        ]
        
        filepath = None
        for directory in directories:
            potential_path = os.path.join(directory, filename)
            if os.path.exists(potential_path):
                filepath = potential_path
                break
        
        if not filepath:
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(filepath)
        
        return {"success": True, "message": "Resume deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_github_data(owner: str, repo: str, token: str):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    # Set reasonable timeouts: 10s connect, 30s read
    timeout = httpx.Timeout(10.0, read=30.0)
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=timeout) as client:
        # Fetch repo details
        try:
            repo_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            print(f"Timeout fetching {owner}/{repo}: {e}")
            return None, None, None
        
        if repo_resp.status_code == 403:
            print(f"Rate limit exceeded while fetching {owner}/{repo}")
            return None, None, None
            
        if repo_resp.status_code != 200:
            # Don't raise here, just return None so we can skip it in batch processing
            return None, None, None
        repo_data = repo_resp.json()

        # Fetch languages
        lang_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/languages")
        languages = lang_resp.json() if lang_resp.status_code == 200 else {}

        # Fetch README
        readme_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
        readme_content = ""
        if readme_resp.status_code == 200:
            import base64
            try:
                readme_content = base64.b64decode(readme_resp.json()["content"]).decode("utf-8")
            except:
                readme_content = "Could not decode README."
        
        return repo_data, languages, readme_content

async def run_llm(prompt: str, context_name: str):
    # Strategy: Prioritize GPU. If VRAM (4GB) is insufficient, offload to CPU/RAM.
    # Using mistral:latest (fine-tuned) optimized for this app.
    model = "mistral:latest"
    try:
        # Test Ollama connection first
        try:
            await asyncio.to_thread(ollama.list)
        except Exception as conn_error:
            print(f"Ollama connection failed: {conn_error}")
            print("Please start Ollama with: ollama serve")
            return {"raw_response": json.dumps({"error": "Ollama service is not running. Please start it with: ollama serve"}), "repo_name": context_name}

        # Force GPU usage with num_gpu option - run synchronous call in thread
        def _chat():
            return ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt}
            ], options={'num_gpu': 99})

        response = await asyncio.to_thread(_chat)
        content = response['message']['content']
        content = content.replace("```json", "").replace("```", "").strip()
        return {"raw_response": content, "repo_name": context_name}
    except ollama.ResponseError as e:
        if e.status_code == 404:
            print(f"Model {model} not found. Attempting to pull...")
            try:
                print(f"Pulling {model}... This may take a few minutes.")
                await asyncio.to_thread(ollama.pull, model)
                print(f"Model {model} pulled successfully!")
                # Retry once
                def _retry():
                    return ollama.chat(model=model, messages=[
                        {'role': 'user', 'content': prompt}
                    ], options={'num_gpu': 99})

                response = await asyncio.to_thread(_retry)
                content = response['message']['content']
                content = content.replace("```json", "").replace("```", "").strip()
                return {"raw_response": content, "repo_name": context_name}
            except Exception as pull_error:
                return {"raw_response": json.dumps({"error": f"Failed to pull model {model}: {str(pull_error)}"}), "repo_name": context_name}
        return {"raw_response": json.dumps({"error": str(e)}), "repo_name": context_name}
    except Exception as e:
        print(f"Ollama error: {e}")
        return {"raw_response": json.dumps({"error": f"Ollama connection failed: {str(e)}"}), "repo_name": context_name}

async def analyze_single_repo(owner: str, repo: str, token: str = None):
    repo_data, languages, readme = await fetch_github_data(owner, repo, token)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found or private")

    # Use full README content for better analysis
    readme_content = readme[:10000] if readme else "No README available"
    repo_description = repo_data.get('description', 'No description provided')
    
    prompt = f"""
You are a technical analyst. Analyze this GitHub repository and extract structured information.

Repository: {repo_data.get('name')}
GitHub Description: {repo_description}
Languages: {', '.join(languages.keys())}

Full README Content:
{readme_content}

Extract and provide:
1. **what_it_does**: A clear 2-3 sentence description of the project's purpose and functionality
2. **tech_stack**: Complete list of technologies (languages, frameworks, libraries, databases, tools)
3. **key_features**: 3-5 main features or capabilities
4. **domain**: Choose EXACTLY ONE from:
   - "Machine Learning" (AI, ML, neural networks, computer vision, NLP, deep learning)
   - "Data Science" (data analysis, visualization, analytics, data pipelines, statistics)
   - "Full Stack" (both frontend and backend components)
   - "Frontend" (UI, UX, web design, client-side, React, Vue, Angular)
   - "Backend" (APIs, servers, databases, microservices, server-side)
   - "Mobile App" (Android, iOS, React Native, Flutter, mobile development)
   - "DevOps" (CI/CD, Docker, Kubernetes, infrastructure, cloud, automation)
   - "Other" (if none above fit)

IMPORTANT:
- Analyze the README thoroughly to extract accurate information
- Infer tech stack from dependencies, code examples, and setup instructions
- Determine domain based on project purpose and technologies used
- If README is minimal, infer from repo description and languages

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "what_it_does": "description here",
  "tech_stack": ["tech1", "tech2"],
  "key_features": ["feature1", "feature2"],
  "domain": "Domain Name"
}}
"""
    
    return await run_llm(prompt, repo_data.get('name'))

def save_to_dataset(repos_data: List[Dict[str, Any]], username: str):
    """
    Saves extracted repository information into a JSONL file in data/Git_details/{username}/
    Also generates a fine-tuning dataset in 'alpaca' format for the 'energetic friend' persona.
    """
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Git_details", username)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        
    # 1. Save raw data for RAG
    dataset_path = os.path.join(base_dir, "data.jsonl")
    with open(dataset_path, "a", encoding="utf-8") as f:
        for repo in repos_data:
            f.write(json.dumps(repo) + "\n")
            
    # 2. Save Fine-Tuning Data (Alpaca Format)
    ft_path = os.path.join(base_dir, "fine_tune_data.jsonl")
    with open(ft_path, "a", encoding="utf-8") as f:
        for repo in repos_data:
            name = repo.get("name", "Project")
            desc = repo.get("what_it_does", "A cool project.")
            stack = ", ".join(repo.get("tech_stack", []))
            features = ", ".join(repo.get("key_features", []))
            domain = repo.get("domain", "Software Engineering")
            
            # Instruction 1: Describe the project
            entry1 = {
                "instruction": f"What is the project {name} about?",
                "input": "",
                "output": f"Yo! So {name} is this awesome {domain} project that {desc} It's built using {stack}. Check it out!"
            }
            f.write(json.dumps(entry1) + "\n")
            
            # Instruction 2: Resume Bullet Point
            entry2 = {
                "instruction": f"Write a resume bullet point for {name}.",
                "input": "",
                "output": f"🚀 Engineered {name}, a high-impact {domain} solution that {desc}, leveraging {stack} to deliver {features}."
            }
            f.write(json.dumps(entry2) + "\n")
            
            # Instruction 3: Tech Stack
            entry3 = {
                "instruction": f"What tech stack does {name} use?",
                "input": "",
                "output": f"For {name}, we went full beast mode with {stack}! It's a solid {domain} setup."
            }
            f.write(json.dumps(entry3) + "\n")
            
            # Instruction 4: Domain Query
            entry4 = {
                "instruction": f"What kind of project is {name}?",
                "input": "",
                "output": f"{name} is a {domain} project."
            }
            f.write(json.dumps(entry4) + "\n")
    
    print(f"Saved {len(repos_data)} repos to {dataset_path} and fine-tuning data to {ft_path}")

async def analyze_user_profile(owner: str, token: str, username: str):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    # Set reasonable timeouts
    timeout = httpx.Timeout(10.0, read=30.0)
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=timeout) as client:
        # Fetch user repos
        repos_resp = await client.get(f"https://api.github.com/users/{owner}/repos?per_page=100&sort=updated")
        if repos_resp.status_code != 200:
            print(f"Failed to fetch repos for {owner}: {repos_resp.status_code}")
            return {"type": "profile", "owner": owner, "repos": []}
        repos = repos_resp.json()

    # Fetch details for all repos with concurrency limit
    print(f"Found {len(repos)} repos. Fetching details...")
    sem = asyncio.Semaphore(3) # Limit to 3 concurrent requests to avoid timeouts

    async def fetch_with_sem(repo_name):
        async with sem:
            # Add a small delay to be nice to the API
            await asyncio.sleep(0.8)
            return await fetch_github_data(owner, repo_name, token)

    tasks = [fetch_with_sem(r['name']) for r in repos]
    results = await asyncio.gather(*tasks)
    
    # Filter out failed fetches
    valid_results = [r for r in results if r[0] is not None]
    print(f"Successfully fetched details for {len(valid_results)}/{len(repos)} repos.")
    
    if not valid_results:
        return {"type": "profile", "owner": owner, "repos": []}

    # Process in batches of 5
    batch_size = 5
    final_repos = []
    
    for i in range(0, len(valid_results), batch_size):
        batch = valid_results[i:i + batch_size]
        
        prompt = f"You are a technical analyst. Analyze these {len(batch)} GitHub repositories for user '{owner}'.\n\n"
        
        for j, (repo_data, languages, readme) in enumerate(batch):
            readme_snippet = readme[:2000] if readme else "No README"
            prompt += f"""
=== Repository {j+1} ===
Name: {repo_data.get('name')}
Description: {repo_data.get('description', 'None')}
Languages: {', '.join(languages.keys())}
Stars: {repo_data.get('stargazers_count', 0)}

README Content:
{readme_snippet}
========================

"""
        
        prompt += """
For EACH repository, analyze the README and extract:

1. **name**: Repository name
2. **what_it_does**: Clear description of purpose (2-3 sentences, infer from README, description, and languages)
3. **tech_stack**: List ALL technologies found (languages, frameworks, libraries, databases, tools)
4. **key_features**: 3-5 main features or capabilities
5. **domain**: Choose EXACTLY ONE:
   - "Machine Learning" (AI, ML, neural networks, computer vision, NLP, deep learning, models)
   - "Data Science" (data analysis, visualization, analytics, data pipelines, statistics, BI)
   - "Full Stack" (both frontend AND backend components)
   - "Frontend" (UI, UX, web design, client-side, React, Vue, Angular, HTML/CSS)
   - "Backend" (APIs, servers, databases, microservices, server-side, REST, GraphQL)
   - "Mobile App" (Android, iOS, React Native, Flutter, mobile development)
   - "DevOps" (CI/CD, Docker, Kubernetes, infrastructure, cloud, automation, deployment)
   - "Other" (if none fit)

Guidelines:
- Read README thoroughly for accurate tech stack
- Infer from setup instructions, dependencies, imports
- If README is minimal, use repo description and primary language
- Domain should match project's PRIMARY purpose

Return ONLY a valid JSON array (no markdown, no ```json):
[{"name": "repo1", "what_it_does": "...", "tech_stack": [...], "key_features": [...], "domain": "Domain"}, ...]
"""
        
        print(f"Debug: Processing batch {i//batch_size + 1}...")
        llm_response = await run_llm(prompt, f"{owner}'s Profile Batch {i}")
        
        # Check if LLM response is valid
        if not llm_response or 'raw_response' not in llm_response:
            print(f"Batch {i} failed: No response from LLM")
            continue
            
        try:
            raw = llm_response['raw_response']
            
            # Check if response contains an error
            try:
                error_check = json.loads(raw)
                if isinstance(error_check, dict) and 'error' in error_check:
                    print(f"Batch {i} failed with error: {error_check['error']}")
                    continue
            except:
                pass
            
            # Try to find a JSON list in the response using regex
            import re
            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                json_str = match.group(0)
                batch_parsed = json.loads(json_str)
            else:
                # Fallback to direct parsing
                batch_parsed = json.loads(raw)
                
            if isinstance(batch_parsed, list):
                final_repos.extend(batch_parsed)
            else:
                print(f"Warning: Batch {i} parsed but not a list: {type(batch_parsed)}")
                
        except Exception as e:
            print(f"Failed to parse batch {i}. Error: {e}")
            if llm_response and 'raw_response' in llm_response:
                print(f"Raw response snippet: {llm_response['raw_response'][:200]}...")
            continue

    # Save to dataset
    if final_repos:
        save_to_dataset(final_repos, username)
        # Add to RAG
        for repo in final_repos:
            try:
                rag_service.add_repo_data(repo, username)
            except Exception as e:
                print(f"Failed to add {repo.get('name')} to RAG: {e}")

    return {
        "type": "profile",
        "owner": owner,
        "repos": final_repos
    } 

async def run_analysis_job(job_id: str, target_url: str, github_token: str, username: str):
    """Background task to run GitHub analysis"""
    try:
        analysis_jobs[job_id] = {
            'status': 'processing',
            'progress': 'Starting analysis...',
            'result': None,
            'error': None
        }
        
        clean_url = target_url.strip()
        
        # Remove protocol
        if clean_url.startswith("https://"):
            clean_url = clean_url[8:]
        elif clean_url.startswith("http://"):
            clean_url = clean_url[7:]
            
        # Remove domain
        if clean_url.startswith("github.com/"):
            clean_url = clean_url[11:]
        elif clean_url.startswith("www.github.com/"):
            clean_url = clean_url[15:]
            
        parts = [p for p in clean_url.split("/") if p]
        
        if len(parts) == 0:
            raise ValueError("Invalid URL")
        
        owner = parts[0]
        if len(parts) == 1:
            # User Profile Mode
            analysis_jobs[job_id]['progress'] = f'Analyzing GitHub profile for {owner}...'
            result = await analyze_user_profile(owner, github_token, username)
        else:
            # Single Repo Mode
            repo = parts[1]
            if repo.endswith(".git"):
                repo = repo[:-4]
            analysis_jobs[job_id]['progress'] = f'Analyzing repository {owner}/{repo}...'
            result = await analyze_single_repo(owner, repo, github_token)
            
            # Save single repo to dataset
            try:
                parsed = json.loads(result['raw_response'])
                if 'name' not in parsed:
                    parsed['name'] = result['repo_name']
                save_to_dataset([parsed], username)
                
                try:
                    rag_service.add_repo_data(parsed, username)
                except Exception as e:
                    print(f"Failed to add repo to RAG: {e}")
                
                result = {
                    "type": "repo",
                    "repo_name": result['repo_name'],
                    "data": parsed
                }
            except Exception as e:
                print(f"Failed to parse single repo: {e}")
        
        analysis_jobs[job_id] = {
            'status': 'completed',
            'progress': 'Analysis complete!',
            'result': result,
            'error': None
        }
        
    except Exception as e:
        import traceback
        print(f"Error in analysis job {job_id}: {e}")
        traceback.print_exc()
        analysis_jobs[job_id] = {
            'status': 'failed',
            'progress': 'Analysis failed',
            'result': None,
            'error': str(e)
        }

@app.post("/analyze")
async def analyze_repo(request: RepoRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """Start GitHub analysis as background task"""
    try:
        # Use user's GitHub URL if not provided
        target_url = request.url or current_user.github_url
        if not target_url:
             raise HTTPException(status_code=400, detail="No GitHub URL provided or found in profile")

        # Generate unique job ID
        job_id = f"{current_user.username}_{int(datetime.now().timestamp() * 1000)}"
        
        # Start background task
        background_tasks.add_task(
            run_analysis_job,
            job_id,
            target_url,
            current_user.github_token,
            current_user.username
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Analysis started in background. Check /analysis-status/{job_id} for progress."
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis-status/{job_id}")
async def get_analysis_status(job_id: str, current_user: User = Depends(get_current_user)):
    """Check the status of a background analysis job"""
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data = analysis_jobs[job_id]
    return {
        "job_id": job_id,
        "status": job_data['status'],
        "progress": job_data['progress'],
        "result": job_data['result'],
        "error": job_data['error']
    }

@app.post("/fine-tune")
async def trigger_fine_tuning(current_user: User = Depends(get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    """
    Triggers the fine-tuning process for the current user.
    Runs in the background.
    """
    try:
        # Check if data exists
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Git_details", current_user.username, "fine_tune_data.jsonl")
        if not os.path.exists(data_path):
            raise HTTPException(status_code=400, detail="No training data found. Please analyze your GitHub profile first.")

        # Import here to avoid startup errors if unsloth is missing
        try:
            from backend.fine_tune_service import fine_tune_model
        except ImportError:
            try:
                from fine_tune_service import fine_tune_model
            except ImportError:
                raise HTTPException(status_code=500, detail="Unsloth is not installed. Please install it to use GPU fine-tuning.")

        # Run in background
        background_tasks.add_task(fine_tune_model, current_user.username)
        
        return {"status": "started", "message": "Fine-tuning started in background. This may take a while."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gpu-status")
def get_gpu_status():
    try:
        import torch
        return {
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count(),
            "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
    except ImportError:
        return {"error": "PyTorch not installed"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Code2Resume API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
