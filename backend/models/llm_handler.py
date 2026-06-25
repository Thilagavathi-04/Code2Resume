import ollama
import openai
import asyncio
import json
import re
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings

class LLMHandler:
    """Handler for LLM integration with Ollama and OpenAI fallback"""
    
    def __init__(self):
        # Ollama configuration
        self.ollama_client = ollama.Client(host=settings.ollama_host)
        self.default_model = settings.default_model
        self.fallback_model = settings.fallback_model
        
        # OpenAI configuration
        if settings.has_openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
            self.openai_model = settings.openai_model
            self.openai_fallback_model = settings.openai_fallback_model
        else:
            self.openai_client = None
            
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
    
    async def generate_resume_content(self, prompt: str) -> Dict[str, Any]:
        """Generate resume content using available LLM (Ollama preferred, OpenAI fallback)"""
        try:
            # First, try to use Ollama
            is_ollama_available = await self._check_ollama_availability()
            
            if is_ollama_available:
                print("Using Ollama for content generation...")
                response = await self._generate_with_ollama(prompt)
                if response:
                    parsed_content = self._parse_llm_response(response)
                    return parsed_content
                    
            # Fallback to OpenAI if Ollama is not available or failed
            if self.openai_client:
                print("Ollama not available, falling back to OpenAI...")
                response = await self._generate_with_openai(prompt)
                if response:
                    parsed_content = self._parse_llm_response(response)
                    return parsed_content
            
            # If both fail, raise exception
            raise Exception("Both Ollama and OpenAI generation failed")
            
        except Exception as e:
            print(f"LLM generation failed: {str(e)}")
            # Return fallback content instead of raising exception
            return self._get_fallback_content()
    
    async def _check_ollama_availability(self) -> bool:
        """Check if Ollama service is running and accessible"""
        try:
            # Test connection with a timeout
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{settings.ollama_host}/api/version")
                return response.status_code == 200
        except Exception:
            return False
    
    async def _generate_with_ollama(self, prompt: str) -> Optional[str]:
        """Generate content using Ollama"""
        try:
            # Try primary model first
            response = await self._generate_with_ollama_model(prompt, self.default_model)
            
            if not response:
                # Fallback to alternative model
                response = await self._generate_with_ollama_model(prompt, self.fallback_model)
            
            return response
            
        except Exception as e:
            print(f"Ollama generation failed: {str(e)}")
            return None
    
    async def _generate_with_ollama_model(self, prompt: str, model: str) -> Optional[str]:
        """Generate content with a specific Ollama model"""
        try:
            # Check if model is available
            if not await self._is_ollama_model_available(model):
                print(f"Model {model} not available, attempting to pull...")
                await self._pull_ollama_model(model)
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._sync_ollama_generate, prompt, model
            )
            
            return response
            
        except Exception as e:
            print(f"Generation with Ollama model {model} failed: {str(e)}")
            return None
    
    def _sync_ollama_generate(self, prompt: str, model: str) -> str:
        """Synchronous Ollama generation for executor"""
        response = self.ollama_client.generate(
            model=model,
            prompt=prompt,
            options={
                'temperature': self.temperature,
                'top_p': 0.9,
                'top_k': 40,
                'num_predict': self.max_tokens,
            }
        )
        return response['response']
    
    async def _is_ollama_model_available(self, model: str) -> bool:
        """Check if an Ollama model is available locally"""
        try:
            models = await asyncio.get_event_loop().run_in_executor(
                None, self.ollama_client.list
            )
            available_models = [m['name'] for m in models['models']]
            return any(model in available_model for available_model in available_models)
        except Exception:
            return False
    
    async def _pull_ollama_model(self, model: str) -> bool:
        """Pull an Ollama model if it's not available locally"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.ollama_client.pull(model)
            )
            return True
        except Exception as e:
            print(f"Failed to pull Ollama model {model}: {str(e)}")
            return False
    
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """Generate content using OpenAI API"""
        try:
            # Try primary OpenAI model first
            response = await self._generate_with_openai_model(prompt, self.openai_model)
            
            if not response:
                # Fallback to alternative OpenAI model
                response = await self._generate_with_openai_model(prompt, self.openai_fallback_model)
            
            return response
            
        except Exception as e:
            print(f"OpenAI generation failed: {str(e)}")
            return None
    
    async def _generate_with_openai_model(self, prompt: str, model: str) -> Optional[str]:
        """Generate content with a specific OpenAI model"""
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer that generates structured content based on code repositories."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(self.max_tokens, 4000),  # OpenAI has token limits
                temperature=self.temperature,
                top_p=0.9
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Generation with OpenAI model {model} failed: {str(e)}")
            return None
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the structured LLM response into components"""
        try:
            # Initialize result structure
            result = {
                'summary': '',
                'bullet_points': [],
                'tech_stack_line': '',
                'portfolio_version': ''
            }
            
            # Clean the response
            response = response.strip()
            
            # Parse sections using regex patterns
            sections = {
                'summary': r'SUMMARY:\s*(.*?)(?=BULLET POINTS:|$)',
                'bullet_points': r'BULLET POINTS:\s*(.*?)(?=TECH STACK:|$)',
                'tech_stack': r'TECH STACK:\s*(.*?)(?=PORTFOLIO VERSION:|$)',
                'portfolio': r'PORTFOLIO VERSION:\s*(.*?)$'
            }
            
            for section_key, pattern in sections.items():
                match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    
                    if section_key == 'summary':
                        result['summary'] = self._clean_text(content)
                    
                    elif section_key == 'bullet_points':
                        # Extract bullet points
                        bullets = []
                        lines = content.split('\n')
                        for line in lines:
                            line = line.strip()
                            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                                bullet = line.lstrip('-•* ').strip()
                                if bullet:
                                    bullets.append(bullet)
                        
                        result['bullet_points'] = bullets[:5]  # Limit to 5 bullets
                    
                    elif section_key == 'tech_stack':
                        result['tech_stack_line'] = self._clean_text(content)
                    
                    elif section_key == 'portfolio':
                        result['portfolio_version'] = self._clean_text(content)
            
            # Validation and fallbacks
            if not result['summary']:
                result['summary'] = "Professional software developer with experience in modern technologies."
            
            if not result['bullet_points']:
                result['bullet_points'] = [
                    "Developed and maintained software applications using modern technologies",
                    "Collaborated with team members to deliver high-quality solutions",
                    "Implemented best practices for code quality and performance"
                ]
            
            if not result['tech_stack_line']:
                result['tech_stack_line'] = "Tech: Various programming languages and frameworks"
            
            if not result['portfolio_version']:
                result['portfolio_version'] = result['summary']
            
            return result
            
        except Exception as e:
            print(f"Failed to parse LLM response: {str(e)}")
            # Return fallback content
            return self._get_fallback_content()
    
    def _clean_text(self, text: str) -> str:
        """Clean and format text content"""
        # Remove extra whitespace and newlines
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove common artifacts
        text = re.sub(r'^(SUMMARY|BULLET POINTS|TECH STACK|PORTFOLIO VERSION):\s*', '', text, flags=re.IGNORECASE)
        
        return text
    
    def _get_fallback_content(self) -> Dict[str, Any]:
        """Provide fallback content when parsing fails"""
        return {
            'summary': "Experienced software developer with expertise in modern development practices and technologies.",
            'bullet_points': [
                "Designed and implemented scalable software solutions using industry best practices",
                "Collaborated with cross-functional teams to deliver high-quality applications",
                "Optimized application performance and maintainability through code refactoring",
                "Integrated modern development tools and frameworks to improve development efficiency"
            ],
            'tech_stack_line': "Tech: Programming languages, frameworks, and development tools",
            'portfolio_version': "Professional software developer with strong technical skills and experience in building modern applications. Focused on writing clean, efficient code and delivering solutions that meet business requirements."
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to available LLM services"""
        result = {
            'ollama_status': 'not_available',
            'openai_status': 'not_available',
            'primary_service': 'none',
            'available_models': [],
            'default_model': self.default_model,
            'fallback_model': self.fallback_model
        }
        
        # Test Ollama connection
        try:
            is_ollama_available = await self._check_ollama_availability()
            if is_ollama_available:
                models = await asyncio.get_event_loop().run_in_executor(
                    None, self.ollama_client.list
                )
                result['ollama_status'] = 'connected'
                result['available_models'].extend([m['name'] for m in models['models']])
                result['primary_service'] = 'ollama'
            else:
                result['ollama_status'] = 'service_not_running'
        except Exception as e:
            result['ollama_status'] = f'error: {str(e)}'
        
        # Test OpenAI connection
        if self.openai_client:
            try:
                # Try a simple API call to test the key
                await self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                result['openai_status'] = 'connected'
                result['available_models'].extend([self.openai_model, self.openai_fallback_model])
                
                # If Ollama is not the primary service, make OpenAI primary
                if result['primary_service'] == 'none':
                    result['primary_service'] = 'openai'
                    
            except Exception as e:
                result['openai_status'] = f'error: {str(e)}'
        else:
            result['openai_status'] = 'no_api_key'
        
        return result
    
    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model (Ollama or OpenAI)"""
        # Check if it's an OpenAI model
        if model in [self.openai_model, self.openai_fallback_model]:
            return {
                'name': model,
                'service': 'openai',
                'available': bool(self.openai_client),
                'description': 'OpenAI GPT model'
            }
        
        # Otherwise, try to get Ollama model info
        try:
            info = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.ollama_client.show(model)
            )
            return {
                'name': model,
                'service': 'ollama',
                'size': info.get('size', 'Unknown'),
                'modified_at': info.get('modified_at', 'Unknown'),
                'available': True
            }
        except Exception as e:
            return {
                'name': model,
                'service': 'ollama',
                'available': False,
                'error': str(e)
            }