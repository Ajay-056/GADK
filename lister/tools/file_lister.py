from datetime import datetime
import os

def list_files_tool(keyword: str, threshold: int = 10, limit: int = 5):
    """
    Lists files in a directory. If the total count exceeds 'threshold', 
    it only returns the top 'limit' files sorted by modification time.
    """

    directory_map = {
        "test": "/home/butcher/test",
        "nalalogs": "/var/log/nala",
    }
    
    path = directory_map.get(keyword.lower())
    if not path or not os.path.exists(path):
        return f"Sorry, I couldn't find a directory for '{keyword}'."

    # 1. Get all files with their modification times
    all_files = []
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            mod_time = os.path.getmtime(full_path)
            all_files.append({
                "name": filename,
                "time": mod_time
            })

    if not all_files:
        return f"The directory '{keyword}' is empty."

    # 2. Sort by modified time (Newest first)
    all_files.sort(key=lambda x: x['time'], reverse=True)

    # 3. Apply the logic: If > 10 files, only show top 5
    total_count = len(all_files)
    display_files = all_files
    note = ""

    if total_count >= threshold:
        display_files = all_files[:limit]
        note = f"(Showing top {limit} newest files out of {total_count} total)\n"

    # 4. Format the output
    output = f"Files present in {keyword} are,\n{note}\n"
    for idx, file_info in enumerate(display_files, 1):
        readable_time = datetime.fromtimestamp(file_info['time']).strftime('%Y-%m-%d %H:%M:%S')
        output += f"{idx}. {file_info['name']} (Modified: {readable_time})\n"

    output += f"\nLet me know which file you want by mentioning the serial number 1 to {len(display_files)}."
    return output
