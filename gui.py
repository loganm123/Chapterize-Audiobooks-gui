import tkinter as tk
from tkinter import filedialog, Listbox, Button, Text, Scrollbar, messagebox
import os
import subprocess
import threading
import tkinter.messagebox as msgbox  # Import messagebox at the beginning of your script


folders_to_process = []  # List to store folder paths
processed_folders = []  # List to store processed folder paths
processing_count = 0  # Counter for the number of folders being processed
total_folders = 0  # Total number of folders to be processed

def update_animation_label():
    global animation_index
    animation_text = ["Chapterizing.", "Chapterizing..", "Chapterizing..."]
    if chapterizing_dialog_label:
        chapterizing_dialog_label.config(text=animation_text[animation_index % len(animation_text)])
        animation_index += 1
    chapterizing_dialog.after(500, update_animation_label)  # Update every 500ms

def show_chapterizing_dialog():
    global chapterizing_dialog, chapterizing_dialog_label, animation_index
    animation_index = 0
    chapterizing_dialog = tk.Toplevel(root)
    chapterizing_dialog.title("Chapterizing")
    chapterizing_dialog.geometry("300x100")
    chapterizing_dialog_label = tk.Label(chapterizing_dialog, text="Chapterizing.")
    chapterizing_dialog_label.pack(expand=True, fill='both', padx=10, pady=10)
    chapterizing_dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
    chapterizing_dialog.transient(root)
    chapterizing_dialog.grab_set()  # Modal window
    update_animation_label()  # Start the animation

def close_chapterizing_dialog():
    global chapterizing_dialog
    if chapterizing_dialog:
        chapterizing_dialog.destroy()
        chapterizing_dialog = None

def test_dialog():
    show_chapterizing_dialog()
    # For testing, automatically close the dialog after a few seconds
    root.after(5000, close_chapterizing_dialog)  # Adjust the time as needed

# ... (rest of your existing code to set up the Tkinter window)




def check_ffmpeg_installed():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return "FFmpeg is installed. Good to go!"
    except subprocess.CalledProcessError:
        return "FFmpeg is installed, but there was an error."
    except FileNotFoundError:
        return "FFmpeg is not installed. Please install FFmpeg to use this program."

def add_files():
    folder = filedialog.askdirectory()
    if folder:
        folders_to_process.append(folder)
        folder_title = os.path.basename(folder)  # Extract the final title from the file path
        file_listbox.insert(tk.END, folder_title)
        update_total_folders()

def remove_selected_folder():
    selected_index = file_listbox.curselection()
    if selected_index:
        selected_index = int(selected_index[0])
        folder_title = file_listbox.get(selected_index)
        folder = os.path.join(os.getcwd(), folder_title)  # Reconstruct the folder path from the title
        folders_to_process.remove(folder)
        file_listbox.delete(selected_index)
        update_total_folders()

def update_total_folders():
    global total_folders
    total_folders = len(folders_to_process)

def concatenate_mp3_files(directory, text_output):
    global processing_count
    if not os.path.isdir(directory):
        text_output.insert(tk.END, "Directory does not exist. Please enter a valid path.\n")
        return
    
    output_file = os.path.join(directory, 'combined.mp3')
    if os.path.exists(output_file):
        # Move the folder to processed_folders list if it already has a "combined.mp3" file
        processed_folders.append(directory)
        processed_listbox.insert(tk.END, os.path.basename(directory))  # Display the folder title
        # Remove the folder from the list of folders to be processed
        folders_to_process.remove(directory)
        file_listbox.delete(0, tk.END)
        for item in folders_to_process:
            folder_title = os.path.basename(item)
            file_listbox.insert(tk.END, folder_title + "\n")

        text_output.insert(tk.END, f"The folder '{os.path.basename(directory)}' was already processed.\n")
        return

    mp3_files = [f for f in os.listdir(directory) if f.endswith('.mp3')]
    mp3_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f)) or -1))

    if not mp3_files:
        text_output.insert(tk.END, "No MP3 files found in the directory.\n")
        return

    filelist_path = os.path.join(directory, 'filelist.txt')
    with open(filelist_path, 'w') as filelist:
        for filename in mp3_files:
            filelist.write(f"file '{os.path.join(directory, filename)}'\n")

    text_output.insert(tk.END, "Filelist.txt created with the following MP3 files:\n")
    text_output.insert(tk.END, "\n".join(mp3_files) + "\n")

    output_file = os.path.join(directory, 'combined.mp3')
    command = f"ffmpeg -f concat -safe 0 -i \"{filelist_path}\" -c copy \"{output_file}\""
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            text=True
        )
        
        for line in process.stdout:
            text_output.insert(tk.END, line)
            text_output.see(tk.END)
        
        process.wait()
        
        text_output.insert(tk.END, f"Successfully created the combined file: {output_file}\n")
        
        # Delete individual MP3 files
        for mp3_file in mp3_files:
            mp3_path = os.path.join(directory, mp3_file)
            os.remove(mp3_path)
        
        text_output.insert(tk.END, "Deleted individual MP3 files after concatenation.\n")
        
        processed_folders.append(directory)  # Add the processed folder to the list
        processed_listbox.insert(tk.END, os.path.basename(directory))  # Display the folder title
        # Remove the folder from the list of folders to be processed
        folders_to_process.remove(directory)
        file_listbox.delete(0, tk.END)
        for item in folders_to_process:
            folder_title = os.path.basename(item)
            file_listbox.insert(tk.END, folder_title + "\n")
        processing_count += 1
        if processing_count == total_folders:
            messagebox.showinfo("Processing Complete", "All folders have been processed.")
    except Exception as e:
        text_output.insert(tk.END, f"An error occurred while running FFmpeg: {e}\n")

import subprocess
def run_chapterize_script(folder):
    chapterize_script = "chapterize_ab.py"
    folder_path = os.path.abspath(folder)
    combined_mp3_path = os.path.join(folder_path, "combined.mp3")

    # Check if the script file exists
    if not os.path.isfile(chapterize_script):
        text_output.insert(tk.END, f"Error: '{chapterize_script}' script not found.\n")
        return

    # Check if the 'combined.mp3' file exists
    if not os.path.isfile(combined_mp3_path):
        text_output.insert(tk.END, f"'combined.mp3' not found in folder: {folder_path}\n")
        return

    # Call the script on 'combined.mp3'
    try:
        subprocess.run(["python", chapterize_script, combined_mp3_path], check=True, text=True)
        text_output.insert(tk.END, f"Chapterized 'combined.mp3' in folder: {folder_path}\n")
    except subprocess.CalledProcessError as e:
        text_output.insert(tk.END, f"Error chapterizing 'combined.mp3' in folder '{folder_path}': {e}\n")
    finally:
        # Close the dialog after processing
        root.after(0, close_chapterizing_dialog)

    # Delete the 'combined.mp3' file
    try:
        os.remove(combined_mp3_path)
        text_output.insert(tk.END, f"Deleted 'combined.mp3' in folder: {folder_path}\n")
    except OSError as e:
        text_output.insert(tk.END, f"Error deleting 'combined.mp3' in folder '{folder_path}': {e}\n")

def chapterize_folders():
    global processing_count
    processing_count = 0

    # Show the dialog before starting the process
    show_chapterizing_dialog()

    for folder in processed_folders.copy():
        # Run chapterizing in a separate thread
        threading.Thread(target=run_chapterize_script, args=(folder,)).start()


def process_folders():
    global processing_count
    processing_count = 0
    for folder in folders_to_process.copy():
        text_output.delete(1.0, tk.END)  # Clear the text output
        threading.Thread(target=concatenate_mp3_files, args=(folder, text_output)).start()

root = tk.Tk()
root.title("Folder Processor")

# Add a new button to test the dialog
#test_dialog_button = tk.Button(root, text="Test Dialog", command=test_dialog)
#test_dialog_button.pack(pady=10)

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

add_button = tk.Button(frame, text="Add Folder", command=add_files)
add_button.pack(side=tk.LEFT, padx=(0, 5))

remove_button = tk.Button(frame, text="Remove Folder", command=remove_selected_folder)
remove_button.pack(side=tk.LEFT)

file_listbox = Listbox(root, width=50)
file_listbox.pack(padx=10, pady=10)

process_button = tk.Button(root, text="Process Folders", command=process_folders)
process_button.pack(pady=(0, 10))  # Centered above the listbox

processed_frame = tk.Frame(root)
processed_frame.pack(padx=10, pady=10)
processed_label = tk.Label(processed_frame, text="Processed Folders:")
processed_label.pack()
processed_listbox = Listbox(processed_frame, width=50)
processed_listbox.pack()

chapterize_button = tk.Button(root, text="Chapterize Folders", command=chapterize_folders)
chapterize_button.pack()

text_output_frame = tk.Frame(root)
text_output_frame.pack(padx=10, pady=10)

text_output = Text(text_output_frame, wrap=tk.WORD, width=80, height=20)
text_output.pack()

scrollbar = Scrollbar(text_output_frame, command=text_output.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
text_output.config(yscrollcommand=scrollbar.set)

root.mainloop()
