import os

# Resolve paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
HISTORY_DIR = os.path.join(DOCS_DIR, 'history')
LOGS_ROOT = os.path.join(DOCS_DIR, 'logs')

def update_sidebar():
    sidebar_path = os.path.join(DOCS_DIR, '_sidebar.md')
    
    # 1. STATIC CORE SECTIONS
    sidebar_content = [
        "* [🏠 Project Home](README.md)",
        "* [📊 Performance Dashboard](dashboard.md)",
        "* [🧠 Latest AI Audit](audit.md)",
        "* [🦴 Pain Scale Protocol](pain-scale.md)",
        "",
        "* **Training Strategy**",
        "  * [Pain-Free Methodology](METHODOLOGY.md)",
        "  * [Soleus & Core Routine](RECOVERY.md)",
        ""
    ]

    # 2. DYNAMIC: PERFORMANCE AUDIT HISTORY
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
        sidebar_content.append(f"\n* **{title} Logbook**")
        target_dir = os.path.join(LOGS_ROOT, log_type)
        
        if os.path.exists(target_dir):
            files = sorted([f for f in os.listdir(target_dir) if f.endswith('.md')], reverse=True)
            if files:
                for f in files:
                    label = f.replace('.md', '')
                    # Pathing: Docsify is in /docs, so it needs to go down to /logs
                    sidebar_content.append(f"  * [{label}](logs/{log_type}/{f})")
            else:
                sidebar_content.append("  * *No logs found*")
        else:
            sidebar_content.append(f"  * [Archive](logs/{log_type}/)")

    # 4. ATOMIC WRITE
    with open(sidebar_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sidebar_content))
    
    print(f"✅ Sidebar successfully rebuilt at {datetime_now()}")

def datetime_now():
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    update_sidebar()