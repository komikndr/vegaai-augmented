# 📚 LesLLM, Chatbot Edukasi. Guiding student to use LLM responsibly

Sebuah chatbot edukatif dengan dua jenis mode: Siswa dan Guru, 
dirancang untuk mendorong pembelajaran aktif dan mencegah 
penyalahgunaan LLM seperti ChatGPT oleh pelajar yang terlalu bergantung.

## 🧠 Tujuan Utama

Proyek ini bertujuan untuk **mengurangi ketergantungan** murid pada chatbot 
pintar tanpa proses berpikir yang mandiri. Sama seperti kalkulator yang 
bermanfaat setelah paham dasar-dasar matematika, chatbot ini berguna 
jika digunakan dengan cara yang benar.

## 👨‍🎓 Mode Siswa

Mode ini dibuat khusus untuk pelajar, dengan fitur-fitur utama:

- ✅ Bertanya soal baru ke dalam database.
- 💬 Menggunakan chatbot sebagai pemandu, bukan pemberi jawaban instan.
- ⚠️ Deteksi penyalahgunaan LLM: Jika siswa bertanya secara langsung tanpa usaha berpikir 
    terlebih dahulu, sistem akan menandai pertanyaan sebagai "LLM abuse".
- 🎯 Mendorong proses berpikir mandiri dengan panduan dari chatbot.

## 👩‍🏫 Mode Guru

Mode ini dibuat lebih sederhana dan fungsional:

- 📊 Membuat plot visualisasi data.
- 🧾 Melihat daftar siswa (nama dan ID) yang terindikasi menyalahgunakan chatbot.
- 🛠️ Membuat dan mengelola jawaban yang bisa diunggah ke database.

## 🔍 Kenapa Ini Dibuat?

Karena banyak siswa sekarang menggunakan ChatGPT tanpa berpikir. Tujuan kita adalah 
mengajarkan cara berpikir, bukan hanya cara mencari jawaban. Chatbot ini adalah alat 
bantu belajar, bukan mesin jawaban instan.

## 👨🏻‍💻 Team Member

- Micko Lesmana, mickolesmana@gmail.com


## 🐋 Installation using Docker
1. git clone https://github.com/komikndr/vegaai-augmented
2. Make volume mount for Postgre and Minio, 
    `mkdir volume_staging && cd volume_staging && mkdir postgre minio`
3. Setting up `.env` by copy-ing and changing the value inside the `.env.example`
4. `docker compose up`, you can change the expose port in app service inside `docker-compose.yaml`
5. Go to `localhost:9000` login with minio account, create bucket the same in `.env`, set it to public
4. Go to `localhost:8000`, login with the credential you put in `.env`
