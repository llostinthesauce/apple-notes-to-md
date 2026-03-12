import os
import subprocess
import re
import sys

def clean_filename(name):
    # Remove characters that are unsafe for filenames
    cleaned = re.sub(r'[\/\\\:\*\?\"\<\>\|]', '_', name)
    # Strip leading/trailing spaces
    return cleaned.strip()

def applescript_escape(s: str) -> str:
    """Escape a string for safe interpolation into an AppleScript double-quoted string."""
    return s.replace('\\', '\\\\').replace('"', '\\"')

def run_applescript(script):
    process = subprocess.Popen(['osascript', '-e', script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = process.communicate()
    if process.returncode != 0:
        return None, err
    return out.strip(), None

def get_accounts():
    out, err = run_applescript('tell application "Notes" to get name of every account')
    if not out: return []
    return [acc.strip() for acc in out.split(',') if acc.strip()]

def get_folders(account):
    script = f'tell application "Notes" to get name of every folder of account "{applescript_escape(account)}"'
    out, err = run_applescript(script)
    if not out: return []
    return [f.strip() for f in out.split(',') if f.strip()]

def get_note_count(account, folder):
    script = f'tell application "Notes" to count notes of folder "{applescript_escape(folder)}" of account "{applescript_escape(account)}"'
    out, err = run_applescript(script)
    if not out: return 0
    try:
        return int(out)
    except:
        return 0

def html_to_text(html_content):
    if not html_content:
        return ""
    try:
        process = subprocess.Popen(['textutil', '-convert', 'txt', '-stdin', '-stdout'],
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        out, err = process.communicate(input=html_content.encode('utf-8'))
        if process.returncode == 0:
            return out.decode('utf-8', errors='ignore')
    except Exception:
        pass
    
    # Fallback to simple regex if textutil fails
    text = re.sub(r'<br\s*/?>', '\n', html_content)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'</div>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return text.strip()

def main():
    print("Fetching notes from Apple Notes using Native AppleScript...")
    print("NOTE: You may see a popup asking to allow Terminal (or Python) to access Notes. Please accept it.")
    
    # Try to activate the app to resolve access timing windows
    run_applescript('tell application "Notes" to activate')
    
    accounts = get_accounts()
    if not accounts:
        print("No accounts found or lacking permissions to access Apple Notes.")
        sys.exit(1)
    
    print(f"Found {len(accounts)} accounts: {', '.join(accounts)}")
    output_dir = "Exported_Notes"
    os.makedirs(output_dir, exist_ok=True)
    
    total_exported = 0
    
    for account in accounts:
        print(f"\nProcessing Account: {account}")
        folders = get_folders(account)
        
        for folder in folders:
            note_count = get_note_count(account, folder)
            if note_count == 0:
                continue
                
            print(f"  Folder: '{folder}' ({note_count} notes)")
            
            safe_account = clean_filename(account)
            safe_folder = clean_filename(folder)
            
            note_dir = os.path.join(output_dir, safe_account, safe_folder)
            os.makedirs(note_dir, exist_ok=True)
            
            # Fetch each note interactively via AppleScript
            for idx in range(1, note_count + 1):
                script = f'''
                try
                    tell application "Notes"
                        set n to note {idx} of folder "{applescript_escape(folder)}" of account "{applescript_escape(account)}"
                        set nName to name of n
                        set nCreation to creation date of n as string
                        set nMod to modification date of n as string
                        set nBody to body of n
                        return nName & "||DATA||" & nCreation & "||DATA||" & nMod & "||DATA||" & nBody
                    end tell
                on error errMsg
                    return "ERROR||DATA||" & errMsg
                end try
                '''
                
                out, err = run_applescript(script)
                if not out:
                    continue
                    
                parts = out.split('||DATA||', 3)
                
                if parts[0] == "ERROR":
                    print(f"    [!] Skipping note {idx}: {parts[1]}")
                    continue
                
                if len(parts) == 4:
                    title = parts[0]
                    creation = parts[1]
                    mod = parts[2]
                    body_html = parts[3]
                    
                    safe_title = clean_filename(title)
                    if not safe_title:
                        safe_title = "Untitled"
                    
                    if len(safe_title) > 200:
                        safe_title = safe_title[:200]
                        
                    text_content = html_to_text(body_html)
                    
                    metadata_header = f"# {title}\n"
                    metadata_header += f"Created: {creation}\n"
                    metadata_header += f"Modified: {mod}\n"
                    metadata_header += "\n---\n\n"
                    
                    full_content = metadata_header + text_content
                    
                    file_path = os.path.join(note_dir, f"{safe_title}.md")
                    counter = 1
                    while os.path.exists(file_path):
                        file_path = os.path.join(note_dir, f"{safe_title}_{counter}.md")
                        counter += 1
                        
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(full_content)
                        total_exported += 1
                        
                        # Only print progress percentage to avoid stdout bloat
                        if idx % 50 == 0:
                            print(f"    ... {idx}/{note_count} notes exported")
                            
                    except Exception as e:
                        print(f"    [!] Failed to save note '{title}': {e}")
                        
    print(f"\n--- Export Complete ---")
    print(f"Successfully saved {total_exported} notes.")
    print(f"Your files are located in: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    main()
