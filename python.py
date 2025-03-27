import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import random
import os
import time

class FileSystemTool:
    def __init__(self, root):
        self.root = root
        self.root.title("File System Recovery & Optimization Tool")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a1a")
        
        # Main frames
        self.sidebar = tk.Frame(root, bg="#252525", width=250)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        self.main_content = tk.Frame(root, bg="#252525")
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Operation variables
        self.operation_running = False
        self.operation_paused = False
        self.current_operation = None
        self.progress = 0
        
        # Sample data
        self.sample_files = [
            {"name": "document.docx", "size": "2.5 MB", "type": "docx", "recoverable": True},
            {"name": "presentation.pptx", "size": "5.1 MB", "type": "pptx", "recoverable": True},
            {"name": "image.jpg", "size": "3.2 MB", "type": "jpg", "recoverable": True},
            {"name": "archive.zip", "size": "150 MB", "type": "zip", "recoverable": False},
            {"name": "config.ini", "size": "12 KB", "type": "ini", "recoverable": True},
            {"name": "report.pdf", "size": "1.8 MB", "type": "pdf", "recoverable": True},
            {"name": "video.mp4", "size": "450 MB", "type": "mp4", "recoverable": False}
        ]
        
        self.setup_sidebar()
        self.setup_main_content()
        
    def setup_sidebar(self):
        # Operation mode selection
        tk.Label(self.sidebar, text="Operation Mode", bg="#252525", fg="#4CAF50").pack(pady=(10, 5))
        self.operation_mode = ttk.Combobox(self.sidebar, values=["File Recovery", "Optimization", "System Analysis"])
        self.operation_mode.current(0)
        self.operation_mode.pack(fill="x", padx=10, pady=5)
        self.operation_mode.bind("<<ComboboxSelected>>", self.update_operation_options)
        
        # Recovery options frame
        self.recovery_frame = tk.Frame(self.sidebar, bg="#252525")
        tk.Label(self.recovery_frame, text="File System Type", bg="#252525", fg="#bbb").pack()
        self.fs_type = ttk.Combobox(self.recovery_frame, values=["NTFS", "ext4", "FAT32"])
        self.fs_type.current(0)
        self.fs_type.pack(fill="x", pady=5)
        
        tk.Label(self.recovery_frame, text="Scan Depth", bg="#252525", fg="#bbb").pack()
        self.scan_depth = ttk.Combobox(self.recovery_frame, values=["Quick Scan", "Deep Scan", "Signature Scan"])
        self.scan_depth.current(0)
        self.scan_depth.pack(fill="x", pady=5)
        self.recovery_frame.pack(fill="x", padx=10, pady=5)
        
        # Optimization options frame (initially hidden)
        self.optimization_frame = tk.Frame(self.sidebar, bg="#252525")
        tk.Label(self.optimization_frame, text="Optimization Type", bg="#252525", fg="#bbb").pack()
        self.opt_type = ttk.Combobox(self.optimization_frame, values=["Defragmentation", "Disk Cleanup", "File Placement"])
        self.opt_type.current(0)
        self.opt_type.pack(fill="x", pady=5)
        
        tk.Label(self.optimization_frame, text="Target Drive", bg="#252525", fg="#bbb").pack()
        self.target_drive = ttk.Combobox(self.optimization_frame, values=["C:", "D:", "E:"])
        self.target_drive.current(0)
        self.target_drive.pack(fill="x", pady=5)
        
        # Control buttons
        tk.Button(self.sidebar, text="Start Operation", bg="#4CAF50", fg="white", 
                 command=self.start_operation).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Pause", bg="#4CAF50", fg="white", 
                 command=self.pause_operation).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Stop", bg="#4CAF50", fg="white", 
                 command=self.stop_operation).pack(fill="x", padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.sidebar, orient="horizontal", length=200, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=10)
        
        # File filter
        tk.Label(self.sidebar, text="File Filter", bg="#252525", fg="#bbb").pack()
        self.file_filter = tk.Entry(self.sidebar, bg="#333", fg="white", insertbackground="white")
        self.file_filter.insert(0, "*.docx, *.jpg, *.pdf")
        self.file_filter.pack(fill="x", padx=10, pady=5)
        
        # Action buttons
        tk.Button(self.sidebar, text="Save Report", bg="#4CAF50", fg="white", 
                 command=self.save_report).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Load Settings", bg="#4CAF50", fg="white", 
                 command=self.load_settings).pack(fill="x", padx=10, pady=5)
        tk.Button(self.sidebar, text="Help", bg="#4CAF50", fg="white", 
                 command=self.show_help).pack(fill="x", padx=10, pady=5)
    
    def setup_main_content(self):
        # Dashboard frame
        dashboard_frame = tk.Frame(self.main_content, bg="#252525")
        dashboard_frame.pack(fill="x", pady=5)
        
        tk.Label(dashboard_frame, text="File System Dashboard", bg="#252525", fg="#4CAF50", 
                font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.current_op_label = tk.Label(dashboard_frame, text="Current Operation: None", bg="#252525", fg="white")
        self.current_op_label.pack(anchor="w", padx=10, pady=5)
        
        # Metrics frame
        metrics_frame = tk.Frame(dashboard_frame, bg="#252525")
        metrics_frame.pack(fill="x", padx=10, pady=10)
        
        self.recoverable_space = self.create_metric_card(metrics_frame, "Recoverable Space", "0 MB", 0)
        self.recoverable_files = self.create_metric_card(metrics_frame, "Recoverable Files", "0", 1)
        self.performance_gain = self.create_metric_card(metrics_frame, "Performance Gain", "0%", 2)
        
        # File list frame with scrollbar
        file_frame = tk.Frame(self.main_content, bg="#252525")
        file_frame.pack(fill="both", expand=True, pady=5)
        
        tk.Label(file_frame, text="Detected Files", bg="#252525", fg="#4CAF50", 
                font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        
        self.file_canvas = tk.Canvas(file_frame, bg="#333", bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_canvas.yview)
        self.scrollable_frame = tk.Frame(self.file_canvas, bg="#333")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.file_canvas.configure(
                scrollregion=self.file_canvas.bbox("all")
            )
        )
        
        self.file_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.file_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.file_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Disk visualization frame
        vis_frame = tk.Frame(self.main_content, bg="#252525")
        vis_frame.pack(fill="x", pady=5)
        
        tk.Label(vis_frame, text="Disk Map Visualization", bg="#252525", fg="#4CAF50", 
                font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        
        self.disk_canvas = tk.Canvas(vis_frame, bg="#333", height=150, bd=0, highlightthickness=0)
        self.disk_canvas.pack(fill="x", padx=10, pady=5)
        self.draw_disk_map()
        
        # Analysis frame
        analysis_frame = tk.Frame(self.main_content, bg="#252525")
        analysis_frame.pack(fill="x", pady=5)
        
        tk.Label(analysis_frame, text="System Analysis", bg="#252525", fg="#4CAF50", 
                font=("Arial", 12)).pack(anchor="w", padx=10, pady=5)
        
        # Analysis table
        self.analysis_table = ttk.Treeview(analysis_frame, columns=("metric", "value", "status"), show="headings")
        self.analysis_table.heading("metric", text="Metric")
        self.analysis_table.heading("value", text="Value")
        self.analysis_table.heading("status", text="Status")
        
        self.analysis_table.column("metric", width=150)
        self.analysis_table.column("value", width=100)
        self.analysis_table.column("status", width=100)
        
        self.analysis_table.pack(fill="x", padx=10, pady=5)
        
        # Add sample data to analysis table
        self.update_analysis_table()
    
    def create_metric_card(self, parent, title, value, column):
        frame = tk.Frame(parent, bg="#333", padx=10, pady=10)
        frame.grid(row=0, column=column, padx=5)
        
        tk.Label(frame, text=title, bg="#333", fg="#bbb").pack()
        value_label = tk.Label(frame, text=value, bg="#333", fg="white", font=("Arial", 14, "bold"))
        value_label.pack()
        
        return value_label
    
    def update_operation_options(self, event=None):
        mode = self.operation_mode.get()
        if mode == "File Recovery":
            self.recovery_frame.pack(fill="x", padx=10, pady=5)
            self.optimization_frame.pack_forget()
        elif mode == "Optimization":
            self.optimization_frame.pack(fill="x", padx=10, pady=5)
            self.recovery_frame.pack_forget()
        else:
            self.recovery_frame.pack_forget()
            self.optimization_frame.pack_forget()
    
    def start_operation(self):
        if self.operation_running:
            return
            
        self.operation_running = True
        self.operation_paused = False
        self.current_operation = self.operation_mode.get()
        self.current_op_label.config(text=f"Current Operation: {self.current_operation}")
        
        # Clear previous files
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Filter recoverable files
        recoverable_files = [f for f in self.sample_files if f["recoverable"]]
        
        # Display files
        for file in recoverable_files:
            self.add_file_to_list(file)
        
        # Start progress simulation
        self.simulate_operation()
        
        # Update analysis
        self.update_analysis_table()
    
    def pause_operation(self):
        if not self.operation_running:
            return
        self.operation_paused = True
    
    def stop_operation(self):
        self.operation_running = False
        self.operation_paused = False
        self.progress = 0
        self.progress_bar["value"] = 0
        self.current_op_label.config(text="Current Operation: None")
    
    def simulate_operation(self):
        if not self.operation_running or self.operation_paused:
            return
            
        if self.progress >= 100:
            self.operation_running = False
            return
            
        self.progress += 2
        self.progress_bar["value"] = self.progress
        
        # Update metrics
        if self.current_operation == "File Recovery":
            recoverable_count = min(int(self.progress * 0.2), len([f for f in self.sample_files if f["recoverable"]]))
            self.recoverable_files.config(text=str(recoverable_count))
            
            space = min(self.progress * 5, 100)
            self.recoverable_space.config(text=f"{space} MB")
        elif self.current_operation == "Optimization":
            gain = min(self.progress, 100)
            self.performance_gain.config(text=f"{gain}%")
        
        self.root.after(200, self.simulate_operation)
    
    def add_file_to_list(self, file):
        frame = tk.Frame(self.scrollable_frame, bg="#333", pady=5)
        frame.pack(fill="x", padx=5, pady=2)
        
        # File icon and name
        icon_label = tk.Label(frame, text="📄", bg="#333", fg="#4CAF50")
        icon_label.pack(side="left", padx=5)
        
        name_label = tk.Label(frame, text=file["name"], bg="#333", fg="white")
        name_label.pack(side="left", padx=5)
        
        # File size
        size_label = tk.Label(frame, text=file["size"], bg="#333", fg="white")
        size_label.pack(side="right", padx=20)
        
        # Action buttons
        btn_frame = tk.Frame(frame, bg="#333")
        btn_frame.pack(side="right", padx=5)
        
        recover_btn = tk.Button(btn_frame, text="Recover", bg="#4CAF50", fg="white", 
                              command=lambda: self.recover_file(file["name"]))
        recover_btn.pack(side="left", padx=2)
        
        preview_btn = tk.Button(btn_frame, text="Preview", bg="#2196F3", fg="white", 
                               command=lambda: self.preview_file(file["name"]))
        preview_btn.pack(side="left", padx=2)
    
    def recover_file(self, filename):
        messagebox.showinfo("Recovery", f"Recovering file: {filename}\n(Simulated in this demo)")
    
    def preview_file(self, filename):
        messagebox.showinfo("Preview", f"Previewing file: {filename}\n(Simulated in this demo)")
    
    def draw_disk_map(self):
        self.disk_canvas.delete("all")
        width = self.disk_canvas.winfo_width()
        height = self.disk_canvas.winfo_height()
        
        sectors = 50
        sector_width = width / sectors
        
        for i in range(sectors):
            # Simulate different sector types
            r = random.random()
            if r < 0.1:
                color = "#4CAF50"  # Free space
            elif r < 0.3:
                color = "#FF5722"  # Fragmented
            elif r < 0.4:
                color = "#F44336"  # Bad sectors
            else:
                color = "#2196F3"  # Used space
            
            self.disk_canvas.create_rectangle(
                i * sector_width, 0,
                (i + 1) * sector_width - 2, height,
                fill=color, outline=""
            )
        
        # Add legend
        self.disk_canvas.create_text(10, 20, text="Legend:", fill="white", anchor="w")
        
        colors = ["#2196F3", "#FF5722", "#4CAF50", "#F44336"]
        labels = ["Used", "Fragmented", "Free", "Bad"]
        
        for i, (color, label) in enumerate(zip(colors, labels)):
            x = 80 + i * 100
            self.disk_canvas.create_rectangle(x, 10, x + 15, 20, fill=color, outline="")
            self.disk_canvas.create_text(x + 20, 15, text=label, fill="white", anchor="w")
    
    def update_analysis_table(self):
        # Clear existing data
        for item in self.analysis_table.get_children():
            self.analysis_table.delete(item)
        
        # Add sample metrics
        metrics = [
            ("Fragmentation Level", "27%", "Moderate"),
            ("Free Space", "45.2 GB", "Good"),
            ("Disk Health", "92%", "Excellent")
        ]
        
        for metric, value, status in metrics:
            self.analysis_table.insert("", "end", values=(metric, value, status))
    
    def save_report(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Success", f"Report saved to:\n{file_path}\n(Simulated in this demo)")
    
    def load_settings(self):
        messagebox.showinfo("Settings", "Settings loaded (simulated in this demo)")
    
    def show_help(self):
        help_text = """File System Recovery & Optimization Tool Help:

1. Select operation mode (Recovery/Optimization/Analysis)
2. Configure options for the selected mode
3. Click Start to begin the operation
