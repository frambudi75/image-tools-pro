import os
import io
import json
import sys
import threading
import time
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont, ImageTk, ExifTags
from fpdf import FPDF
import PyPDF2
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
try:
    import cairosvg
    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# Application version
CURRENT_VERSION = "6.0.0"
GITHUB_REPO = "frambudi75/jpg-to-pdf-convert"  # Replace with actual GitHub repository

# Update settings

class ImageCompressorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Image Tools PRO")
        self.geometry("900x900")
        self.resizable(True, True)

        # Initialize variables
        self.image_paths = []
        self.pdf_image_paths = []  # Separate list for PDF export
        self.backup_paths = []
        self.history = []
        self.undo_available = False
        self.processing = False
        self.output_folder = os.path.join(os.getcwd(), "output")
        os.makedirs(self.output_folder, exist_ok=True)

        # Load settings
        self.load_settings()

        # Bind keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.select_files())
        self.bind('<Control-s>', lambda e: self.save_settings())
        self.bind('<Control-z>', lambda e: self.undo_last_operation())
        self.bind('<F1>', lambda e: self.show_help())



        self.label_title = ctk.CTkLabel(self, text="📷 Image Tools PRO", font=("Arial", 20, "bold"))
        self.label_title.pack(pady=10)

        # Tabview untuk mengorganisir fitur
        self.tabview = ctk.CTkTabview(self, width=850, height=700)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)

        # Tab Kompresi
        self.tabview.add("Kompresi")
        self.setup_compression_tab()

        # Tab Konversi
        self.tabview.add("Konversi")
        self.setup_conversion_tab()

        # Tab PDF
        self.tabview.add("PDF")
        self.setup_pdf_tab()

        # Tab Riwayat
        self.tabview.add("Riwayat")
        self.setup_history_tab()

        # Tab Pengaturan
        self.tabview.add("Pengaturan")
        self.setup_settings_tab()

        # Status bar
        self.status_frame = ctk.CTkFrame(self, height=30)
        self.status_frame.pack(fill="x", padx=20, pady=(0, 10))
        self.status_label = ctk.CTkLabel(self.status_frame, text="Siap digunakan", anchor="w")
        self.status_label.pack(side="left", padx=10)
        self.credit_label = ctk.CTkLabel(self.status_frame, text="By: Habib Frambudi", anchor="e")
        self.credit_label.pack(side="right", padx=10)

        # Output text di bagian bawah
        self.output_text = ctk.CTkTextbox(self, height=120, width=850)
        self.output_text.pack(pady=(0, 10), padx=20)

        # Update tooltips
        self.update_tooltips()

        # Application is ready

    def setup_compression_tab(self):
        tab = self.tabview.tab("Kompresi")

        # File selection
        self.file_frame = ctk.CTkFrame(tab)
        self.file_frame.pack(pady=10, padx=20, fill="x")

        self.file_button = ctk.CTkButton(self.file_frame, text="📁 Pilih Gambar", command=self.select_files)
        self.file_button.grid(row=0, column=0, padx=10, pady=5)

        self.folder_button = ctk.CTkButton(self.file_frame, text="📂 Pilih Folder", command=self.select_folder)
        self.folder_button.grid(row=0, column=1, padx=10, pady=5)

        self.pdf_button = ctk.CTkButton(self.file_frame, text="📄 Pilih PDF", command=self.select_pdf)
        self.pdf_button.grid(row=0, column=2, padx=10, pady=5)

        # Compression settings
        self.settings_frame = ctk.CTkFrame(tab)
        self.settings_frame.pack(pady=10, padx=20, fill="x")

        # Quality presets
        self.quality_preset_frame = ctk.CTkFrame(self.settings_frame)
        self.quality_preset_frame.pack(pady=5, padx=20, fill="x")

        self.quality_preset_label = ctk.CTkLabel(self.quality_preset_frame, text="Preset Kompresi:")
        self.quality_preset_label.pack(pady=2)

        self.quality_preset_buttons = []
        presets = [("Ringan (90%)", 90), ("Sedang (75%)", 75), ("Agresif (50%)", 50), ("Ekstrem (25%)", 25)]
        for text, value in presets:
            btn = ctk.CTkButton(self.quality_preset_frame, text=text, command=lambda v=value: self.set_quality_preset(v), width=80, height=25, font=("Arial", 10))
            btn.pack(side="left", padx=2)
            self.quality_preset_buttons.append(btn)

        self.quality_slider = ctk.CTkSlider(self.settings_frame, from_=10, to=100, number_of_steps=18, command=self.update_quality_label)
        self.quality_slider.set(75)  # Changed default to 75% for better compression
        self.quality_slider.pack(pady=5, padx=20, fill="x")
        self.quality_label = ctk.CTkLabel(self.settings_frame, text="Kualitas: 75%")
        self.quality_label.pack()

        self.resize_slider = ctk.CTkSlider(self.settings_frame, from_=10, to=100, number_of_steps=18, command=self.update_resize_label)
        self.resize_slider.set(100)
        self.resize_slider.pack(pady=5, padx=20, fill="x")
        self.resize_label = ctk.CTkLabel(self.settings_frame, text="Resize: 100% (tidak diubah)")
        self.resize_label.pack()

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(tab, width=800)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, padx=20)

        # Action button
        self.compress_button = ctk.CTkButton(tab, text="🚀 Kompres Sekarang", command=self.compress_all, font=("Arial", 14, "bold"))
        self.compress_button.pack(pady=10)

    def setup_conversion_tab(self):
        tab = self.tabview.tab("Konversi")

        # File selection
        self.conv_file_frame = ctk.CTkFrame(tab)
        self.conv_file_frame.pack(pady=10, padx=20, fill="x")

        self.conv_file_button = ctk.CTkButton(self.conv_file_frame, text="📁 Pilih Gambar", command=self.select_files)
        self.conv_file_button.grid(row=0, column=0, padx=10, pady=5)

        self.conv_folder_button = ctk.CTkButton(self.conv_file_frame, text="📂 Pilih Folder", command=self.select_folder)
        self.conv_folder_button.grid(row=0, column=1, padx=10, pady=5)

        # Conversion settings
        self.conv_settings_frame = ctk.CTkFrame(tab)
        self.conv_settings_frame.pack(pady=10, padx=20, fill="x")

        self.output_format_label = ctk.CTkLabel(self.conv_settings_frame, text="Format Output:")
        self.output_format_label.pack(pady=5)
        self.output_format_menu = ctk.CTkOptionMenu(self.conv_settings_frame, values=["JPG", "PNG", "ICO", "BMP", "GIF", "TIFF", "WEBP"])
        self.output_format_menu.set("PNG")
        self.output_format_menu.pack(pady=5)

        self.conv_resize_slider = ctk.CTkSlider(self.conv_settings_frame, from_=10, to=100, number_of_steps=18, command=self.update_conv_resize_label)
        self.conv_resize_slider.set(100)
        self.conv_resize_slider.pack(pady=5, padx=20, fill="x")
        self.conv_resize_label = ctk.CTkLabel(self.conv_settings_frame, text="Resize: 100% (tidak diubah)")
        self.conv_resize_label.pack()

        # Metadata preservation checkbox
        self.preserve_metadata_checkbox = ctk.CTkCheckBox(self.conv_settings_frame, text="Pelestarian Metadata (EXIF)")
        self.preserve_metadata_checkbox.pack(pady=5)

        # Watermark entry removed as requested

        # Progress bar
        self.conv_progress_bar = ctk.CTkProgressBar(tab, width=800)
        self.conv_progress_bar.set(0)
        self.conv_progress_bar.pack(pady=10, padx=20)

        # Action button
        self.convert_button = ctk.CTkButton(tab, text="🔄 Convert All Formats", command=self.convert_all_formats, font=("Arial", 14, "bold"))
        self.convert_button.pack(pady=10)

    def setup_pdf_tab(self):
        tab = self.tabview.tab("PDF")

        # File selection for PDF export
        self.pdf_file_frame = ctk.CTkFrame(tab)
        self.pdf_file_frame.pack(pady=10, padx=20, fill="x")

        self.pdf_file_button = ctk.CTkButton(self.pdf_file_frame, text="📁 Pilih Gambar untuk PDF", command=self.select_files_for_pdf)
        self.pdf_file_button.grid(row=0, column=0, padx=10, pady=5)

        self.pdf_folder_button = ctk.CTkButton(self.pdf_file_frame, text="📂 Pilih Folder Gambar untuk PDF", command=self.select_folder_for_pdf)
        self.pdf_folder_button.grid(row=0, column=1, padx=10, pady=5)

        # PDF layout options
        self.pdf_layout_frame = ctk.CTkFrame(tab)
        self.pdf_layout_frame.pack(pady=10, padx=20, fill="x")

        self.pdf_layout_label = ctk.CTkLabel(self.pdf_layout_frame, text="Tata Letak PDF:")
        self.pdf_layout_label.pack(pady=5)
        self.pdf_layout_menu = ctk.CTkOptionMenu(self.pdf_layout_frame, values=["Satu gambar per halaman"])
        self.pdf_layout_menu.set("Satu gambar per halaman")
        self.pdf_layout_menu.pack(pady=5)

        # Sort by filename checkbox
        self.sort_by_filename_checkbox = ctk.CTkCheckBox(self.pdf_layout_frame, text="Urutkan berdasarkan nama file")
        self.sort_by_filename_checkbox.pack(pady=5)

        # PDF operations
        self.pdf_frame = ctk.CTkFrame(tab)
        self.pdf_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.export_pdf_button = ctk.CTkButton(self.pdf_frame, text="📄 Export Gambar ke PDF", command=self.export_to_pdf, font=("Arial", 12))
        self.export_pdf_button.pack(pady=10, padx=20, fill="x")

        self.merge_pdf_button = ctk.CTkButton(self.pdf_frame, text="📄 Gabung PDF", command=self.merge_pdfs, font=("Arial", 12))
        self.merge_pdf_button.pack(pady=10, padx=20, fill="x")

        self.compress_pdf_button = ctk.CTkButton(self.pdf_frame, text="📄 Kompres PDF", command=self.select_and_compress_pdf, font=("Arial", 12))
        self.compress_pdf_button.pack(pady=10, padx=20, fill="x")

        # Instructions
        self.pdf_info = ctk.CTkLabel(self.pdf_frame, text="Pilih gambar untuk export ke PDF menggunakan tombol di atas\nUntuk Gabung PDF: Pilih file PDF yang ingin digabung\nUntuk Kompres PDF: Pilih file PDF yang ingin dikompresi", wraplength=400)
        self.pdf_info.pack(pady=20, padx=20)

    def setup_settings_tab(self):
        tab = self.tabview.tab("Pengaturan")

        # Theme toggle
        self.theme_frame = ctk.CTkFrame(tab)
        self.theme_frame.pack(pady=10, padx=20, fill="x")

        self.theme_label = ctk.CTkLabel(self.theme_frame, text="Tema Aplikasi:", font=("Arial", 14))
        self.theme_label.pack(pady=10)

        self.theme_menu = ctk.CTkOptionMenu(self.theme_frame, values=["System", "Light", "Dark"], command=self.change_theme)
        self.theme_menu.set("System")
        self.theme_menu.pack(pady=5)

        # Output folder selection
        self.output_frame = ctk.CTkFrame(tab)
        self.output_frame.pack(pady=10, padx=20, fill="x")

        self.output_label = ctk.CTkLabel(self.output_frame, text="Folder Output:", font=("Arial", 14))
        self.output_label.pack(pady=10)

        self.output_path_label = ctk.CTkLabel(self.output_frame, text=self.output_folder, wraplength=400)
        self.output_path_label.pack(pady=5)

        self.change_output_button = ctk.CTkButton(self.output_frame, text="🔄 Ubah Folder Output", command=self.change_output_folder)
        self.change_output_button.pack(pady=10)

        # Keyboard shortcuts reference
        self.shortcuts_frame = ctk.CTkFrame(tab)
        self.shortcuts_frame.pack(pady=10, padx=20, fill="x")

        self.shortcuts_label = ctk.CTkLabel(self.shortcuts_frame, text="Pintasan Keyboard:", font=("Arial", 14))
        self.shortcuts_label.pack(pady=10)

        shortcuts_text = """Ctrl+O: Pilih file gambar
Ctrl+S: Simpan pengaturan
Ctrl+Z: Undo operasi terakhir
F1: Bantuan (belum diimplementasi)"""

        self.shortcuts_textbox = ctk.CTkTextbox(self.shortcuts_frame, height=100, width=400)
        self.shortcuts_textbox.pack(pady=5, padx=20)
        self.shortcuts_textbox.insert("0.0", shortcuts_text)
        self.shortcuts_textbox.configure(state="disabled")



        # Check for updates button
        self.update_frame = ctk.CTkFrame(tab)
        self.update_frame.pack(pady=10, padx=20, fill="x")

        self.update_label = ctk.CTkLabel(self.update_frame, text=f"Versi Saat Ini: {CURRENT_VERSION}", font=("Arial", 14))
        self.update_label.pack(pady=10)

        self.check_update_button = ctk.CTkButton(self.update_frame, text="🔍 Cek Update", command=self.check_for_updates)
        self.check_update_button.pack(pady=10)

        # Developer support
        self.developer_frame = ctk.CTkFrame(tab)
        self.developer_frame.pack(pady=10, padx=20, fill="x")

        self.developer_label = ctk.CTkLabel(self.developer_frame, text="Support Developer:", font=("Arial", 14))
        self.developer_label.pack(pady=10, side="left")

        self.developer_button = ctk.CTkButton(self.developer_frame, text="Habib Frambudi", command=self.show_qris_image, font=("Arial", 14, "underline"))
        self.developer_button.pack(pady=10, side="left", padx=(5, 0))

    def change_theme(self, theme):
        ctk.set_appearance_mode(theme)

    def change_output_folder(self):
        folder = filedialog.askdirectory(title="Pilih Folder Output")
        if folder:
            self.output_folder = folder
            self.output_path_label.configure(text=self.output_folder)

    def update_conv_resize_label(self, value):
        val = int(float(value))
        text = "Resize: 100% (tidak diubah)" if val == 100 else f"Resize: {val}%"
        self.conv_resize_label.configure(text=text)

    def set_quality_preset(self, value):
        """Set quality slider to preset value"""
        self.quality_slider.set(value)
        self.update_quality_label(value)

    def update_quality_label(self, value):
        self.quality_label.configure(text=f"Kualitas: {int(float(value))}%")

    def update_resize_label(self, value):
        val = int(float(value))
        text = "Resize: 100% (tidak diubah)" if val == 100 else f"Resize: {val}%"
        self.resize_label.configure(text=text)

    def select_files(self):
        paths = filedialog.askopenfilenames(title="Pilih gambar", filetypes=[("Images", "*.jpg *.jpeg *.png *.ico *.bmp *.gif *.tiff *.webp *.svg")])
        if paths:
            self.image_paths = list(paths)
            self.output_text.insert("end", f"✅ {len(paths)} gambar dipilih.\n")

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Pilih Folder Gambar")
        if folder_path:
            self.image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".ico", ".bmp", ".gif", ".tiff", ".webp", ".svg"))]
            self.output_text.insert("end", f"✅ {len(self.image_paths)} gambar dari folder dipilih.\n")

    def select_pdf(self):
        pdf_path = filedialog.askopenfilename(title="Pilih PDF", filetypes=[("PDF files", "*.pdf")])
        if pdf_path:
            if PYMUPDF_AVAILABLE:
                try:
                    doc = fitz.open(pdf_path)
                    images = []
                    for page_num in range(len(doc)):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap()
                        img = Image.open(io.BytesIO(pix.tobytes()))
                        images.append(img)
                    doc.close()
                    # Save images temporarily and add to image_paths
                    temp_dir = os.path.join(self.output_folder, "temp_pdf_images")
                    os.makedirs(temp_dir, exist_ok=True)
                    self.image_paths = []
                    for i, img in enumerate(images):
                        img_path = os.path.join(temp_dir, f"page_{i+1}.png")
                        img.save(img_path)
                        self.image_paths.append(img_path)
                    self.output_text.insert("end", f"✅ {len(images)} halaman PDF dikonversi ke gambar.\n")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mengkonversi PDF: {e}")
            else:
                messagebox.showerror("Error", "PyMuPDF tidak tersedia. Instal PyMuPDF untuk konversi PDF ke gambar.")



    def select_files_for_pdf(self):
        paths = filedialog.askopenfilenames(title="Pilih gambar untuk PDF", filetypes=[("Images", "*.jpg *.jpeg *.png *.ico *.bmp *.gif *.tiff *.webp *.svg")])
        if paths:
            self.pdf_image_paths = list(paths)
            self.output_text.insert("end", f"✅ {len(paths)} gambar dipilih untuk PDF.\n")

    def select_folder_for_pdf(self):
        folder_path = filedialog.askdirectory(title="Pilih Folder Gambar untuk PDF")
        if folder_path:
            self.pdf_image_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png", ".ico", ".bmp", ".gif", ".tiff", ".webp", ".svg"))]
            self.output_text.insert("end", f"✅ {len(self.pdf_image_paths)} gambar dari folder dipilih untuk PDF.\n")

    def export_to_pdf(self):
        if not self.pdf_image_paths:
            messagebox.showerror("Tidak ada file", "Silakan pilih gambar untuk PDF terlebih dahulu.")
            return

        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return

        try:
            pdf = FPDF(unit="pt", format="A4")
            for img_path in self.pdf_image_paths:
                img = Image.open(img_path)
                img = img.convert("RGB")
                w, h = img.size

                # A4 dimensions in points (1/72 inch)
                a4_width = 595
                a4_height = 842

                # Calculate scaling to fit image within A4 page while maintaining aspect ratio
                scale = min(a4_width / w, a4_height / h)
                new_w = w * scale
                new_h = h * scale

                # Center the image on the page
                x = (a4_width - new_w) / 2
                y = (a4_height - new_h) / 2

                pdf.add_page()
                pdf.image(img_path, x=x, y=y, w=new_w, h=new_h)
            pdf.output(pdf_path)
            self.output_text.insert("end", f"📄 PDF disimpan: {pdf_path}\n")
            messagebox.showinfo("Selesai", "PDF berhasil dibuat!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat PDF: {e}")

    def merge_pdfs(self):
        pdf_paths = filedialog.askopenfilenames(title="Pilih PDF untuk digabung", filetypes=[("PDF files", "*.pdf")])
        if not pdf_paths:
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_path:
            return

        try:
            merger = PyPDF2.PdfMerger()
            for pdf in pdf_paths:
                merger.append(pdf)
            merger.write(output_path)
            merger.close()
            self.output_text.insert("end", f"📄 PDF gabungan disimpan: {output_path}\n")
            messagebox.showinfo("Selesai", "PDF berhasil digabung!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menggabung PDF: {e}")

    def compress_pdf(self, input_path, output_path):
        """Kompresi file PDF menggunakan PyPDF2"""
        try:
            with open(input_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()

                for page in reader.pages:
                    page.compress_content_streams()  # Compress content streams
                    writer.add_page(page)

                # Menulis file PDF yang dikompresi
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            return True
        except Exception as e:
            print(f"Error saat mengompresi PDF: {e}")
            raise e

    def select_and_compress_pdf(self):
        input_path = filedialog.askopenfilename(title="Pilih PDF untuk dikompresi", filetypes=[("PDF files", "*.pdf")])
        if not input_path:
            return

        dir_name = os.path.dirname(input_path)
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        default_output = os.path.join(dir_name, f"{base_name}_compressed.pdf")

        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=os.path.basename(default_output),
            title="Simpan file PDF hasil kompresi"
        )
        if not output_path:
            return

        self.status_label.configure(text="Mengompresi PDF...")
        self.processing = True

        def run_compress():
            try:
                orig_size = os.path.getsize(input_path)
                self.compress_pdf(input_path, output_path)
                comp_size = os.path.getsize(output_path)

                saving = orig_size - comp_size
                percent = int(100 * saving / orig_size) if orig_size > 0 else 0

                orig_kb = orig_size // 1024
                comp_kb = comp_size // 1024

                summary = f"Kompresi PDF selesai: {orig_kb} KB → {comp_kb} KB (↓{percent}%)"

                self.after(0, lambda: self.output_text.insert("end", f"📄 {summary}\n"))
                self.after(0, lambda: self.add_to_history("PDF Compression", f"Compressed {os.path.basename(input_path)}: saved {percent}% space"))
                self.after(0, lambda: messagebox.showinfo("Selesai", f"PDF berhasil dikompresi!\nUkuran: {orig_kb} KB → {comp_kb} KB (↓{percent}%)"))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Gagal mengompresi PDF: {e}"))
            finally:
                self.processing = False
                self.after(0, lambda: self.status_label.configure(text="Siap digunakan"))

        threading.Thread(target=run_compress, daemon=True).start()



    def load_settings(self):
        """Load settings from JSON file"""
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    self.output_folder = settings.get('output_folder', self.output_folder)
                    theme = settings.get('theme', 'System')
                    ctk.set_appearance_mode(theme)
                    self.theme_menu.set(theme)
            except:
                pass

    def save_settings(self):
        """Save current settings to JSON file"""
        settings = {
            'output_folder': self.output_folder,
            'theme': self.theme_menu.get()
        }
        with open("settings.json", 'w') as f:
            json.dump(settings, f, indent=4)



    def setup_history_tab(self):
        """Setup history tab to show operation logs"""
        tab = self.tabview.tab("Riwayat")

        # History display
        self.history_frame = ctk.CTkScrollableFrame(tab)
        self.history_frame.pack(pady=20, padx=20, fill="both", expand=True)

        self.history_label = ctk.CTkLabel(self.history_frame, text="Riwayat Operasi:", font=("Arial", 16, "bold"))
        self.history_label.pack(pady=10)

        self.history_text = ctk.CTkTextbox(self.history_frame, height=300, width=800)
        self.history_text.pack(pady=10, padx=20, fill="both", expand=True)

        # Buttons frame
        self.history_buttons_frame = ctk.CTkFrame(self.history_frame)
        self.history_buttons_frame.pack(pady=10, fill="x")

        # Clear history button
        self.clear_history_button = ctk.CTkButton(self.history_buttons_frame, text="🗑️ Hapus Riwayat", command=self.clear_history)
        self.clear_history_button.pack(side="left", padx=5)

        # View compression log button
        self.view_log_button = ctk.CTkButton(self.history_buttons_frame, text="📋 Lihat Log Kompresi", command=self.view_compression_log)
        self.view_log_button.pack(side="left", padx=5)

        # Load existing history
        self.load_history()

    def update_tooltips(self):
        """Update tooltips for all buttons"""
        try:
            self.file_button.configure(tooltip_text="Pilih file gambar (Ctrl+O)")
            self.folder_button.configure(tooltip_text="Pilih folder berisi gambar")
            self.pdf_button.configure(tooltip_text="Konversi PDF ke gambar")
            self.compress_button.configure(tooltip_text="Kompres gambar dengan pengaturan saat ini")
            self.convert_button.configure(tooltip_text="Konversi format gambar")
            self.export_pdf_button.configure(tooltip_text="Export gambar ke PDF")
            self.merge_pdf_button.configure(tooltip_text="Gabung beberapa PDF")
            self.compress_pdf_button.configure(tooltip_text="Kompres file PDF")
            self.change_output_button.configure(tooltip_text="Ubah folder output")
        except:
            pass  # Tooltips might not be supported in all versions

    def load_history(self):
        """Load history from file"""
        history_file = "history.json"
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.history = json.load(f)
                    self.update_history_display()
            except:
                self.history = []

    def save_history(self):
        """Save history to file"""
        with open("history.json", 'w') as f:
            json.dump(self.history, f, indent=4, default=str)

    def add_to_history(self, operation, details):
        """Add operation to history"""
        entry = {
            'timestamp': datetime.now(),
            'operation': operation,
            'details': details
        }
        self.history.append(entry)
        if len(self.history) > 100:  # Keep only last 100 entries
            self.history = self.history[-100:]
        self.save_history()
        self.update_history_display()

    def update_history_display(self):
        """Update history display in tab"""
        self.history_text.delete("0.0", "end")
        for entry in reversed(self.history[-20:]):  # Show last 20 entries
            time_str = entry['timestamp'].strftime("%Y-%m-%d %H:%M:%S") if isinstance(entry['timestamp'], datetime) else str(entry['timestamp'])
            self.history_text.insert("end", f"[{time_str}] {entry['operation']}\n{entry['details']}\n\n")

    def clear_history(self):
        """Clear operation history"""
        self.history = []
        self.save_history()
        self.update_history_display()
        messagebox.showinfo("Info", "Riwayat telah dihapus!")

    def view_compression_log(self):
        """View the compression log file"""
        log_file = "compression_log.txt"
        if not os.path.exists(log_file):
            messagebox.showinfo("Info", "File log kompresi tidak ditemukan.")
            return

        try:
            with open(log_file, 'r') as f:
                log_content = f.read()

            # Create log viewer window
            log_window = ctk.CTkToplevel(self)
            log_window.title("Log Kompresi")
            log_window.geometry("800x600")
            log_window.resizable(True, True)

            # Make it modal
            log_window.grab_set()

            # Log text area
            log_textbox = ctk.CTkTextbox(log_window, wrap="word")
            log_textbox.pack(pady=20, padx=20, fill="both", expand=True)
            log_textbox.insert("0.0", log_content)
            log_textbox.configure(state="disabled")

            # Close button
            close_button = ctk.CTkButton(log_window, text="Tutup", command=log_window.destroy)
            close_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca file log: {e}")

    def undo_last_operation(self):
        """Undo last compression/conversion operation"""
        if not self.undo_available:
            messagebox.showinfo("Info", "Tidak ada operasi yang bisa di-undo.")
            return

        # Restore from backup
        for backup_path, original_path in zip(self.backup_paths, self.image_paths):
            if os.path.exists(backup_path):
                os.replace(backup_path, original_path)

        # Clean up backup folder
        backup_dir = os.path.join(self.output_folder, "backup")
        if os.path.exists(backup_dir):
            import shutil
            shutil.rmtree(backup_dir)

        self.undo_available = False
        self.output_text.insert("end", "🔄 Operasi terakhir telah di-undo.\n")
        self.status_label.configure(text="Operasi di-undo")
        messagebox.showinfo("Info", "Operasi terakhir telah di-undo!")

    def create_backup(self):
        """Create backup of original files"""
        if not self.image_paths:
            return

        backup_dir = os.path.join(self.output_folder, "backup")
        os.makedirs(backup_dir, exist_ok=True)

        self.backup_paths = []
        for path in self.image_paths:
            backup_path = os.path.join(backup_dir, os.path.basename(path))
            import shutil
            shutil.copy2(path, backup_path)
            self.backup_paths.append(backup_path)

    def preserve_exif(self, img, path):
        """Preserve EXIF data if available"""
        try:
            if hasattr(img, '_getexif') and img._getexif():
                exif_dict = img._getexif()
                if exif_dict:
                    # Convert to proper format for saving
                    exif_bytes = img.info.get('exif')
                    if exif_bytes:
                        return exif_bytes
        except:
            pass
        return None

    def bulk_rename_files(self, output_paths, prefix="", suffix="", start_num=1):
        """Bulk rename output files"""
        if not prefix and not suffix:
            return output_paths

        renamed_paths = []
        for i, path in enumerate(output_paths):
            dir_name = os.path.dirname(path)
            ext = os.path.splitext(path)[1]
            base_name = f"{prefix}{start_num + i}{suffix}{ext}"
            new_path = os.path.join(dir_name, base_name)
            if os.path.exists(path):
                os.rename(path, new_path)
            renamed_paths.append(new_path)

        return renamed_paths

    def process_images_threaded(self, func, *args):
        """Process images in a separate thread to keep UI responsive"""
        if self.processing:
            messagebox.showwarning("Warning", "Operasi sedang berlangsung, tunggu selesai.")
            return

        self.processing = True
        self.status_label.configure(text="Memproses...")

        def run():
            try:
                func(*args)
            finally:
                self.processing = False
                self.after(0, lambda: self.status_label.configure(text="Siap digunakan"))

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    def compress_all(self):
        """Modified compress_all with threading and additional features"""
        if not self.image_paths:
            messagebox.showerror("Tidak ada file", "Silakan pilih gambar terlebih dahulu.")
            return

        # Auto create output folder
        os.makedirs(self.output_folder, exist_ok=True)

        # Create backup if enabled
        self.create_backup()
        self.undo_available = True

        def _compress():
            quality = int(self.quality_slider.get())
            resize = int(self.resize_slider.get())

            total_saving = 0
            total_orig = 0
            total_comp = 0
            log = []
            output_paths = []

            # Full logging setup
            import logging
            logging.basicConfig(filename='compression_log.txt', level=logging.INFO,
                                format='%(asctime)s - %(levelname)s - %(message)s')

            format_map = {
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "png": "PNG",
                "ico": "ICO",
                "bmp": "BMP",
                "gif": "GIF",
                "tiff": "TIFF",
                "webp": "WEBP"
            }

            logging.info(f"Starting compression with quality={quality}, resize={resize}%")
            logging.info(f"Processing {len(self.image_paths)} files")

            total_files = len(self.image_paths)
            for i, path in enumerate(self.image_paths):
                try:
                    logging.info(f"Processing file {i+1}/{total_files}: {path}")

                    # Check if file is locked
                    with open(path, 'rb') as f:
                        pass

                    orig_size = os.path.getsize(path)
                    ext = os.path.splitext(path)[1].lower()
                    logging.info(f"Original size: {orig_size} bytes ({orig_size//1024} KB)")

                    if ext == ".svg":
                        if CAIROSVG_AVAILABLE:
                            png_path = path.replace(".svg", "_temp.png")
                            cairosvg.svg2png(url=path, write_to=png_path)
                            img = Image.open(png_path)
                            os.remove(png_path)
                            save_format = "PNG"
                            save_path = os.path.join(self.output_folder, os.path.basename(path).replace(".svg", ".png"))
                            logging.info("Converted SVG to PNG")
                        else:
                            raise Exception("Cairosvg tidak tersedia untuk konversi SVG.")
                    else:
                        img = Image.open(path)
                        save_format = format_map.get(ext[1:], "PNG")
                        # Save compressed file to output folder
                        save_path = os.path.join(self.output_folder, os.path.basename(path))
                        logging.info(f"Save format: {save_format}, Save path: {save_path}")

                    # Preserve EXIF
                    exif_data = self.preserve_exif(img, path)
                    logging.info(f"EXIF data preserved: {exif_data is not None}")

                    original_dimensions = img.size
                    logging.info(f"Original dimensions: {original_dimensions}")

                    if resize < 100:
                        w, h = img.size
                        new_size = (int(w * resize / 100), int(h * resize / 100))
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        logging.info(f"Resized to: {new_size}")

                    # Save with EXIF preservation
                    save_kwargs = {
                        'format': save_format,
                        'quality': quality if save_format == "JPEG" else None,
                        'optimize': save_format in ["JPEG", "PNG"]
                    }
                    if save_format == "PNG":
                        save_kwargs['optimize'] = True
                    if exif_data and save_format == "JPEG":
                        save_kwargs['exif'] = exif_data

                    logging.info(f"Save kwargs: {save_kwargs}")
                    img.save(save_path, **save_kwargs)
                    comp_size = os.path.getsize(save_path)
                    output_paths.append(save_path)

                    saving = orig_size - comp_size
                    total_saving += saving
                    total_orig += orig_size
                    total_comp += comp_size

                    logging.info(f"Compressed size: {comp_size} bytes ({comp_size//1024} KB)")
                    logging.info(f"Space saved: {saving} bytes ({saving//1024} KB)")

                    log.append(f"{os.path.basename(path)}: {orig_size//1024}KB → {comp_size//1024}KB ({'↓' if comp_size < orig_size else '↑'}{abs(orig_size - comp_size)//1024}KB)")

                    # Update progress
                    progress = (i + 1) / total_files
                    self.after(0, lambda p=progress: self.progress_bar.set(p))

                except Exception as e:
                    error_msg = f"❌ Gagal: {os.path.basename(path)} - {e}"
                    log.append(error_msg)
                    logging.error(error_msg)

            percent = int(100 * (total_orig - total_comp) / total_orig) if total_orig > 0 else 0
            summary = f"\nTotal saving: {total_orig//1024}KB → {total_comp//1024}KB (↓{percent}%)"
            log.append(summary)
            logging.info(summary)

            # Add to history
            details = f"Compressed {total_files} files, saved {percent}% space"
            self.after(0, lambda: self.add_to_history("Compression", details))

            self.after(0, lambda l=log: self.output_text.insert("end", "\n".join(l) + "\n"))
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: messagebox.showinfo("Selesai", f"Kompresi selesai! Total penghematan: {percent}%"))

        self.process_images_threaded(_compress)

    def convert_all_formats(self):
        """Modified convert_all_formats with threading and additional features"""
        if not self.image_paths:
            messagebox.showerror("Tidak ada file", "Silakan pilih gambar terlebih dahulu.")
            return

        os.makedirs(self.output_folder, exist_ok=True)

        def _convert():
            resize = int(self.conv_resize_slider.get())
            output_format = self.output_format_menu.get().lower()

            log = []
            output_paths = []

            format_map = {
                "jpg": "JPEG",
                "jpeg": "JPEG",
                "png": "PNG",
                "ico": "ICO",
                "bmp": "BMP",
                "gif": "GIF",
                "tiff": "TIFF",
                "webp": "WEBP"
            }

            total_files = len(self.image_paths)
            for i, path in enumerate(self.image_paths):
                try:
                    with open(path, 'rb') as f:
                        pass

                    ext = os.path.splitext(path)[1].lower()

                    if ext == ".svg":
                        if CAIROSVG_AVAILABLE:
                            png_path = path.replace(".svg", "_temp.png")
                            cairosvg.svg2png(url=path, write_to=png_path)
                            img = Image.open(png_path)
                            os.remove(png_path)
                            save_format = "PNG"
                            save_path = os.path.join(self.output_folder, os.path.basename(path).replace(".svg", ".png"))
                        else:
                            raise Exception("Cairosvg tidak tersedia untuk konversi SVG.")
                    else:
                        img = Image.open(path)
                        save_format = format_map[output_format]
                        save_path = os.path.join(self.output_folder, os.path.basename(path).replace(ext, f".{output_format}"))

                        if output_format in ["jpg", "jpeg"]:
                            img = img.convert("RGB")
                        elif output_format == "ico":
                            img = img.resize((256, 256), Image.Resampling.LANCZOS)
                        elif output_format == "bmp":
                            img = img.convert("RGB")

                    exif_data = self.preserve_exif(img, path)

                    if resize < 100:
                        w, h = img.size
                        img = img.resize((int(w * resize / 100), int(h * resize / 100)), Image.Resampling.LANCZOS)

                    save_kwargs = {'format': save_format}
                    if self.preserve_metadata_checkbox.get() and exif_data and save_format == "JPEG":
                        save_kwargs['exif'] = exif_data

                    img.save(save_path, **save_kwargs)
                    output_paths.append(save_path)

                    log.append(f"✅ {os.path.basename(path)} → {os.path.basename(save_path)}")

                    progress = (i + 1) / total_files
                    self.after(0, lambda p=progress: self.conv_progress_bar.set(p))

                except Exception as e:
                    log.append(f"❌ Gagal: {os.path.basename(path)} - {e}")

            details = f"Converted {total_files} files to {output_format.upper()}"
            self.after(0, lambda: self.add_to_history("Conversion", details))

            self.after(0, lambda l=log: self.output_text.insert("end", "\n".join(l) + "\n"))
            self.after(0, lambda: self.conv_progress_bar.set(0))
            self.after(0, lambda: messagebox.showinfo("Selesai", "Konversi format selesai!"))

        self.process_images_threaded(_convert)

    def check_for_updates(self):
        """Check for updates from GitHub repository"""
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("Error", "Requests library tidak tersedia. Instal requests untuk cek update.")
            return

        try:
            # GitHub API URL for latest release
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            release_data = response.json()
            latest_version = release_data['tag_name'].lstrip('v')  # Remove 'v' prefix if present

            if latest_version > CURRENT_VERSION:
                # Show update available with two options
                self.show_update_options(latest_version, release_data)
            else:
                messagebox.showinfo("Update", f"Aplikasi sudah versi terbaru ({CURRENT_VERSION})")

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Gagal cek update: {e}")
        except KeyError:
            messagebox.showerror("Error", "Format response API tidak valid")
        except Exception as e:
            messagebox.showerror("Error", f"Error tidak terduga: {e}")

    def show_update_options(self, latest_version, release_data):
        """Show update options dialog with visit web or download manual"""
        # Create custom dialog with two options
        update_window = ctk.CTkToplevel(self)
        update_window.title("Update Tersedia")
        update_window.geometry("450x250")
        update_window.resizable(False, False)
        update_window.grab_set()

        # Center the window
        update_window.geometry("+{}+{}".format(
            self.winfo_rootx() + self.winfo_width()//2 - 225,
            self.winfo_rooty() + self.winfo_height()//2 - 125
        ))

        # Title
        title_label = ctk.CTkLabel(update_window, text="🚀 Update Tersedia!", font=("Arial", 18, "bold"))
        title_label.pack(pady=20)

        # Version info
        info_text = f"Versi terbaru: {latest_version}\nVersi saat ini: {CURRENT_VERSION}"

        info_label = ctk.CTkLabel(update_window, text=info_text, justify="center")
        info_label.pack(pady=10)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(update_window, fg_color="transparent")
        buttons_frame.pack(pady=20, fill="x", padx=20)

        def visit_web():
            update_window.destroy()
            import webbrowser
            webbrowser.open(release_data['html_url'])

        def download_manual():
            update_window.destroy()
            self.download_update_manual(latest_version, release_data)

        # Visit web button
        web_button = ctk.CTkButton(buttons_frame, text="🌐 Kunjungi Web",
                                 command=visit_web, fg_color="transparent")
        web_button.pack(side="left", padx=5, expand=True)

        # Download manual button
        download_button = ctk.CTkButton(buttons_frame, text="⬇️ Download Manual",
                                      command=download_manual, font=("Arial", 12, "bold"))
        download_button.pack(side="left", padx=5, expand=True)

    def download_update_manual(self, latest_version, release_data):
        """Download update manually using urllib"""
        try:
            # Find the download URL for the executable
            download_url = None
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.exe') or 'image-tools' in asset['name'].lower():
                    download_url = asset['browser_download_url']
                    break

            if not download_url:
                messagebox.showerror("Error", "Tidak dapat menemukan file download untuk versi terbaru.")
                return

            # Create progress window
            progress_window = ctk.CTkToplevel(self)
            progress_window.title("Downloading Update")
            progress_window.geometry("400x150")
            progress_window.resizable(False, False)
            progress_window.grab_set()

            # Center the window
            progress_window.geometry("+{}+{}".format(
                self.winfo_rootx() + self.winfo_width()//2 - 200,
                self.winfo_rooty() + self.winfo_height()//2 - 75
            ))

            # Progress label
            progress_label = ctk.CTkLabel(progress_window, text="Downloading update...")
            progress_label.pack(pady=20)

            # Progress bar
            progress_bar = ctk.CTkProgressBar(progress_window, width=300)
            progress_bar.set(0)
            progress_bar.pack(pady=10)

            def download_file():
                try:
                    import urllib.request
                    import urllib.parse

                    # Get filename from URL
                    filename = urllib.parse.unquote(download_url.split('/')[-1])
                    if not filename:
                        filename = f"image-tools-pro-v{latest_version}.exe"

                    # Download to current directory
                    local_path = os.path.join(os.getcwd(), filename)

                    def report_progress(block_num, block_size, total_size):
                        downloaded = block_num * block_size
                        if total_size > 0:
                            progress = min(downloaded / total_size, 1.0)
                            progress_bar.set(progress)
                            progress_label.configure(text=f"Downloading... {int(progress * 100)}%")

                    # Download the file
                    urllib.request.urlretrieve(download_url, local_path, reporthook=report_progress)

                    progress_bar.set(1.0)
                    progress_label.configure(text="Download selesai!")

                    # Show success message
                    progress_window.after(1000, lambda: self.show_download_complete(progress_window, local_path, filename))

                except Exception as e:
                    progress_window.destroy()
                    messagebox.showerror("Download Failed", f"Gagal download update: {str(e)}")

            # Start download in background thread
            import threading
            download_thread = threading.Thread(target=download_file, daemon=True)
            download_thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Error saat mempersiapkan download: {str(e)}")

    def show_download_complete(self, progress_window, file_path, filename):
        """Show download completion dialog"""
        progress_window.destroy()

        complete_window = ctk.CTkToplevel(self)
        complete_window.title("Download Selesai")
        complete_window.geometry("400x200")
        complete_window.resizable(False, False)
        complete_window.grab_set()

        # Center the window
        complete_window.geometry("+{}+{}".format(
            self.winfo_rootx() + self.winfo_width()//2 - 200,
            self.winfo_rooty() + self.winfo_height()//2 - 100
        ))

        # Success message
        success_label = ctk.CTkLabel(complete_window, text="✅ Download berhasil!", font=("Arial", 16, "bold"))
        success_label.pack(pady=20)

        info_label = ctk.CTkLabel(complete_window, text=f"File tersimpan sebagai:\n{filename}")
        info_label.pack(pady=10)

        def open_folder():
            complete_window.destroy()
            import subprocess
            import platform
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(file_path)])

        def close_window():
            complete_window.destroy()

        # Buttons
        button_frame = ctk.CTkFrame(complete_window, fg_color="transparent")
        button_frame.pack(pady=20, fill="x", padx=20)

        open_button = ctk.CTkButton(button_frame, text="📂 Buka Folder", command=open_folder)
        open_button.pack(side="left", padx=5, expand=True)

        close_button = ctk.CTkButton(button_frame, text="Tutup", command=close_window, fg_color="transparent")
        close_button.pack(side="left", padx=5)

    def show_qris_image(self):
        """Open Saweria donation page"""
        try:
            import webbrowser
            webbrowser.open("https://saweria.co/Habibframbudi")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka link Saweria: {e}")

    def show_help(self):
        """Show help window with application information"""
        help_text = """🖼️ Image Tools PRO - Bantuan

Aplikasi ini adalah alat komprehensif untuk mengelola dan memproses gambar dengan berbagai fitur:

📋 TAB KOMPRESI:
• Kompres gambar dengan pengaturan kualitas dan ukuran
• Mendukung format: JPG, PNG, ICO, BMP, GIF, TIFF, WEBP, SVG
• Pelestarian metadata EXIF
• Backup otomatis untuk undo

🔄 TAB KONVERSI:
• Konversi format gambar ke format lain
• Pengaturan resize independen
• Opsi pelestarian metadata

📄 TAB PDF:
• Export gambar ke PDF (satu gambar per halaman)
• Gabung beberapa file PDF menjadi satu
• Kompres file PDF untuk memperkecil ukuran
• Konversi PDF ke gambar (jika PyMuPDF tersedia)

📊 TAB RIWAYAT:
• Lihat log operasi sebelumnya
• Hapus riwayat jika diperlukan

⚙️ TAB PENGATURAN:
• Ubah tema aplikasi (System/Light/Dark)
• Ubah folder output
• Lihat pintasan keyboard

⌨️ PINTASAN KEYBOARD:
• Ctrl+O: Pilih file gambar
• Ctrl+S: Simpan pengaturan
• Ctrl+Z: Undo operasi terakhir
• F1: Tampilkan bantuan ini

📝 CATATAN:
• File output disimpan di folder 'output'
• Aplikasi mendukung multithreading untuk performa optimal
• Riwayat operasi disimpan otomatis

Dibuat oleh: Habib Frambudi
Versi: 6.0.0"""

        # Create help window
        help_window = ctk.CTkToplevel(self)
        help_window.title("Bantuan - Image Tools PRO")
        help_window.geometry("700x600")
        help_window.resizable(True, True)

        # Make it modal
        help_window.grab_set()

        # Help text area
        help_textbox = ctk.CTkTextbox(help_window, wrap="word")
        help_textbox.pack(pady=20, padx=20, fill="both", expand=True)
        help_textbox.insert("0.0", help_text)
        help_textbox.configure(state="disabled")

        # Close button
        close_button = ctk.CTkButton(help_window, text="Tutup", command=help_window.destroy)
        close_button.pack(pady=10)

if __name__ == "__main__":
    app = ImageCompressorApp()
    app.mainloop()
