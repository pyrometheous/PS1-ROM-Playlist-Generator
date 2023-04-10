import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


def browse_directory():
    folder_path = filedialog.askdirectory()
    if folder_path:
        path_label.config(text=folder_path)
        organize_button.config(state=tk.NORMAL)


def organize_files():
    folder_path = path_label["text"]
    organize_button.config(state=tk.DISABLED)

    # Step 1: Select the input directory
    if not folder_path:
        messagebox.showerror("Error", "No directory selected.")
        return

    # Step 2: Scan directory for multidisc games
    multi_disc_games = {}
    total_files = 0
    error_log = []

    for _, _, files in os.walk(folder_path):
        total_files += len(files)

    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".chd"):
                match = re.match(r"(.+?)\s\((.+?)\)\s\((Disc\s\d+)\)", filename)
                if match:
                    game_title, region, disc = match.groups()
                    if game_title not in multi_disc_games:
                        multi_disc_games[game_title] = []
                    multi_disc_games[game_title].append(os.path.join(root, filename))
            progress_bar["value"] += 1

    # Step 3: Create subdirectories for multi-disc games
    # Step 4: Move games into their appropriate subdirectories
    for game_title, disc_paths in multi_disc_games.items():
        subdir_path = os.path.join(folder_path, game_title)
        if not os.path.exists(subdir_path):
            os.mkdir(subdir_path)

        for disc_path in sorted(
            disc_paths, key=lambda x: re.search(r"(Disc\s\d+)", x).group(0)
        ):
            if os.path.dirname(disc_path) != subdir_path:
                old_path = disc_path
                new_path = os.path.join(subdir_path, os.path.basename(disc_path))
                try:
                    os.rename(old_path, new_path)
                except Exception as e:
                    error_log.append(
                        f"Error moving file '{old_path}' to '{new_path}': {str(e)}"
                    )

    # Step 5: Scan the directory for subdirectories
    subdirectories = [
        os.path.join(folder_path, d)
        for d in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, d))
    ]

    # Step 6: Create the m3u for each subdirectory relative to the input directory
    # Step 7: Save m3u files to the input directory
    for subdir_path in subdirectories:
        game_title = os.path.basename(subdir_path)
        m3u_filename = f"{game_title}.m3u"
        m3u_path = os.path.join(folder_path, m3u_filename)

        chd_files = [f for f in os.listdir(subdir_path) if f.endswith(".chd")]

        if chd_files:
            try:
                with open(m3u_path, "w") as m3u_file:
                    for chd_file in sorted(
                        chd_files, key=lambda x: re.search(r"(Disc\s\d+)", x).group(0)
                    ):
                        m3u_file.write(f"{game_title}/{chd_file}\n")
            except Exception as e:
                error_log.append(f"Error creating m3u file '{m3u_path}': {str(e)}")

    progress_bar["value"] = 0

    if error_log:
        with open(os.path.join(folder_path, "error_log.txt"), "w") as error_file:
            for error in error_log:
                error_file.write(f"{error}\n")

        messagebox.showerror(
            "Error", "Errors occurred during execution. Please check error_log.txt."
        )
    else:
        messagebox.showinfo("Completed", "Organization of PS1 Roms is complete.")
    organize_button.config(state=tk.NORMAL)


# Initialize tkinter window
window = tk.Tk()
window.title("PS1 Roms Organizer")
window.geometry("500x100")

# Create widgets
frame = ttk.Frame(window, padding="10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

browse_button = ttk.Button(frame, text="Browse", command=browse_directory)
browse_button.grid(column=0, row=0, sticky=(tk.W, tk.E))

path_label = ttk.Label(frame, text="")
path_label.grid(column=1, row=0, sticky=(tk.W, tk.E))

organize_button = ttk.Button(
    frame, text="Organize PS1 Roms", state=tk.DISABLED, command=organize_files
)
organize_button.grid(column=2, row=0, sticky=(tk.W, tk.E))

progress_bar = ttk.Progressbar(frame, mode="determinate")
progress_bar.grid(column=0, row=1, columnspan=3, sticky=(tk.W, tk.E))

# Configure column and row weights
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
frame.columnconfigure(1, weight=1)
frame.rowconfigure(1, weight=1)

# Run the main loop
window.mainloop()
