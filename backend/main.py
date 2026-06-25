import os
import re
import base64
import httpx
import ollama
import asyncio
import traceback
from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.database import engine, get_db, Base
from backend.models.user import User
from backend.services.rag_service import RAGService
from backend.services.agent_service import AgentService

Base.metadata.create_all(bind=engine)

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-keep-it-secret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app = FastAPI(title="Code2Resume API")

analysis_jobs = {}

rag_service = RAGService()
agent_service = AgentService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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


@app.post("/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

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
        mobile_number=user.mobile_number,
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
        mobile_number=current_user.mobile_number,
    )


@app.put("/auth/me", response_model=UserResponse)
async def update_user(user_update: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        mobile_number=current_user.mobile_number,
    )


class RepoRequest(BaseModel):
    url: Optional[str] = None


class AskRequest(BaseModel):
    query: str


class ResumeRequest(BaseModel):
    query: str
    domain: Optional[str] = None


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
    try:
        async def generate():
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
    try:
        repos = rag_service.get_user_repos(current_user.username)
        return repos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-resume")
async def generate_resume_file(request: ResumeRequest, current_user: User = Depends(get_current_user)):
    try:
        latex_content = agent_service.generate_resume(
            request.query,
            username=current_user.username,
            model="mistral:latest",
        )

        if latex_content.startswith("Error"):
            raise HTTPException(status_code=500, detail=latex_content)

        resumes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "resumes")
        os.makedirs(resumes_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"resume_{current_user.username}_{timestamp}.tex"
        filepath = os.path.join(resumes_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(latex_content)

        return {
            "success": True,
            "filename": filename,
            "message": "Resume generated successfully! Click below to download.",
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str, current_user: User = Depends(get_current_user)):
    try:
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")

        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tmp")
        filepath = os.path.join(tmp_dir, filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="File not found")

        if current_user.username not in filename:
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type="application/x-tex",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/resumes")
async def list_resumes(current_user: User = Depends(get_current_user)):
    try:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes"),
        ]

        user_files = []
        for directory in directories:
            if not os.path.exists(directory):
                continue
            for filename in os.listdir(directory):
                if filename.startswith(f"resume_{current_user.username}_") and filename.endswith(".tex"):
                    filepath = os.path.join(directory, filename)
                    stats = os.stat(filepath)
                    parts = filename[:-4].split("_", 3)
                    query = parts[3].replace("_", " ") if len(parts) > 3 else "Resume"
                    user_files.append({
                        "filename": filename,
                        "query": query,
                        "created_at": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        "size": stats.st_size,
                    })

        user_files.sort(key=lambda x: x["created_at"], reverse=True)
        return user_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download-resume/{filename}")
async def download_resume(filename: str, current_user: User = Depends(get_current_user)):
    try:
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        if not filename.startswith(f"resume_{current_user.username}_"):
            raise HTTPException(status_code=403, detail="Access denied")

        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes"),
        ]

        for directory in directories:
            potential_path = os.path.join(directory, filename)
            if os.path.exists(potential_path):
                return FileResponse(
                    path=potential_path,
                    filename=filename,
                    media_type="application/x-tex",
                    headers={"Content-Disposition": f"attachment; filename={filename}"},
                )

        raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/delete-resume/{filename}")
async def delete_resume(filename: str, current_user: User = Depends(get_current_user)):
    try:
        if ".." in filename or "/" in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        if not filename.startswith(f"resume_{current_user.username}_"):
            raise HTTPException(status_code=403, detail="Access denied")

        base_dir = os.path.dirname(os.path.dirname(__file__))
        directories = [
            os.path.join(base_dir, "tmp"),
            os.path.join(base_dir, "data", "resumes"),
        ]

        for directory in directories:
            potential_path = os.path.join(directory, filename)
            if os.path.exists(potential_path):
                os.remove(potential_path)
                return {"success": True, "message": "Resume deleted successfully"}

        raise HTTPException(status_code=404, detail="File not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def fetch_github_data(owner: str, repo: str, token: str):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    timeout = httpx.Timeout(10.0, read=30.0)
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=timeout) as client:
        try:
            repo_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        except (httpx.ConnectTimeout, httpx.ReadTimeout):
            return None, None, None

        if repo_resp.status_code == 403 or repo_resp.status_code != 200:
            return None, None, None
        repo_data = repo_resp.json()

        lang_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/languages")
        languages = lang_resp.json() if lang_resp.status_code == 200 else {}

        readme_resp = await client.get(f"https://api.github.com/repos/{owner}/{repo}/readme")
        readme_content = ""
        if readme_resp.status_code == 200:
            try:
                readme_content = base64.b64decode(readme_resp.json()["content"]).decode("utf-8")
            except Exception:
                readme_content = "Could not decode README."

        return repo_data, languages, readme_content


async def run_llm(prompt: str, context_name: str):
    model = "mistral:latest"
    try:
        try:
            await asyncio.to_thread(ollama.list)
        except Exception as conn_error:
            return {"raw_response": json.dumps({"error": "Ollama service is not running. Please start it with: ollama serve"}), "repo_name": context_name}

        def _chat():
            return ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}], options={'num_gpu': 99})

        response = await asyncio.to_thread(_chat)
        content = response['message']['content'].replace("```json", "").replace("```", "").strip()
        return {"raw_response": content, "repo_name": context_name}
    except ollama.ResponseError as e:
        if e.status_code == 404:
            try:
                await asyncio.to_thread(ollama.pull, model)
                def _retry():
                    return ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}], options={'num_gpu': 99})
                response = await asyncio.to_thread(_retry)
                content = response['message']['content'].replace("```json", "").replace("```", "").strip()
                return {"raw_response": content, "repo_name": context_name}
            except Exception as pull_error:
                return {"raw_response": json.dumps({"error": f"Failed to pull model {model}: {str(pull_error)}"}), "repo_name": context_name}
        return {"raw_response": json.dumps({"error": str(e)}), "repo_name": context_name}
    except Exception as e:
        return {"raw_response": json.dumps({"error": f"Ollama connection failed: {str(e)}"}), "repo_name": context_name}


async def analyze_single_repo(owner: str, repo: str, token: str = None):
    repo_data, languages, readme = await fetch_github_data(owner, repo, token)
    if not repo_data:
        raise HTTPException(status_code=404, detail="Repository not found or private")

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
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Git_details", username)
    os.makedirs(base_dir, exist_ok=True)

    dataset_path = os.path.join(base_dir, "data.jsonl")
    with open(dataset_path, "a", encoding="utf-8") as f:
        for repo in repos_data:
            f.write(json.dumps(repo) + "\n")

    ft_path = os.path.join(base_dir, "fine_tune_data.jsonl")
    with open(ft_path, "a", encoding="utf-8") as f:
        for repo in repos_data:
            name = repo.get("name", "Project")
            desc = repo.get("what_it_does", "A cool project.")
            stack = ", ".join(repo.get("tech_stack", []))
            features = ", ".join(repo.get("key_features", []))
            domain = repo.get("domain", "Software Engineering")

            entries = [
                {"instruction": f"What is the project {name} about?", "input": "", "output": f"Yo! So {name} is this awesome {domain} project that {desc} It's built using {stack}. Check it out!"},
                {"instruction": f"Write a resume bullet point for {name}.", "input": "", "output": f"Engineered {name}, a high-impact {domain} solution that {desc}, leveraging {stack} to deliver {features}."},
                {"instruction": f"What tech stack does {name} use?", "input": "", "output": f"For {name}, we went full beast mode with {stack}! It's a solid {domain} setup."},
                {"instruction": f"What kind of project is {name}?", "input": "", "output": f"{name} is a {domain} project."},
            ]
            for entry in entries:
                f.write(json.dumps(entry) + "\n")


async def analyze_user_profile(owner: str, token: str, username: str):
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    timeout = httpx.Timeout(10.0, read=30.0)
    async with httpx.AsyncClient(follow_redirects=True, headers=headers, timeout=timeout) as client:
        repos_resp = await client.get(f"https://api.github.com/users/{owner}/repos?per_page=100&sort=updated")
        if repos_resp.status_code != 200:
            return {"type": "profile", "owner": owner, "repos": []}
        repos = repos_resp.json()

    print(f"Found {len(repos)} repos. Fetching details...")
    sem = asyncio.Semaphore(3)

    async def fetch_with_sem(repo_name):
        async with sem:
            await asyncio.sleep(0.8)
            return await fetch_github_data(owner, repo_name, token)

    tasks = [fetch_with_sem(r['name']) for r in repos]
    results = await asyncio.gather(*tasks)
    valid_results = [r for r in results if r[0] is not None]
    print(f"Successfully fetched details for {len(valid_results)}/{len(repos)} repos.")

    if not valid_results:
        return {"type": "profile", "owner": owner, "repos": []}

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
2. **what_it_does**: Clear description of purpose (2-3 sentences)
3. **tech_stack**: List ALL technologies found
4. **key_features**: 3-5 main features or capabilities
5. **domain**: Choose EXACTLY ONE from: "Machine Learning", "Data Science", "Full Stack", "Frontend", "Backend", "Mobile App", "DevOps", "Other"

Return ONLY a valid JSON array (no markdown, no ```json):
[{"name": "repo1", "what_it_does": "...", "tech_stack": [...], "key_features": [...], "domain": "Domain"}, ...]
"""

        llm_response = await run_llm(prompt, f"{owner}'s Profile Batch {i}")

        if not llm_response or 'raw_response' not in llm_response:
            continue

        try:
            raw = llm_response['raw_response']
            try:
                error_check = json.loads(raw)
                if isinstance(error_check, dict) and 'error' in error_check:
                    continue
            except Exception:
                pass

            match = re.search(r'\[.*\]', raw, re.DOTALL)
            if match:
                batch_parsed = json.loads(match.group(0))
            else:
                batch_parsed = json.loads(raw)

            if isinstance(batch_parsed, list):
                final_repos.extend(batch_parsed)
        except Exception as e:
            print(f"Failed to parse batch {i}. Error: {e}")
            continue

    if final_repos:
        save_to_dataset(final_repos, username)
        for repo in final_repos:
            try:
                rag_service.add_repo_data(repo, username)
            except Exception as e:
                print(f"Failed to add {repo.get('name')} to RAG: {e}")

    return {"type": "profile", "owner": owner, "repos": final_repos}


async def run_analysis_job(job_id: str, target_url: str, github_token: str, username: str):
    try:
        analysis_jobs[job_id] = {'status': 'processing', 'progress': 'Starting analysis...', 'result': None, 'error': None}

        clean_url = target_url.strip()
        if clean_url.startswith("https://"):
            clean_url = clean_url[8:]
        elif clean_url.startswith("http://"):
            clean_url = clean_url[7:]

        if clean_url.startswith("github.com/"):
            clean_url = clean_url[11:]
        elif clean_url.startswith("www.github.com/"):
            clean_url = clean_url[15:]

        parts = [p for p in clean_url.split("/") if p]
        if len(parts) == 0:
            raise ValueError("Invalid URL")

        owner = parts[0]
        if len(parts) == 1:
            analysis_jobs[job_id]['progress'] = f'Analyzing GitHub profile for {owner}...'
            result = await analyze_user_profile(owner, github_token, username)
        else:
            repo = parts[1]
            if repo.endswith(".git"):
                repo = repo[:-4]
            analysis_jobs[job_id]['progress'] = f'Analyzing repository {owner}/{repo}...'
            result = await analyze_single_repo(owner, repo, github_token)

            try:
                parsed = json.loads(result['raw_response'])
                if 'name' not in parsed:
                    parsed['name'] = result['repo_name']
                save_to_dataset([parsed], username)
                try:
                    rag_service.add_repo_data(parsed, username)
                except Exception as e:
                    print(f"Failed to add repo to RAG: {e}")
                result = {"type": "repo", "repo_name": result['repo_name'], "data": parsed}
            except Exception as e:
                print(f"Failed to parse single repo: {e}")

        analysis_jobs[job_id] = {'status': 'completed', 'progress': 'Analysis complete!', 'result': result, 'error': None}

    except Exception as e:
        traceback.print_exc()
        analysis_jobs[job_id] = {'status': 'failed', 'progress': 'Analysis failed', 'result': None, 'error': str(e)}


@app.post("/analyze")
async def analyze_repo(request: RepoRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    try:
        target_url = request.url or current_user.github_url
        if not target_url:
            raise HTTPException(status_code=400, detail="No GitHub URL provided or found in profile")

        job_id = f"{current_user.username}_{int(datetime.now().timestamp() * 1000)}"
        background_tasks.add_task(run_analysis_job, job_id, target_url, current_user.github_token, current_user.username)

        return {"job_id": job_id, "status": "started", "message": "Analysis started in background."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analysis-status/{job_id}")
async def get_analysis_status(job_id: str, current_user: User = Depends(get_current_user)):
    if job_id not in analysis_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job_data = analysis_jobs[job_id]
    return {"job_id": job_id, "status": job_data['status'], "progress": job_data['progress'], "result": job_data['result'], "error": job_data['error']}


@app.post("/fine-tune")
async def trigger_fine_tuning(current_user: User = Depends(get_current_user), background_tasks: BackgroundTasks = BackgroundTasks()):
    try:
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Git_details", current_user.username, "fine_tune_data.jsonl")
        if not os.path.exists(data_path):
            raise HTTPException(status_code=400, detail="No training data found. Please analyze your GitHub profile first.")

        try:
            from backend.fine_tune_service import fine_tune_model
        except ImportError:
            try:
                from fine_tune_service import fine_tune_model
            except ImportError:
                raise HTTPException(status_code=500, detail="Unsloth is not installed.")

        background_tasks.add_task(fine_tune_model, current_user.username)
        return {"status": "started", "message": "Fine-tuning started in background."}
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
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        }
    except ImportError:
        return {"error": "PyTorch not installed"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Code2Resume API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
