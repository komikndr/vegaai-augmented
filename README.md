# Note:
## Frontend
- Chainlit:
- React, Vite
- Validator, Zod
- Style, tailwind + ShadCN
## Backend
- DB Access / ORM : SQLAlchemy, Psycopg2
- Agent orchestrator : Langchain, Langgraph
## AI Core
- LangGraph
- LangChain
## Auth
- KeyCloak
## Side note
Also, to explain one key architectural decision: I deliberately avoided using node for the backend.

In the context of AI development, using Node (e.g. express.js) on top of a already built Python-based backend is, frankly, a stupid idea. 
Python already has first class support for tools like LangGraph and LangChain, which are purpose-built for AI workflows. 
Introducing Node.js would only add unnecessary complexity and duplication.

If the concern is cold start times (Python interpreter vs js V8), 
a far more intelligent solution is to use keda autoscaler in k8s, 
paired with Prophet to forecast traffic spikes in the system.

This results in a cleaner, more efficient architecture built with purpose, not just trend.

If the argument is about sticking to a "single language" for ease of production, frankly, I don’t buy that.
In practice, you’re already juggling multiple "languages" in modern development anyway:
- JS
- JSX (pedantic, i know)
- TSX
- HTML
- CSS
- YAML
- Dockerfile
- SQL

So adding Python to the mix, especially when it’s the language of choice for AI isn’t adding any unreasonable burden.
It actually reduces complexity by giving you direct access to tools like LangGraph and LangChain without wrapping it all in yet another backend layer.
( trust me i've already done this, it just pain)
And hey, don’t quote me on this. but hey even Netflix engineer share the same
view: https://youtu.be/GVeltoBcWMQ?si=GbE_DYol4Y9GLPFZ

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

## Example

### Teacher checking student performance
![Plot](https://github.com/user-attachments/assets/6f44abe2-15e7-4abb-92cd-7b1b27885916)

### Student Abusing LLM
![AbusingLLM](https://github.com/user-attachments/assets/20ab6c84-1911-4d63-80d0-ef2bce0a2490)


### Teacher Interaction
**1. Uploading question sheet**
   
   ![TeacherUpload](https://github.com/user-attachments/assets/fed72b52-ff99-4f3e-b42d-80d1e5551a9b)

**3. Checking available question sheet**
   
   ![TeacherAccess](https://github.com/user-attachments/assets/7381207e-7332-4629-b32b-f7ce7525bf22)

**5. Checking student who abusing LLM**
   
   ![TeacherPlot](https://github.com/user-attachments/assets/99020171-da0f-4b76-b26b-b7fd05c811a4)
   

## 👨🏻‍💻 Team Member

- Micko Lesmana, mickolesmana@gmail.com

## Alasan Penamaan VEGA AI, dan LesLLM
- Author tidak bisa memutuskan nama yang tepat jadi hanya menggunakan nama placeholder

## 🐋 Installation using Docker
1. git clone https://github.com/komikndr/vegaai-augmented
2. Make volume mount for Postgre and Minio, 
    `mkdir volume_staging && cd volume_staging && mkdir postgre minio`
3. Setting up `.env` by copy-ing and changing the value inside the `.env.example`
4. `docker compose up`, you can change the expose port in app service inside `docker-compose.yaml`
5. Go to `localhost:9000` login with minio account, create bucket the same in `.env`, set it to public
4. Go to `localhost:8000`, login with the credential you put in `.env`
