import tkinter as tk
from tkinter import filedialog, messagebox
import os
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

class CoverUpdater:
    def __init__(self, root):
        self.root = root
        self.root.title("MP3 & FLAC Cover Updater")
        self.root.geometry("500x350")
        
        # Variables to store file paths
        self.cover_path = tk.StringVar()
        self.folder_path = tk.StringVar()
        self.file_format = tk.StringVar(value="both")  # "mp3", "flac", "both"
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="MP3 & FLAC Cover Updater", font=("Arial", 16, "bold"))
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
        
        tk.Label(folder_frame, text="Audio Folder:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=40).pack(side=tk.LEFT, padx=5)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)
        
        # Format selection
        format_frame = tk.Frame(self.root)
        format_frame.pack(pady=10)
        
        tk.Label(format_frame, text="Audio Format:").pack(side=tk.LEFT)
        format_options = [("MP3 Only", "mp3"), ("FLAC Only", "flac"), ("Both", "both")]
        for text, value in format_options:
            tk.Radiobutton(format_frame, text=text, variable=self.file_format, value=value).pack(side=tk.LEFT, padx=5)
        
        # Update button
        update_button = tk.Button(self.root, text="Update Audio Covers", command=self.update_covers, 
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
        folder_path = filedialog.askdirectory(title="Select Audio Folder")
        if folder_path:
            self.folder_path.set(folder_path)
            
    def update_covers(self):
        cover_path = self.cover_path.get()
        folder_path = self.folder_path.get()
        format_type = self.file_format.get()
        
        # Validate inputs
        if not cover_path:
            messagebox.showerror("Error", "Please select a cover image")
            return
            
        if not folder_path:
            messagebox.showerror("Error", "Please select an audio folder")
            return
            
        if not os.path.exists(cover_path):
            messagebox.showerror("Error", "Cover image does not exist")
            return
            
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Audio folder does not exist")
            return
            
        # Determine which files to process
        supported_extensions = {
            "mp3": [".mp3"],
            "flac": [".flac"],
            "both": [".mp3", ".flac"]
        }
        
        extensions = supported_extensions[format_type]
        
        # Get all audio files in the folder with selected extensions
        audio_files = []
        for filename in os.listdir(folder_path):
            if any(filename.lower().endswith(ext) for ext in extensions) and os.path.isfile(os.path.join(folder_path, filename)):
                audio_files.append(filename)
        
        if not audio_files:
            messagebox.showwarning("Warning", f"No {format_type.upper()} files found in the selected folder")
            return
            
        # Process each audio file
        success_count = 0
        for filename in audio_files:
            try:
                file_path = os.path.join(folder_path, filename)
                
                # Determine file type and process accordingly
                if filename.lower().endswith('.mp3'):
                    self.process_mp3(file_path, cover_path)
                elif filename.lower().endswith('.flac'):
                    self.process_flac(file_path, cover_path)
                
                success_count += 1
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
        self.status_label.config(text=f"Updated {success_count} of {len(audio_files)} files", fg="green")
        messagebox.showinfo("Success", f"Successfully updated {success_count} audio files")

    def process_mp3(self, file_path, cover_path):
        """Process MP3 files with ID3 tags"""
        # Load ID3 tags
        audio = MP3(file_path, ID3=ID3)
        
        # Add cover image
        audio.tags.delall('APIC')  # Remove existing cover if any
        audio.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime=self.get_image_mime_type(cover_path),
                type=3,  # Cover (front)
                desc='Cover',
                data=open(cover_path, 'rb').read()
            )
        )
        
        # Save changes
        audio.save()

    def process_flac(self, file_path, cover_path):
        """Process FLAC files with Vorbis comments"""
        # Load FLAC tags
        audio = FLAC(file_path)
        
        # Create picture object for FLAC
        from mutagen.flac import Picture
        import base64
        
        # Read image data
        with open(cover_path, 'rb') as img_file:
            img_data = img_file.read()
            
        # Create picture object
        picture = Picture()
        picture.type = 3  # Cover (front)
        picture.mime = self.get_image_mime_type(cover_path)
        picture.desc = 'Cover'
        picture.data = img_data
        
        # Add to FLAC tags
        audio.clear_pictures()
        audio.add_picture(picture)
        
        # Save changes
        audio.save()

    def get_image_mime_type(self, cover_path):
        """Determine MIME type based on file extension"""
        ext = os.path.splitext(cover_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif ext in ['.png']:
            return 'image/png'
        elif ext in ['.bmp']:
            return 'image/bmp'
        else:
            return 'image/jpeg'  # Default to JPEG

if __name__ == "__main__":
    root = tk.Tk()
    app = CoverUpdater(root)
    root.mainloop()
