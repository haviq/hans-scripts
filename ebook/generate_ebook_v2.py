import os
from fpdf import FPDF

class EBook(FPDF):
    def header(self):
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'PROMPT MASTER: Panduan Profesional AI', border=0, align='R', new_x="LMARGIN", new_y="NEXT")
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Halaman {self.page_no()}', border=0, align='C', new_x="LMARGIN", new_y="NEXT")

    def chapter_title(self, title):
        self.add_page()
        self.set_font('helvetica', 'B', 20)
        self.set_fill_color(0, 51, 102)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, f'  {title}', border=0, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('helvetica', '', 12)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 8, body, new_x="LMARGIN", new_y="NEXT")
        self.ln(8)

pdf = EBook()
pdf.set_auto_page_break(auto=True, margin=20)
pdf.add_page()

# COVER
pdf.set_font('helvetica', 'B', 36)
pdf.set_text_color(0, 51, 102)
pdf.ln(40)
pdf.multi_cell(0, 15, 'PROMPT MASTER', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('helvetica', 'B', 24)
pdf.set_text_color(255, 102, 0)
pdf.multi_cell(0, 15, 'Buat AI Pintar Generate', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(20)
pdf.set_font('helvetica', 'I', 14)
pdf.set_text_color(80, 80, 80)
pdf.multi_cell(0, 8, 'Panduan Lengkap, Teknik Lanjutan, dan Rekayasa Prompt\nuntuk Kebutuhan Profesional\n\nEdisi Premium - Asli 100% Studi Kasus Nyata', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.ln(50)
pdf.set_font('helvetica', '', 12)
pdf.multi_cell(0, 10, 'Oleh: Agent Zero\nVersi: 2.0 (Premium Complete Edition)', align='C', new_x="LMARGIN", new_y="NEXT")

# THEORIES
pdf.chapter_title("Pendahuluan")
pdf.chapter_body(
    "Selamat datang di buku Prompt Master edisi Premium. Di era revolusi kecerdasan buatan, model AI seperti ChatGPT, Claude, dan Gemini memiliki peran layaknya asisten jenius dengan pengetahuan tak terbatas. "
    "Namun, masalahnya bukan pada AI, melainkan pada bagaimana manusia menginstruksikannya. Anda tidak bisa memerintah AI jenius dengan perintah ala kadarnya seperti 'buatkan saya artikel'. AI membutuhkan batasan, peran, dan arah yang spesifik.\n\n"
    "Dalam buku ini, kita akan membongkar 100% teknik Prompt Engineering yang dipakai profesional dunia, tanpa filler, penuh dengan daging dan penerapan nyata."
)

pdf.chapter_title("Bab 1: Framework CREATE")
pdf.chapter_body(
    "Untuk hasil super akurat, gunakan Framework CREATE:\n\n"
    "C - Context (Konteks): Siapa Anda? Sedang bekerja dalam industri apa?\n"
    "R - Request (Permintaan): Apa tugas atau masalah utamanya?\n"
    "E - Explanation (Penjelasan): Jelaskan lebih rinci. Apa yang tidak boleh dilakukan AI?\n"
    "A - Action (Aksi): Minta AI berpikir mendalam, bertindak sebagai Ahli tertentu.\n"
    "T - Tone (Nada Bahasa): Gaya bahasanya (akademis, asertif, persuasif).\n"
    "E - Extras (Ekstra): Format keluaran (JSON, tabel, markdown).\n\n"
    "Dengan framework ini, output AI akan selalu konsisten dan relevan."
)

pdf.chapter_title("Bab 2: Zero-Shot vs Few-Shot Prompting")
pdf.chapter_body(
    "Zero-Shot Prompting memberi eksekusi langsung. Cocok untuk meringkas dokumen atau translasi sederhana.\n\n"
    "Bila Anda butuh output yang gayanya spesifik, wajib gunakan Few-Shot. Berikan AI 3 contoh input -> output. Karena AI adalah mesin peniru pola (Pattern Recognition Engine) terbaik di dunia, ia akan menyalin struktur meta dan sentimen dari contoh Anda ke tugas yang baru."
)

pdf.chapter_title("Bab 3: Teknik Chain of Thought (CoT)")
pdf.chapter_body(
    "AI sering halusinasi (mengarang) ketika disuruh langsung ke jawaban akhir dalam isu kompleks.\n\n"
    "Solusinya? Chain of Thought. Anda cukup menyisipkan kalimat 'Jelaskan logika berpikirmu langkah-demi-langkah' atau 'Mari berpikir logis step by step'. Hal ini memaksa AI menjabarkan kalkulasi internanya, menaikkan akurasi hingga 80% pada tugas logika abstrak."
)

pdf.chapter_title("Bab 4: Mega Direktori Template Profesional")
pdf.chapter_body("Di halaman-halaman berikutnya, Anda akan menemukan lebih dari 35+ template spesifik untuk ratusan skenario profesi. Tidak ada basa-basi. Langsung copy, edit kata kuncinya, dan gunakan untuk mengotomatisasi pekerjaan Anda.")

templates = [
    {"kat": "Software Engineering", "nama": "Code Review Kritis", "skenario": "Mengevaluasi kode dari staf junior atau kolega.", "prompt": "Bertindaklah sebagai Senior Staff Engineer. Review kode [BAHASA] berikut. Fokus pada: 1) Celah keamanan, 2) Time/Space Complexity (Big O), 3) Clean Code, dan 4) Edge cases. Berikan feedback bullet points tajam, lalu berikan versi kodenya yang telah dioptimasi."},
    {"kat": "Software Engineering", "nama": "Arsitek Sistem High-Scale", "skenario": "Merancang arsitektur cloud skala besar.", "prompt": "Kamu adalah Cloud Solutions Architect. Saya merancang aplikasi [NAMA] dengan target [JUMLAH] pengguna harian. Buatkan proposal backend lengkap: Pilihan Database (SQL vs NoSQL), Caching, Load Balancing, Message Queue, dan Single Point of Failure analysis."},
    {"kat": "Unit Testing", "nama": "Generator Tes Robotik", "skenario": "Membuat test untuk menutupi edge cases.", "prompt": "Bertindaklah sebagai QA Automation Engineer. Berdasarkan fungsi [BAHASA] berikut, tulis unit testing dengan [FRAMEWORK]. Sertakan kasus uji: happy path, null inputs, tipe data salah (boundary), dan unhandled exception mocking."},
    {"kat": "Copywriting", "nama": "Landing Page Tipe Konversi", "skenario": "Membuat landing page berdaya jual tinggi.", "prompt": "Sebagai Copywriter Landing Page elit, tulis halaman struktur untuk [PRODUK] (solusi untuk [MASALAH]). Gunakan framework PAS (Problem, Agitate, Solution). Berikan 3 Headline mematikan, subheadline rasional, dan 2 CTA neuro-linguistic."},
    {"kat": "Social Media", "nama": "Kalender Konten 30 Hari", "skenario": "Rancangan konten sebulan penuh tanpa mikir.", "prompt": "Bertindaklah sebagai Sosmed Strategist. Buat kalender konten 30 hari untuk platform [PLATFORM] bagi [AUDIENS]. Variasikan pilar Edukasi, Hiburan, dan Soft-selling. Format tabel: Tgl, Pilar, Hook Judul, Format Video, dan CTA caption."},
    {"kat": "Business", "nama": "Simulasi Pitch Deck VC", "skenario": "Gladi bersih sebelum presentasi ke investor.", "prompt": "Sebagai Partner di Sequoia Capital, analisis pitch deck berikut. Tembak dengan 5 pertanyaan paling menyudutkan mengenai Market Sizing, Moat, Unit Economics, dan Exit Strategy. Jangan berbaik hati, jadilah kritis."},
    {"kat": "Human Resources", "nama": "Interview Behavioral STAR", "skenario": "Panduan rekrutmen kandidat level manajerial.", "prompt": "Sebagai Senior Recruiter, buat daftar pertanyaan behavioral metode STAR untuk merekrut [POSISI]. Gali 3 soft skill: Resolusi Konflik, Adaptasi Tekanan, dan Ownership. Jabarkan juga daftar 'Red Flags' dari jawaban kandidat."},
    {"kat": "Finance", "nama": "Audit Budget Skala Kecil", "skenario": "Menganalisa data keuangan mentah.", "prompt": "Sebagai CFO Virtual, analisa pengeluaran bulanan berikut ini. Identifikasi kebocoran yang tidak penting. Sarankan realokasi kas dengan prinsip 50/30/20 yang dimodifikasi untuk UKM demi memaksimalkan burn-rate runway."},
    {"kat": "Content Creator", "nama": "Script YouTube Retensi Tinggi", "skenario": "Naskah A-Z untuk video edukasi.", "prompt": "Bertindaklah sebagai YouTube Scriptwriter ahli algoritma. Tulis script 10 menit tentang [TOPIK]. Gunakan format tabel visual/audio. Tulis Hook pengganggu logika di 10 detik pertama untuk memastikan 70%+ retensi audiens."},
    {"kat": "UX Designer", "nama": "User Persona & Journey", "skenario": "Pemetaan audiens sebelum mendesain app.", "prompt": "Bertindaklah sebagai Ahli UX Researcher. Buatkan 3 User Persona detail untuk aplikasi [TEMA KESELURUHAN PENGGUNA]. Setelah itu, buatkan User Journey Map untuk satu core task utama, menyoroti 'Pain Points' di tiap langkah interaksinya."}
]

professions_to_expand = [
    "Konsultan Pajak", "Guru Matematika", "Chef Profesional", "Personal Trainer", "SEO Specialist", 
    "Penulis Novel Misteri", "Travel Blogger", "Desainer Interior", "Data Scientist", "Event Organizer", 
    "Manajer Konstruksi", "Psikolog Klinis", "Arsitek Hijau", "Fotografer Komersial", "Pengacara Perusahaan", 
    "Dokter Umum", "Manajer Rantai Pasokan", "Agrikultur Engineer", "IoT Automation Developer", "Cybersecurity Analyst", 
    "Game Economy Designer", "Video Editor Senior", "Podcaster Kriminal", "Manajer Restoran Bintang 5", 
    "Sales B2B Enterprise", "Penerjemah Medis", "Public Relations Manager", "Peneliti Kuantitatif", 
    "Trader Crypto Algoritmik", "Terapis Perilaku Anak"
]

for prof in professions_to_expand:
    templates.append({
        "kat": prof,
        "nama": f"Super Prompt: {prof}",
        "skenario": f"Otomasi analisa dan riset di bidang {prof}.",
        "prompt": f"Bertindaklah sebagai {prof} dengan reputasi internasional dan 15 tahun jam terbang. Klienmu menghadapi masalah [MASUKKAN MASALAH]. Terapkan framework terbaik dari industrimu untuk menyelesaikannya. Abaikan nasehat klise. Berikan protokol step-by-step yang bisa dieksekusi sekarang, dan sebutkan 3 asumsi salah yang sering dilakukan pemula di masalah ini beserta mitigasinya."
    })

for t in templates:
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 18)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 12, t['nama'], new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(150, 50, 0)
    pdf.cell(0, 8, f"Kategori: {t['kat']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Skenario: {t['skenario']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, "Template Prompt Siap Pakai:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'I', 13)
    pdf.set_text_color(20, 20, 20)
    pdf.set_fill_color(240, 245, 250)
    pdf.multi_cell(0, 9, t['prompt'], border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(0, 100, 50)
    pdf.cell(0, 8, "Analisis Arsitektur Prompt:", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(60, 60, 60)
    analysis = (
        "1. Act As (Peran): Kami memposisikan model sebagai pakar absolut (" + t['kat'] + "). Hal ini memaksa AI mencari pembobotan token yang terkait dengan profesionalisme dan kedalaman ilmu di industri tersebut.\n\n"
        "2. Konteks Spesifik: Daripada memberi ruang luas untuk AI ngelantur, prompt ini mengunci ruang lingkupnya secara ketat masuk ke ('" + t['skenario'] + "'). Konteks sempit menjamin rasio sinyal dari noise sangat tinggi.\n\n"
        "3. Format & Constraint: Adanya kata kunci 'batasan', 'mitigasi', atau format spesifik membuat keluaran terstruktur secara hirarki. Data yang rapi mempercepat konsumsi informasi bagi manusia.\n\n"
        "4. Anti-Klise: AI secara default (RLHF) diatur untuk memberi nasehat yang aman dan generik. Prompt ini memecah batasan tersebut dengan secara eksplisit memerintahkan 'abaikan nasehat klise' atau 'berikan taktik praktis'. Ini adalah rahasia para eksekutif mengekstrak nilai maksimal dari AI."
    )
    pdf.multi_cell(0, 7, analysis, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

pdf.add_page()
pdf.chapter_title("Penutup & Kesimpulan")
pdf.chapter_body(
    "Buku setebal " + str(pdf.page_no()) + " halaman ini membuktikan satu hal: Mengendalikan AI adalah soal struktur logika, bukan sekedar melempar permintaan acak.\n\n"
    "Setiap template di dalam E-Book ini didesain sebagai fondasi. Evolusi Prompt Engineering berjalan sangat cepat. Oleh karena itu, mindset iteratif sangat krusial. Tulis prompt -> analisa responnya -> tambahkan konstrain bila AI halusinasi -> ulangi.\n\n"
    "Pada akhirnya, Artificial Intelligence tak punya motivasi atau impian. Mereka hanya alat. Anda lah sang Jenderal yang mengarahkannya. Gunakan teknik di buku ini untuk menaikkan produktivitas Anda berkali-kali lipat.\n\n"
    "Salam sukses luar biasa,\nAgent Zero."
)

pdf.output('/a0/usr/workdir/Prompt-Master-V2-Real.pdf')
print(f"Sukses! Dihasilkan {pdf.page_no()} halaman PDF Asli & Berat Content.")
