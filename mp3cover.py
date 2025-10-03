import tkinter as tk
from tkinter import filedialog, messagebox
import os
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

class CoverUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 Cover Updater")
        self.root.geometry("500x300")
        
        # Variables to store file paths
        self.cover_path = tk.StringVar()
        self.folder_path = tk.StringVar()
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="MP3 Cover Updater", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Cover image selection
        cover_frame = tk.Frame(self.root)
        cover_frame.pack(pady=10)
        
        tk.Label(cover_frame, text="Cover Image:").pack(side=tk.LEFT)
        tk.Entry(cover_frame, textvariable=self.cover_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(cover_frame, text="Browse", command=self.browse_cover).pack(side=tk.LEFT)
        
        # Folder selection
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=10)
        
        tk.Label(folder_frame, text="MP3 Folder:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Update button
        update_button = tk.Button(self.root, text="Update MP3 Covers", command=self.update_covers, 
                                bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        update_button.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(self.root, text="", fg="blue")
        self.status_label.pack(pady=5)
        
    def browse_cover(self):
        file_path = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.cover_path.set(file_path)
            
    def browse_folder(self):
        folder_path = filedialog.askdirectory(title="Select MP3 Folder")
        if folder_path:
            self.folder_path.set(folder_path)
            
    def update_covers(self):
        cover_path = self.cover_path.get()
        folder_path = self.folder_path.get()
        
        # Validate inputs
        if not cover_path:
            messagebox.showerror("Error", "Please select a cover image")
            return
            
        if not folder_path:
            messagebox.showerror("Error", "Please select an MP3 folder")
            return
            
        if not os.path.exists(cover_path):
            messagebox.showerror("Error", "Cover image does not exist")
            return
            
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "MP3 folder does not exist")
            return
            
        # Get all MP3 files in the folder
        mp3_files = [f for f in os.listdir(folder_path) 
                    if f.lower().endswith('.mp3') and os.path.isfile(os.path.join(folder_path, f))]
        
        if not mp3_files:
            messagebox.showwarning("Warning", "No MP3 files found in the selected folder")
            return
            
        # Process each MP3 file
        success_count = 0
        for filename in mp3_files:
            try:
                file_path = os.path.join(folder_path, filename)
                
                # Load ID3 tags
                audio = MP3(file_path, ID3=ID3)
                
                # Add cover image
                audio.tags.delall('APIC')  # Remove existing cover if any
                audio.tags.add(
                    APIC(
                        encoding=3,  # UTF-8
                        mime='image/jpeg' if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg') else 'image/png',
                        type=3,  # Cover (front)
                        desc='Cover',
                        data=open(cover_path, 'rb').read()
                    )
                )
                
                # Save changes
                audio.save()
                success_count += 1
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
        self.status_label.config(text=f"Updated {success_count} of {len(mp3_files)} files", fg="green")
        messagebox.showinfo("Success", f"Successfully updated {success_count} MP3 files")

if __name__ == "__main__":
    root = tk.Tk()
    app = CoverUpdater(root)
    root.mainloop()