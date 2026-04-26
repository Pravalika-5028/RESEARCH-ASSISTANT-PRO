# 🔍 Multi-Tab Research Assistant (AI Powered)

An AI-powered research assistant that allows users to search for any
topic and get:

🧠 AI-generated summary\
⏱️ Runtime tracking\
📄 Web results\
🖼️ Images\
🎥 YouTube videos (HD thumbnails)\
📚 Research papers

Built using Streamlit, Groq LLM, and SQLAlchemy, with a multi-tab
interface similar to ChatGPT.

------------------------------------------------------------------------

## 🚀 Features

✅ Multi-tab search (like ChatGPT)\
✅ Left sidebar history navigation\
✅ AI-generated summaries using Groq (LLaMA models)\
✅ Web search using Serper API\
✅ Research papers from arXiv\
✅ Image search integration\
✅ YouTube video results with high-quality thumbnails (HD)\
✅ Data stored in SQLite database\
✅ Runtime tracking for each search

------------------------------------------------------------------------

## 🛠️ Tech Stack

Frontend: Streamlit\
Backend: Python\
LLM: Groq (LLaMA 3 / Mixtral models)\
Database: SQLite (SQLAlchemy ORM)

APIs Used: - Serper API (Web + Image + Video Search) - arXiv API
(Research Papers) - Groq API (LLM inference)

------------------------------------------------------------------------

## 📂 Project Structure

Search Topic/ │ ├── app.py\
├── agent_system.py\
├── tools.py\
├── models.py\
├── database.py\
├── research.db\
├── .env\
├── requirements.txt\
└── README.md

------------------------------------------------------------------------

## ⚙️ Installation

### 1️⃣ Clone the repository

git clone `<your-repo-link>`{=html} cd Search Topic

### 2️⃣ Create virtual environment

python -m venv venv venv`\Scripts`{=tex}`\activate   `{=tex}\# Windows

### 3️⃣ Install dependencies

pip install -r requirements.txt

------------------------------------------------------------------------

## 🔑 Environment Variables

Create a `.env` file and add:

SERPER_API_KEY=your_serper_api_key\
GROQ_API_KEY=your_groq_api_key

------------------------------------------------------------------------

## ▶️ Run the Application

streamlit run app.py


------------------------------------------------------------------------

## 💡 How It Works

1.  User enters a topic\
2.  System fetches web results, images, videos, and papers\
3.  Results are ranked\
4.  Groq generates a summary\
5.  Data is stored in SQLite\
6.  Each search becomes a new tab

------------------------------------------------------------------------

## 🧩 UI Flow (Updated Order)

1.  Summary\
2.  Runtime\
3.  Web Results\
4.  Images\
5.  Videos\
6.  Research Papers

------------------------------------------------------------------------

## 🎥 YouTube Thumbnail Quality

Uses YouTube CDN with HD support and fallback.

------------------------------------------------------------------------

## 📊 Use Cases

-   Research topics\
-   Student learning\
-   Data exploration\
-   Trend analysis

------------------------------------------------------------------------

## 🔮 Future Enhancements

-   Delete tabs\
-   Bookmark searches\
-   Export results\
-   RAG improvements\
-   News filtering

------------------------------------------------------------------------

## 👩‍💻 Author

Pravalika

------------------------------------------------------------------------

## ⭐ Conclusion

A real-world AI research assistant using Groq, APIs, database, and
interactive UI.
