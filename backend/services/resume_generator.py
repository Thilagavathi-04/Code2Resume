import asyncio
from typing import Dict, List, Any, Optional
from services.github_service import GitHubService
from services.prompt_builder import PromptBuilder
from models.llm_handler import LLMHandler
from config.settings import settings

class ResumeGenerator:
    """Main service for orchestrating resume content generation"""
    
    def __init__(self, github_service: GitHubService, prompt_builder: PromptBuilder, llm_handler: LLMHandler):
        self.github_service = github_service
        self.prompt_builder = prompt_builder
        self.llm_handler = llm_handler
    
    async def generate_from_github(self, 
                                 repo_url: str, 
                                 target_role: str,
                                 user_role: Optional[str] = None) -> Dict[str, Any]:
        """Generate resume content from GitHub repository"""
        try:
            # Step 1: Analyze GitHub repository
            print(f"Analyzing GitHub repository: {repo_url}")
            repo_data = await self.github_service.analyze_repository(repo_url)
            
            # Step 2: Build prompt for LLM
            print("Building prompt for LLM generation...")
            prompt = self.prompt_builder.build_github_prompt(
                repo_data=repo_data,
                target_role=target_role,
                user_role=user_role
            )
            
            # Step 3: Generate content using LLM
            print("Generating resume content with LLM...")
            llm_response = await self.llm_handler.generate_resume_content(prompt)
            
            # Step 4: Format final response
            result = self._format_response(
                project_name=repo_data.get('name', 'Unknown Project'),
                llm_response=llm_response,
                metadata={
                    'source': 'github',
                    'repo_url': repo_url,
                    'stars': repo_data.get('stars', 0),
                    'primary_language': repo_data.get('language'),
                    'project_type': repo_data.get('project_type')
                }
            )
            
            print("Resume content generation completed successfully")
            return result
            
        except Exception as e:
            print(f"GitHub resume generation failed: {str(e)}")
            # Return fallback content with error indication
            return self._generate_fallback_response(
                project_name=self._extract_project_name_from_url(repo_url),
                target_role=target_role,
                error_message=str(e)
            )
    
    async def generate_from_manual(self,
                                 project_name: str,
                                 project_description: str,
                                 tech_stack: str,
                                 target_role: str,
                                 user_role: Optional[str] = None) -> Dict[str, Any]:
        """Generate resume content from manual project input"""
        try:
            # Step 1: Build prompt for LLM
            print("Building prompt from manual input...")
            prompt = self.prompt_builder.build_manual_prompt(
                project_name=project_name,
                project_description=project_description,
                tech_stack=tech_stack,
                target_role=target_role,
                user_role=user_role
            )
            
            # Step 2: Generate content using LLM
            print("Generating resume content with LLM...")
            llm_response = await self.llm_handler.generate_resume_content(prompt)
            
            # Step 3: Format final response
            result = self._format_response(
                project_name=project_name,
                llm_response=llm_response,
                metadata={
                    'source': 'manual',
                    'tech_stack_input': tech_stack,
                    'description_length': len(project_description)
                }
            )
            
            print("Manual resume content generation completed successfully")
            return result
            
        except Exception as e:
            print(f"Manual resume generation failed: {str(e)}")
            # Return fallback content with error indication
            return self._generate_fallback_response(
                project_name=project_name,
                target_role=target_role,
                error_message=str(e)
            )
    
    def _format_response(self, 
                        project_name: str, 
                        llm_response: Dict[str, Any], 
                        metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format the final response for the API"""
        return {
            'success': True,
            'project_name': project_name,
            'summary': llm_response.get('summary', ''),
            'bullet_points': llm_response.get('bullet_points', []),
            'tech_stack_line': llm_response.get('tech_stack_line', ''),
            'portfolio_version': llm_response.get('portfolio_version', ''),
            'metadata': metadata
        }
    
    def _generate_fallback_response(self, 
                                   project_name: str, 
                                   target_role: str, 
                                   error_message: str) -> Dict[str, Any]:
        """Generate fallback response when main generation fails"""
        
        # Create basic resume content as fallback
        summary = f"Experienced {target_role.lower()} with hands-on experience in {project_name} development using modern technologies and best practices."
        
        bullet_points = [
            f"Developed and maintained {project_name} using modern software engineering practices",
            f"Implemented scalable solutions addressing complex technical requirements",
            f"Collaborated with development teams to deliver high-quality software products",
            f"Applied {target_role.lower()} expertise to optimize performance and user experience"
        ]
        
        tech_stack_line = "Tech: Modern programming languages, frameworks, and development tools"
        
        portfolio_version = f"{project_name} is a comprehensive software project that demonstrates proficiency in {target_role.lower()} skills. The project showcases ability to design, implement, and maintain software solutions using industry-standard practices and modern technologies."
        
        return {
            'success': False,  # Indicate this is fallback content
            'project_name': project_name,
            'summary': summary,
            'bullet_points': bullet_points,
            'tech_stack_line': tech_stack_line,
            'portfolio_version': portfolio_version,
            'metadata': {
                'source': 'fallback',
                'error': error_message,
                'note': 'This is generated fallback content due to processing error'
            }
        }
    
    def _extract_project_name_from_url(self, repo_url: str) -> str:
        """Extract project name from GitHub URL for fallback"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(repo_url)
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) >= 2:
                return path_parts[1]
        except Exception:
            pass
        return "Project"
    
    async def validate_inputs(self, source_type: str, **kwargs) -> Dict[str, Any]:
        """Validate inputs before processing"""
        errors = []
        
        if source_type == 'github':
            repo_url = kwargs.get('repo_url')
            if not repo_url:
                errors.append("Repository URL is required for GitHub source")
            elif 'github.com' not in repo_url:
                errors.append("Invalid GitHub repository URL")
        
        elif source_type == 'manual':
            required_fields = ['project_name', 'project_description', 'tech_stack']
            for field in required_fields:
                if not kwargs.get(field):
                    errors.append(f"{field.replace('_', ' ').title()} is required for manual input")
        
        target_role = kwargs.get('target_role')
        if not target_role:
            errors.append("Target role is required")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def get_generation_status(self) -> Dict[str, Any]:
        """Get status of generation services"""
        try:
            # Test LLM connection
            llm_status = await self.llm_handler.test_connection()
            
            return {
                'service_status': 'operational',
                'llm_status': llm_status,
                'github_service': 'available',
                'prompt_builder': 'available'
            }
        except Exception as e:
            return {
                'service_status': 'error',
                'error': str(e),
                'llm_status': {'status': 'unknown'},
                'github_service': 'unknown',
                'prompt_builder': 'unknown'
            }