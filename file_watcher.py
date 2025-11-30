import sys
import time
import subprocess
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AdkRestartHandler(FileSystemEventHandler):
    """Handler for file system events that restarts adk web"""
    
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.last_restart = 0
        self.debounce_seconds = 2  # Wait 2 seconds before restarting to avoid multiple rapid restarts
        
    def on_modified(self, event):
        # Only respond to file modification events (actual writes)
        if event.is_directory:
            return
            
        # Debounce: don't restart if we just restarted recently
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_seconds:
            return
            
        print(f"\n[CHANGE DETECTED] File modified: {event.src_path}")
        self.last_restart = current_time
        self.restart_callback()
    
    def on_created(self, event):
        # Respond to new file creation
        if event.is_directory:
            return
            
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_seconds:
            return
            
        print(f"\n[CHANGE DETECTED] File created: {event.src_path}")
        self.last_restart = current_time
        self.restart_callback()
    
    def on_deleted(self, event):
        # Respond to file deletion
        if event.is_directory:
            return
            
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_seconds:
            return
            
        print(f"\n[CHANGE DETECTED] File deleted: {event.src_path}")
        self.last_restart = current_time
        self.restart_callback()

class AdkWebWatcher:
    """Watches a directory and manages adk web process"""
    
    def __init__(self, watch_path):
        self.watch_path = Path(watch_path).resolve()
        self.process = None
        self.observer = None
        
        if not self.watch_path.exists():
            raise ValueError(f"Path does not exist: {self.watch_path}")
        if not self.watch_path.is_dir():
            raise ValueError(f"Path is not a directory: {self.watch_path}")
    
    def start_adk_web(self):
        """Start the adk web process"""
        if self.process:
            self.stop_adk_web()
        
        print(f"\n{'='*60}")
        print("[STARTING] adk web...")
        print(f"{'='*60}")
        
        try:
            self.process = subprocess.Popen(
                ["adk", "web"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            print(f"[SUCCESS] adk web started (PID: {self.process.pid})")
        except FileNotFoundError:
            print("[ERROR] 'adk' command not found. Make sure it's installed and in PATH.")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to start adk web: {e}")
            sys.exit(1)
    
    def stop_adk_web(self):
        """Stop the adk web process"""
        if self.process:
            print(f"\n[STOPPING] adk web (PID: {self.process.pid})...")
            
            try:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("[WARNING] Process didn't terminate, forcing kill...")
                    self.process.kill()
                    self.process.wait()
                
                print("[SUCCESS] adk web stopped")
            except Exception as e:
                print(f"[ERROR] Failed to stop process: {e}")
            
            self.process = None
    
    def restart_adk_web(self):
        """Restart the adk web process"""
        self.stop_adk_web()
        time.sleep(1)  # Brief pause between stop and start
        self.start_adk_web()
    
    def start_watching(self):
        """Start watching the directory for changes"""
        print(f"\n{'='*60}")
        print(f"[WATCHING] {self.watch_path}")
        print(f"[INFO] Monitoring all files in root and subdirectories")
        print(f"[INFO] Press Ctrl+C to stop")
        print(f"{'='*60}")
        
        # Start initial adk web process
        self.start_adk_web()
        
        # Set up file system observer
        event_handler = AdkRestartHandler(self.restart_adk_web)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.watch_path), recursive=True)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n[INTERRUPT] Shutting down...")
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.stop_adk_web()
        print("[EXIT] File watcher stopped")

def main():
    print("="*60)
    print("ADK Web File Watcher")
    print("="*60)
    
    if len(sys.argv) > 1:
        watch_path = sys.argv[1]
    else:
        watch_path = input("Enter the path to watch: ").strip()
    
    try:
        watcher = AdkWebWatcher(watch_path)
        watcher.start_watching()
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
