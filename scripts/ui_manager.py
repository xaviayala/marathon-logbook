import shutil
import os
from datetime import datetime

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
HISTORY_DIR = os.path.join(DOCS_DIR, 'history')
LOGS_ROOT = os.path.join(DOCS_DIR, 'logs')

def update_sidebar():
   # Sync Root README to a cleaner named file in /docs
    root_readme = os.path.join(PROJECT_ROOT, 'README.md')
    docs_home = os.path.join(DOCS_DIR, '_home.md') # Change name here
    shutil.copy2(root_readme, docs_home)
    print("🏠 Syncing Root README to /docs/_home.md")
    
    sidebar_path = os.path.join(DOCS_DIR, '_sidebar.md')
    
    # 1. STATIC CORE SECTIONS
    sidebar_content = [
        "* [🏠 Project Home](/)",
        "* [📊 Performance Dashboard](dashboard.md)",
        "* [🧠 Latest AI Audit](audit.md)",
        "* [🦴 Pain Scale Protocol](pain-scale.md)",
        "",
        "* **Training Strategy**",
        "  * [Pain-Free Methodology](methodology.md)",
        "  * [Soleus & Core Routine](recovery.md)",
        ""
    ]

    # 2. DYNAMIC: PERFORMANCE AUDIT HISTORY
    # Using a nested list structure for collapsing
    sidebar_content.append("* **Performance Audit History**")
    if os.path.exists(HISTORY_DIR):
        files = sorted([f for f in os.listdir(HISTORY_DIR) if f.endswith('.md')], reverse=True)
        for f in files:
            date_label = f.replace('audit-', '').replace('.md', '')
            sidebar_content.append(f"  * [{date_label}](history/{f})")
    else:
        sidebar_content.append("  * *No audits recorded*")

    # 3. DYNAMIC: LOGBOOKS (Simplified & Detailed)
    for log_type in ['simplified', 'detailed']:
        title = log_type.capitalize()
        target_dir = os.path.join(LOGS_ROOT, log_type)
        
        # --- ADD DEBUG LINES HERE ---
        print(f"🔍 DEBUG: Checking {target_dir}")
        print(f"   -> Exists: {os.path.exists(target_dir)}")
        if os.path.exists(target_dir):
            print(f"   -> Files found: {os.listdir(target_dir)}")
        # ----------------------------

        # Determine file count for the label
        count = 0
        if os.path.exists(target_dir):
            files = sorted([f for f in os.listdir(target_dir) if f.endswith('.md')], reverse=True)
            count = len(files)
        
        # Header for the collapsible section
        sidebar_content.append(f"\n* **{title} Logbook ({count})**")
        
        if count > 0:
            for f in files:
                label = f.replace('.md', '').replace('-run', '')
                # Ensure exactly TWO spaces for the nested list
                sidebar_content.append(f"  * [{label}](logs/{log_type}/{f})")
        else:
            sidebar_content.append("  * *No logs found*")

    # 4. ATOMIC WRITE
    with open(sidebar_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sidebar_content))
    
    print(f"✅ Sidebar successfully rebuilt at {datetime_now()}")

def datetime_now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    update_sidebar()