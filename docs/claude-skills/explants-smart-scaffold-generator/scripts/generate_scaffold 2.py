#!/usr/bin/env python3
"""
Smart Scaffold Generator - Automated Query Script

This script automates the process of generating Gold Standard scaffolds
by formatting queries and calling NotebookLM.

Usage:
    python generate_scaffold.py --chapter "Chapter 4: Vance's Approach" 
                                --act "Act IV: The New Bondage"
                                --setting "Pasadena dojo, evening - Mickey POV"
                                --beats "Vance arrives, acknowledges pioneers, pilot territories"
                                --wordcount "5,000-6,000"

Or with a minimal outline file:
    python generate_scaffold.py --outline /path/to/minimal_outline.md
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def load_ace_template():
    """Load the ACE template for query formatting."""
    template_path = Path(__file__).parent.parent / "references" / "ace-template.md"
    
    # Simple condensed template for automation
    return """Generate Gold Standard Scaffold for {chapter} using ACE template.
{act}. Setting: {setting}.
Beats: {beats}. Word count: {wordcount}.
Follow complete ACE structure with all sections."""

def format_query(chapter, act, setting, beats, wordcount):
    """Format the query with provided variables."""
    template = load_ace_template()
    return template.format(
        chapter=chapter,
        act=act,
        setting=setting,
        beats=beats,
        wordcount=wordcount
    )

def check_notebooklm_auth():
    """Verify NotebookLM authentication status."""
    try:
        result = subprocess.run([
            "python", "scripts/run.py", "auth_manager.py", "status"
        ], cwd=os.path.expanduser("~/.claude/skills/notebooklm"), 
           capture_output=True, text=True)
        
        if result.returncode != 0:
            print("❌ NotebookLM authentication failed")
            print("Run: cd ~/.claude/skills/notebooklm && python scripts/run.py auth_manager.py login")
            return False
        
        print("✅ NotebookLM authentication verified")
        return True
    except Exception as e:
        print(f"❌ Error checking NotebookLM auth: {e}")
        return False

def query_notebooklm(query):
    """Send query to NotebookLM and return response."""
    try:
        print("🔄 Querying NotebookLM...")
        print(f"Query: {query[:100]}...")
        
        result = subprocess.run([
            "python", "scripts/run.py", "ask_question.py", 
            "--question", query
        ], cwd=os.path.expanduser("~/.claude/skills/notebooklm"),
           capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ NotebookLM query failed: {result.stderr}")
            return None
        
        print("✅ NotebookLM query completed")
        return result.stdout
    
    except Exception as e:
        print(f"❌ Error querying NotebookLM: {e}")
        return None

def save_scaffold(response, output_path):
    """Save the scaffold response to file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response)
        print(f"✅ Scaffold saved to: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving scaffold: {e}")
        return False

def parse_outline_file(outline_path):
    """Parse a minimal outline file to extract variables."""
    # This is a simple implementation - could be enhanced
    # to parse structured outline files more intelligently
    
    try:
        with open(outline_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic info (simplified parsing)
        lines = content.split('\n')
        chapter = None
        act = None
        setting = None
        beats = []
        wordcount = "5,000-6,000"  # default
        
        for line in lines:
            line = line.strip()
            if line.startswith('# ') and 'Chapter' in line:
                chapter = line[2:]
            elif 'Act' in line and ':' in line:
                act = line
            elif 'Setting:' in line:
                setting = line.replace('Setting:', '').strip()
            elif 'POV:' in line:
                if setting:
                    setting += f" - {line.replace('POV:', '').strip()} POV"
            elif line.startswith('- ') and any(word in line.lower() for word in ['beat', 'key', 'element']):
                beats.append(line[2:])
            elif 'word count' in line.lower() or 'words' in line.lower():
                # Extract word count if present
                words = [w for w in line.split() if any(c.isdigit() for c in w)]
                if words:
                    wordcount = ', '.join(words)
        
        return {
            'chapter': chapter,
            'act': act, 
            'setting': setting,
            'beats': '; '.join(beats) if beats else '',
            'wordcount': wordcount
        }
    
    except Exception as e:
        print(f"❌ Error parsing outline file: {e}")
        return None

def generate_output_filename(chapter):
    """Generate appropriate output filename from chapter title."""
    # Convert "Chapter 4: Vance's Approach" to "CHAPTER_4_VANCES_APPROACH_SCAFFOLD.md"
    if ':' in chapter:
        parts = chapter.split(':')
        number_part = parts[0].strip().replace('Chapter ', '').replace('chapter ', '')
        title_part = parts[1].strip()
    else:
        number_part = chapter.replace('Chapter ', '').replace('chapter ', '')
        title_part = ''
    
    title_clean = title_part.replace(' ', '_').replace("'", '').upper()
    return f"CHAPTER_{number_part}_{title_clean}_SCAFFOLD.md"

def main():
    parser = argparse.ArgumentParser(description='Generate Gold Standard scaffolds using NotebookLM')
    
    # Option 1: Individual parameters
    parser.add_argument('--chapter', help='Chapter number and title')
    parser.add_argument('--act', help='Act number and title')
    parser.add_argument('--setting', help='Setting and POV')
    parser.add_argument('--beats', help='Comma-separated list of key beats')
    parser.add_argument('--wordcount', help='Target word count', default='5,000-6,000')
    
    # Option 2: Outline file
    parser.add_argument('--outline', help='Path to minimal outline file')
    
    # Output options
    parser.add_argument('--output', help='Output file path (auto-generated if not specified)')
    parser.add_argument('--directory', help='Output directory', default='.')
    
    args = parser.parse_args()
    
    # Determine input method
    if args.outline:
        print(f"📖 Parsing outline file: {args.outline}")
        outline_data = parse_outline_file(args.outline)
        if not outline_data:
            sys.exit(1)
        
        chapter = outline_data['chapter']
        act = outline_data['act']
        setting = outline_data['setting']
        beats = outline_data['beats']
        wordcount = outline_data['wordcount']
    
    elif all([args.chapter, args.act, args.setting, args.beats]):
        chapter = args.chapter
        act = args.act
        setting = args.setting
        beats = args.beats
        wordcount = args.wordcount
    
    else:
        print("❌ Must provide either --outline file or all individual parameters")
        print("Use --help for usage information")
        sys.exit(1)
    
    # Validate inputs
    if not all([chapter, act, setting, beats]):
        print("❌ Missing required information")
        print(f"Chapter: {chapter}")
        print(f"Act: {act}")
        print(f"Setting: {setting}")
        print(f"Beats: {beats}")
        sys.exit(1)
    
    # Check NotebookLM authentication
    if not check_notebooklm_auth():
        sys.exit(1)
    
    # Format query
    query = format_query(chapter, act, setting, beats, wordcount)
    print(f"\n📝 Generated Query:\n{query}\n")
    
    # Query NotebookLM
    response = query_notebooklm(query)
    if not response:
        sys.exit(1)
    
    # Generate output filename
    if args.output:
        output_path = args.output
    else:
        filename = generate_output_filename(chapter)
        output_path = os.path.join(args.directory, filename)
    
    # Save scaffold
    if save_scaffold(response, output_path):
        print(f"\n🎉 Scaffold generation completed!")
        print(f"📄 File: {output_path}")
        print(f"📊 Ready for scene-writer skill")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
