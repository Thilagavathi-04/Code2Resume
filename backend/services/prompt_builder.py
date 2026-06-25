from typing import Dict, List, Any, Optional

class PromptBuilder:
    """Service to build structured prompts for LLM generation"""
    
    def __init__(self):
        self.base_template = self._get_base_template()
    
    def build_github_prompt(self, 
                           repo_data: Dict[str, Any], 
                           target_role: str, 
                           user_role: Optional[str] = None) -> str:
        """Build prompt for GitHub repository analysis"""
        
        # Extract key information
        project_name = repo_data.get('name', 'Unknown Project')
        description = repo_data.get('description', '')
        readme_content = repo_data.get('readme_content', '')[:2000]  # Limit for context
        tech_stack = ', '.join(repo_data.get('tech_stack', []))
        project_type = repo_data.get('project_type', 'Software Project')
        stars = repo_data.get('stars', 0)
        
        # Build comprehensive project description
        project_description = self._build_project_description(
            description, readme_content, project_type, stars
        )
        
        return self.base_template.format(
            project_name=project_name,
            project_description=project_description,
            tech_stack=tech_stack,
            user_role=user_role or "Developer",
            target_role=target_role,
            github_data_optional=self._format_github_metadata(repo_data)
        )
    
    def build_manual_prompt(self, 
                           project_name: str,
                           project_description: str,
                           tech_stack: str,
                           target_role: str,
                           user_role: Optional[str] = None) -> str:
        """Build prompt for manual project input"""
        
        return self.base_template.format(
            project_name=project_name,
            project_description=project_description,
            tech_stack=tech_stack,
            user_role=user_role or "Developer",
            target_role=target_role,
            github_data_optional=""
        )
    
    def _get_base_template(self) -> str:
        """Get the base prompt template for resume generation"""
        return """You are an expert technical resume writer.

Your goal is to convert the following project information into:
1. A short professional project summary (2–3 lines)
2. 3–5 strong ATS-friendly resume bullet points
3. A clean tech stack line
4. Optional: a more descriptive portfolio version

Write everything in clean, measurable, action-driven language.

---

### USER PROJECT INFORMATION
Project Name: {project_name}
Project Description: {project_description}
Technologies Used: {tech_stack}
User Role: {user_role}
Target Job Role: {target_role}

{github_data_optional}

---

### RULES FOR OUTPUT
• Start with a 2–3 line *Summary*  
• Then write exactly 4–5 *Bullet Points* using strong verbs  
• Focus on:
  – what the user built  
  – how it works  
  – measurable impact  
  – performance improvement  
  – ML/AI or backend logic where relevant  
• Avoid generic student wording like "I learned", "I did", "I participated".  
• Use developer-style wording suitable for an ATS resume.

---

### OUTPUT FORMAT (VERY IMPORTANT)
Return the output in this exact format:

SUMMARY:
<2–3 line summary>

BULLET POINTS:
- <bullet 1>
- <bullet 2>
- <bullet 3>
- <bullet 4>
- <bullet 5>

TECH STACK:
Tech: <clean tech stack line>

PORTFOLIO VERSION:
<long descriptive version written in smooth English>"""
    
    def _build_project_description(self, 
                                 description: str, 
                                 readme_content: str, 
                                 project_type: str,
                                 stars: int) -> str:
        """Build comprehensive project description from available data"""
        
        # Start with repository description
        desc_parts = []
        
        if description:
            desc_parts.append(description)
        
        # Add project type context
        desc_parts.append(f"This is a {project_type.lower()} project")
        
        # Add social proof if significant
        if stars > 10:
            desc_parts.append(f"with {stars} GitHub stars")
        
        # Extract key features from README
        if readme_content:
            features = self._extract_features_from_readme(readme_content)
            if features:
                desc_parts.append(f"Key features include: {', '.join(features)}")
        
        return '. '.join(desc_parts) + '.'
    
    def _extract_features_from_readme(self, readme_content: str) -> List[str]:
        """Extract key features from README content"""
        import re
        
        features = []
        lines = readme_content.split('\n')
        
        # Look for feature lists (lines starting with -, *, or numbers)
        feature_patterns = [
            r'^[\s]*[-*]\s+(.+)',  # Bullet points
            r'^[\s]*\d+\.\s+(.+)',  # Numbered lists
            r'^\s*[✓✅]\s+(.+)',    # Checkmarks
        ]
        
        for line in lines:
            for pattern in feature_patterns:
                match = re.match(pattern, line)
                if match:
                    feature = match.group(1).strip()
                    # Clean up and validate feature
                    if len(feature) > 10 and len(feature) < 100:
                        features.append(feature)
                    
                    if len(features) >= 5:  # Limit features
                        break
            
            if len(features) >= 5:
                break
        
        return features
    
    def _format_github_metadata(self, repo_data: Dict[str, Any]) -> str:
        """Format GitHub metadata for additional context"""
        metadata_parts = []
        
        # Add repository statistics
        stats = []
        if repo_data.get('stars', 0) > 0:
            stats.append(f"{repo_data['stars']} stars")
        if repo_data.get('forks', 0) > 0:
            stats.append(f"{repo_data['forks']} forks")
        
        if stats:
            metadata_parts.append(f"Repository metrics: {', '.join(stats)}")
        
        # Add language breakdown
        languages = repo_data.get('languages', {})
        if languages:
            # Calculate percentages
            total_bytes = sum(languages.values())
            lang_percentages = {
                lang: round((bytes_count / total_bytes) * 100, 1) 
                for lang, bytes_count in languages.items()
            }
            
            # Format top 3 languages
            top_langs = sorted(lang_percentages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_breakdown = ', '.join([f"{lang} ({pct}%)" for lang, pct in top_langs])
            metadata_parts.append(f"Language breakdown: {lang_breakdown}")
        
        # Add topics if available
        topics = repo_data.get('topics', [])
        if topics:
            metadata_parts.append(f"Topics: {', '.join(topics[:5])}")
        
        if metadata_parts:
            return "### ADDITIONAL GITHUB CONTEXT\n" + '\n'.join(metadata_parts)
        
        return ""
    
    def get_enhancement_suggestions(self, content: str, target_role: str) -> List[str]:
        """Generate suggestions for improving resume content"""
        suggestions = []
        
        # Role-specific suggestions
        role_keywords = {
            'Machine Learning Engineer': ['model', 'accuracy', 'performance', 'dataset', 'algorithm'],
            'Backend Developer': ['API', 'database', 'scalability', 'performance', 'architecture'],
            'Frontend Developer': ['user interface', 'responsive', 'user experience', 'optimization'],
            'Full Stack Developer': ['end-to-end', 'full-stack', 'integration', 'deployment'],
            'Data Scientist': ['analysis', 'insights', 'visualization', 'statistical', 'data']
        }
        
        if target_role in role_keywords:
            missing_keywords = []
            content_lower = content.lower()
            
            for keyword in role_keywords[target_role]:
                if keyword not in content_lower:
                    missing_keywords.append(keyword)
            
            if missing_keywords:
                suggestions.append(f"Consider adding {target_role.lower()}-specific keywords: {', '.join(missing_keywords)}")
        
        # General suggestions
        if 'metric' not in content.lower() and 'performance' not in content.lower():
            suggestions.append("Add quantifiable metrics or performance improvements")
        
        if len(content.split()) < 50:
            suggestions.append("Consider adding more technical details about implementation")
        
        return suggestions