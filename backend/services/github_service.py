import requests
import re
import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import base64
from config.settings import settings

class GitHubService:
    """Service to interact with GitHub API and extract repository information"""
    
    def __init__(self, user_token: str = None):
        self.base_url = settings.github_api_base
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Code2Resume/1.0'
        }
        
        token = user_token or settings.github_token
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    async def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Extract comprehensive information from a GitHub repository
        """
        try:
            owner, repo = self._parse_repo_url(repo_url)
            
            # Fetch repository metadata
            repo_data = await self._fetch_repo_data(owner, repo)
            
            # Fetch README content
            readme_content = await self._fetch_readme(owner, repo)
            
            # Fetch language statistics
            languages = await self._fetch_languages(owner, repo)
            
            # Analyze repository structure
            structure = await self._analyze_structure(owner, repo)
            
            return {
                'name': repo_data['name'],
                'description': repo_data.get('description', ''),
                'stars': repo_data.get('stargazers_count', 0),
                'forks': repo_data.get('forks_count', 0),
                'language': repo_data.get('language'),
                'languages': languages,
                'readme_content': readme_content,
                'topics': repo_data.get('topics', []),
                'created_at': repo_data.get('created_at'),
                'updated_at': repo_data.get('updated_at'),
                'size': repo_data.get('size', 0),
                'structure': structure,
                'tech_stack': self._detect_tech_stack(languages, readme_content, structure),
                'project_type': self._classify_project_type(repo_data, readme_content, structure)
            }
        
        except Exception as e:
            raise Exception(f"Failed to analyze repository: {str(e)}")
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Extract owner and repo name from GitHub URL"""
        parsed = urlparse(repo_url)
        
        if parsed.netloc != 'github.com':
            raise ValueError("Invalid GitHub URL")
        
        path_parts = parsed.path.strip('/').split('/')
        if len(path_parts) < 2:
            raise ValueError("Invalid GitHub repository URL format")
        
        return path_parts[0], path_parts[1]
    
    async def _fetch_repo_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository metadata from GitHub API"""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch repository data: {str(e)}")
    
    async def _fetch_readme(self, owner: str, repo: str) -> str:
        """Fetch README content from repository"""
        readme_files = ['README.md', 'readme.md', 'README.txt', 'README.rst', 'README']
        
        for readme_file in readme_files:
            try:
                url = f"{self.base_url}/repos/{owner}/{repo}/contents/{readme_file}"
                response = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    content_data = response.json()
                    if content_data.get('encoding') == 'base64':
                        content = base64.b64decode(content_data['content']).decode('utf-8')
                        return content[:5000] if len(content) > 5000 else content
                        
            except Exception:
                continue
        
        return ""
    
    async def _fetch_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """Fetch programming languages used in the repository"""
        url = f"{self.base_url}/repos/{owner}/{repo}/languages"
        
        try:
            response = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
    
    async def _analyze_structure(self, owner: str, repo: str) -> Dict[str, Any]:
        """Analyze repository structure to detect frameworks and patterns"""
        try:
            url = f"{self.base_url}/repos/{owner}/{repo}/contents"
            response = await asyncio.to_thread(requests.get, url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                contents = response.json()
                files = [item['name'] for item in contents if item['type'] == 'file']
                dirs = [item['name'] for item in contents if item['type'] == 'dir']
                
                return {
                    'root_files': files,
                    'root_directories': dirs,
                    'has_package_json': 'package.json' in files,
                    'has_requirements_txt': 'requirements.txt' in files,
                    'has_dockerfile': any('Dockerfile' in f for f in files),
                    'has_makefile': 'Makefile' in files or 'makefile' in files,
                    'has_tests': any('test' in d.lower() for d in dirs),
                    'has_docs': any('doc' in d.lower() for d in dirs),
                }
        except Exception:
            pass
        
        return {}
    
    def _detect_tech_stack(self, languages: Dict[str, int], readme: str, structure: Dict[str, Any]) -> List[str]:
        """Detect technology stack from various indicators"""
        tech_stack = []
        
        # Language detection
        if languages:
            # Sort languages by usage
            sorted_langs = sorted(languages.items(), key=lambda x: x[1], reverse=True)
            main_languages = [lang for lang, _ in sorted_langs[:5]]  # Top 5 languages
            tech_stack.extend(main_languages)
        
        # Framework detection from files
        if structure.get('has_package_json'):
            tech_stack.append('Node.js')
        if structure.get('has_requirements_txt'):
            tech_stack.append('Python')
        if structure.get('has_dockerfile'):
            tech_stack.append('Docker')
        
        # Framework detection from README
        framework_patterns = {
            'React': r'\b(react|jsx)\b',
            'Vue.js': r'\b(vue|vuejs)\b',
            'Angular': r'\bangular\b',
            'Django': r'\bdjango\b',
            'Flask': r'\bflask\b',
            'FastAPI': r'\bfastapi\b',
            'Express': r'\bexpress\b',
            'Spring': r'\bspring\b',
            'Laravel': r'\blaravel\b',
            'Rails': r'\brails\b',
            'TensorFlow': r'\btensorflow\b',
            'PyTorch': r'\bpytorch\b',
            'MongoDB': r'\bmongodb\b',
            'PostgreSQL': r'\bpostgresql|postgres\b',
            'MySQL': r'\bmysql\b',
            'Redis': r'\bredis\b',
            'AWS': r'\b(aws|amazon)\b',
            'Docker': r'\bdocker\b',
            'Kubernetes': r'\bkubernetes|k8s\b'
        }
        
        readme_lower = readme.lower()
        for tech, pattern in framework_patterns.items():
            if re.search(pattern, readme_lower, re.IGNORECASE):
                if tech not in tech_stack:
                    tech_stack.append(tech)
        
        return tech_stack[:10]  # Limit to top 10 technologies
    
    def _classify_project_type(self, repo_data: Dict, readme: str, structure: Dict) -> str:
        """Classify the type of project based on available information"""
        description = ((repo_data.get('description') or '') + ' ' + (readme or '')).lower()
        
        # Project type patterns
        if any(keyword in description for keyword in ['machine learning', 'ml', 'ai', 'neural', 'model']):
            return 'Machine Learning'
        elif any(keyword in description for keyword in ['web app', 'website', 'frontend', 'backend']):
            return 'Web Application'
        elif any(keyword in description for keyword in ['mobile', 'android', 'ios', 'flutter', 'react native']):
            return 'Mobile Application'
        elif any(keyword in description for keyword in ['data analysis', 'visualization', 'dashboard']):
            return 'Data Analysis'
        elif any(keyword in description for keyword in ['game', 'gaming']):
            return 'Game Development'
        elif any(keyword in description for keyword in ['tool', 'utility', 'cli']):
            return 'Developer Tool'
        elif any(keyword in description for keyword in ['api', 'service', 'microservice']):
            return 'API/Service'
        else:
            return 'Software Project'