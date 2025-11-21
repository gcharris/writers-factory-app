import os
import sys
import shutil
import logging
from typing import Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Mock LLM Analysis ---
def _mock_llm_voice_analysis(voice_sample: str) -> Dict[str, str]:
    """
    Mocks an LLM call to analyze a voice sample.
    """
    logging.info("Performing mock LLM analysis on voice sample...")
    if "gritty" in voice_sample and "noir" in voice_sample:
        return {
            "character_name": "Jake 'The Shadow' Riley",
            "dominant_traits": "Cynical and world-weary, with a strong sense of justice.",
            "key_adjectives": "Gritty, clipped, observant.",
            "emotional_baseline": "Distrustful but professional.",
            "pacing_and_rhythm": "Short, declarative sentences. A steady, deliberate pace.",
            "vocabulary_level": "Prefers simple, direct language over jargon.",
            "common_phrases": "'Just the facts.'",
            "metaphor_domains": "Gambling, shadows, urban decay",
            "sensory_focus": "Notices small, out-of-place details; the smell of rain on asphalt.",
            "core_philosophy": "Everyone has an angle.",
            "attitude_towards_others": "Assumes the worst but is occasionally surprised by decency.",
            "reference_sample": voice_sample
        }
    return {
        "character_name": "Generic Hero", "dominant_traits": "Brave and determined.", "key_adjectives": "Clear, direct, noble.",
        "emotional_baseline": "Hopeful.", "pacing_and_rhythm": "Standard prose rhythm.", "vocabulary_level": "Average.",
        "common_phrases": "'Let's go!'", "metaphor_domains": "Light vs. dark.", "sensory_focus": "Visual action.",
        "core_philosophy": "Good will triumph over evil.", "attitude_towards_others": "Trusting.", "reference_sample": voice_sample
    }

def generate_project_config(project_name: str, voice_sample: str, user_answers: Dict, base_template_path: str, project_root: str):
    """
    Generates initial project configuration files, personalizing them with student data.
    """
    logging.info(f"--- Starting Project Generation for '{project_name}' ---")
    
    project_path = os.path.join(project_root, project_name)
    config_path = os.path.join(project_path, "config")
    os.makedirs(config_path, exist_ok=True)
    logging.info(f"Created project directory: {config_path}")

    # --- Voice Analysis and Personalization ---
    voice_analysis = _mock_llm_voice_analysis(voice_sample)
    
    # Placeholders for personalizing all config files
    placeholders = {
        "{{protagonist_name}}": user_answers.get("protagonist_name", "Protagonist"),
        "{{voice_name}}": voice_analysis.get("character_name", "Character"),
        "{{domains}}": voice_analysis.get("metaphor_domains", "general"),
        "{{primary_domain}}": voice_analysis.get("metaphor_domains", "general").split(',')[0].strip()
    }
    
    # --- Generate Personalized voice.md ---
    voice_template_path = os.path.join(base_template_path, "reference_voice.md")
    with open(voice_template_path, 'r') as f:
        voice_template = f.read()
    
    filled_voice_md = voice_template
    for key, value in voice_analysis.items():
        filled_voice_md = filled_voice_md.replace(f"{{{{{key}}}}}", value)
    
    new_voice_path = os.path.join(config_path, "voice.md")
    with open(new_voice_path, 'w') as f:
        f.write(filled_voice_md)
    logging.info(f"Generated and saved personalized voice profile to {new_voice_path}")

    # --- Generate Personalized YAML configs ---
    for filename in ["reference_multiplier.yaml", "reference_critic.yaml"]:
        source_path = os.path.join(base_template_path, filename)
        dest_path = os.path.join(config_path, filename.replace("reference_", "")) # e.g., critic.yaml
        
        with open(source_path, 'r') as f:
            template_content = f.read()
        
        personalized_content = template_content
        for key, value in placeholders.items():
            personalized_content = personalized_content.replace(key, value)
            
        with open(dest_path, 'w') as f:
            f.write(personalized_content)
        logging.info(f"Generated personalized '{os.path.basename(dest_path)}' from {filename}")
    
    logging.info(f"--- Project '{project_name}' generated successfully! ---")


if __name__ == "__main__":
    logging.info("--- Running Setup Wizard Verification (Refactored) ---")

    TEST_PROJECT_NAME = "student_project"
    TEST_PROJECT_ROOT = "workspace"
    
    if os.path.exists(os.path.join(TEST_PROJECT_ROOT, TEST_PROJECT_NAME)):
        shutil.rmtree(os.path.join(TEST_PROJECT_ROOT, TEST_PROJECT_NAME))
        logging.info("Cleaned up old test project directory.")

    mock_voice_sample = "The city was a gritty mess, a real noir landscape. I knew the facts were out there, but the shadows held them tight."
    mock_user_answers = {
        "genre": "detective_noir",
        "protagonist_name": "Alice"
    }
    
    template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'templates', 'reference_skills')

    generate_project_config(
        project_name=TEST_PROJECT_NAME,
        voice_sample=mock_voice_sample,
        user_answers=mock_user_answers,
        base_template_path=template_path,
        project_root=TEST_PROJECT_ROOT
    )

    logging.info("\n--- Verifying generated and personalized files ---")
    final_config_path = os.path.join(TEST_PROJECT_ROOT, TEST_PROJECT_NAME, "config")
    
    # --- Verification ---
    all_checks_passed = True
    try:
        # Check 1: Files exist
        expected_files = ["voice.md", "multiplier.yaml", "critic.yaml"]
        for f in expected_files:
            if not os.path.exists(os.path.join(final_config_path, f)):
                logging.error(f"VERIFICATION FAILED: File '{f}' not found.")
                all_checks_passed = False
        
        if not all_checks_passed: raise AssertionError("File creation check failed.")
        logging.info("All 3 config files were created successfully.")

        # Check 2: Critic YAML is personalized
        with open(os.path.join(final_config_path, "critic.yaml"), 'r') as f:
            critic_content = f.read()
        if "Does it sound like Alice observing" not in critic_content:
            logging.error("VERIFICATION FAILED: critic.yaml was not personalized with protagonist name.")
            all_checks_passed = False
        if "Are metaphors rooted in Alice's specific domains (Gambling, shadows, urban decay)?" not in critic_content:
            logging.error("VERIFICATION FAILED: critic.yaml was not personalized with metaphor domains.")
            all_checks_passed = False
        
        # Check 3: Multiplier YAML is personalized
        with open(os.path.join(final_config_path, "multiplier.yaml"), 'r') as f:
            multiplier_content = f.read()
        if "reflect Alice's internal state" not in multiplier_content:
            logging.error("VERIFICATION FAILED: multiplier.yaml was not personalized.")
            all_checks_passed = False

        if all_checks_passed:
            logging.info("YAML files were successfully personalized.")
            logging.info("--- VERIFICATION PASSED ---")
        else:
            raise AssertionError("Content personalization check failed.")

    except Exception as e:
        logging.error(f"--- VERIFICATION FAILED --- \nAn error occurred: {e}")