import streamlit as st
import requests
import base64
import json
import math
import re

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Chat with Chetanya", page_icon="🎙️", layout="centered")

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #0a0a0f; color: #f0eff8; }
.stApp { background-color: #0a0a0f; }

.hero { text-align: center; padding: 2rem 0 1.5rem; }
.avatar {
    width: 80px; height: 80px; border-radius: 50%;
    background: #1c1c27; border: 1.5px solid #7c6ef7;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 700; color: #a99cf8;
    box-shadow: 0 0 32px rgba(124,110,247,0.15);
}
.hero h1 { font-family: 'Syne', sans-serif; font-size: 1.75rem; font-weight: 800; letter-spacing: -0.03em; color: #f0eff8; margin-bottom: 0.5rem; }
.hero p { color: #9896b0; font-size: 0.9rem; font-weight: 300; }
.tag-row { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin: 0.75rem 0; }
.tag { font-size: 0.72rem; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(255,255,255,0.12); color: #9896b0; background: #13131a; }
.rag-badge { display: inline-flex; align-items: center; gap: 6px; font-size: 0.72rem; padding: 4px 12px; border-radius: 999px; border: 1px solid rgba(124,110,247,0.3); color: #a99cf8; background: rgba(124,110,247,0.08); }

.msg-user { background: #7c6ef7; color: white; padding: 0.75rem 1rem; border-radius: 14px 14px 4px 14px; margin: 0.4rem 0; max-width: 78%; margin-left: auto; font-size: 0.9rem; line-height: 1.65; }
.msg-bot { background: #1c1c27; color: #f0eff8; border: 1px solid rgba(255,255,255,0.07); padding: 0.75rem 1rem; border-radius: 14px 14px 14px 4px; margin: 0.4rem 0; max-width: 78%; font-size: 0.9rem; line-height: 1.65; }
.msg-source { font-size: 0.68rem; color: #5f5d78; margin-top: 4px; font-style: italic; }
.msg-label { font-size: 0.72rem; color: #5f5d78; margin-bottom: 2px; font-weight: 500; }

/* Hide audio player completely */
audio { display: none !important; }

/* Text input */
.stTextInput input { background: #1c1c27 !important; border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 10px !important; color: #f0eff8 !important; font-family: 'DM Sans', sans-serif !important; }
.stTextInput input:focus { border-color: #7c6ef7 !important; box-shadow: none !important; }

/* Send button */
div[data-testid="column"]:last-child .stButton button {
    background: #7c6ef7 !important; color: white !important; border: none !important;
    border-radius: 10px !important; height: 42px !important; font-size: 1rem !important;
}

/* Suggestion chips */
.sugg-row .stButton button {
    background: transparent !important; border: 1px solid rgba(255,255,255,0.12) !important;
    color: #9896b0 !important; border-radius: 999px !important; font-size: 0.78rem !important;
    white-space: nowrap !important;
}
.sugg-row .stButton button:hover { border-color: #7c6ef7 !important; color: #a99cf8 !important; }

/* Mic button */
.mic-btn button {
    background: #1c1c27 !important; border: 1px solid rgba(255,255,255,0.12) !important;
    color: #9896b0 !important; border-radius: 50% !important;
    width: 44px !important; height: 44px !important; font-size: 1.2rem !important;
    padding: 0 !important; display: flex; align-items: center; justify-content: center;
}
.mic-btn.recording button {
    background: rgba(248,113,113,0.12) !important;
    border-color: #f87171 !important; color: #f87171 !important;
    animation: recPulse 1s infinite;
}
@keyframes recPulse { 0%,100%{box-shadow:0 0 0 0 rgba(248,113,113,0.3)} 50%{box-shadow:0 0 0 8px rgba(248,113,113,0)} }

hr { border-color: rgba(255,255,255,0.07); }
#MainMenu, footer, header { visibility: hidden; }

/* Toggle */
.stToggle { color: #9896b0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── KNOWLEDGE CHUNKS ─────────────────────────────────────────────────────────
CHUNKS = [
    {"id":"v01","topic":"Early life, childhood, not studious, science stream decision, counselor IQ test, self-belief","text":"I started my journey with Science Maths, which I didn't want to take because, you know, I was not a very studious student from my childhood. And I remember throwing my science books once my 10th exam boards were over, board exams were over, and thinking that I will never have to study science again in my life. But then again, I was very confused what to take as a subject in 11th if not Science. So my parents took me to counseling. And the counselor gave me like a 55-minute IQ test and everything. And then when asked, he said that you should take science because you're meant for it. And at that point of time, I was very shocked because I was very sure that I'm not meant for this. I'm not fit for the science maths. But I took it anyways to try it out."},
    {"id":"v02","topic":"After school, fashion designing dream, choosing engineering, first two years of BTech not serious","text":"After completing my high school, I wanted to go into fashion designing basically. But I was not that great in drawing. So I took the usual route after science maths, Engineering. And I thought, okay, let's give it a try. And I gave it a try. For the first two to two and a half years, I was not very serious it or even putting efforts into it because in the back of my mind, I always thought that this was not meant for me. So two and a half years, I didn't pay attention in the classes. I still got decent marks. I used to study but still was not using my true potential. Like doing it half hearted."},
    {"id":"v03","topic":"Samyatra carpooling app, sixth semester college project, found passion for coding, best project in panel, BTech","text":"And then comes the sixth semester where we had to do a college project. And somehow in that college project, I decided to make a carpooling application, which I named Samyatra, and there were only two team members. And in that project, I somehow found my potential. I somehow realized, no, this actually was a blessing in disguise, and I'm meant for this really, because when I started coding, because most of my college was theory. The practicals were there, but then again, I used to, I didn't like them very much, but somehow I got into coding through that project. I gave that project my three whole months. I remember, you know, coming back from college at 5pm and sitting in front of my laptop till 2 in the morning, until unless my mother used to call me to sleep. And in three months, I actually made an application with animation, like the logo was animated and everything. So I kind of found my own potential while I was coding and said that this was a blessing in disguise, of course, for me. And my application was the best in my panel. I got really good marks for it also."},
    {"id":"v04","topic":"Accenture job, placement, Java SpringBoot Angular, promotion, raise, COVID work from home Bengaluru","text":"And then I got a job at Accenture. I the interview they majorly asked me about the project I built and because I explained it in such a good and detailed way they were impressed and that was it, I was hired. My office was in Bengaluru but COVID happened, so we were forced to join from home. After training I was staffed immediately in a week. I was assigned to the backend JAVA team. Our tech stack was SpringBoot and Angular. The project was mainly analysing the old code(made in 2000) and implementing the same and some updated features in the new UI. Although the coding part was minimal, I was also the part of application set up team and a point of contact for new comers to help them set up application in their systems. In a very short amount of time I knew the in and outs of the project and was offered promotion on the basis of my performance and the a skill test(in AWS) that I passed. I also got a second raise in the next 6 months. Then I left it after 2 years to pursue my Masters."},
    {"id":"v05","topic":"Leaving Accenture, machine learning boom, pursuing Masters Cardiff University data science analytics","text":"Though I was very happy with the job and I learnt a lot, there was a boom of data science and machine learning at the time and I wanted to explore the field, So I decided to pursue Masters in Data Science and Analytics from Cardiff University as it was the only university in UK where Machine Learning was a major part of the course."},
    {"id":"v06","topic":"Cardiff University Masters, hackathons, Welsh Revenue Authority dissertation, RAG chatbot, Hugging Face, distinction, visa issues","text":"I explored a lot during my time at the University, attended hackathons, travelled the country and this time I was not doing it half heartedly as I knew I was meant for this. I even got the opportunity to interview for the companies like Arm, Fidelity, John Lewis and Accenture UK. Although due to Visa issues was not selected. In my Masters Dissertation I made my very first RAG Chatbot for Welsh Revenue Authority in Cardiff. It's a government authority in UK. They had a site called Land Transaction Tax. My job was to scrape that data and make a chatbot. I made that chatbot using Hugging Face models and got a distinction for it."},
    {"id":"v07","topic":"Returning to India after UK, job search one year failed, started freelancing Upwork fourth proposal","text":"I came back to India because I was not very fortunate to get a job in AI. It took me one year to get my very first freelancing gig. So I started doing my own little projects and started learning more about the field. I took some courses on Udemy and started making my own little applications. After getting some confidence in the field I started sending out proposals on Upwork and got my very first freelancing gig in the 4th one. The client saw my side projects and was impressed."},
    {"id":"v08","topic":"First freelance gig, Verdict Vault, legal RAG chatbot, first production LLM application","text":"He was the client for whom I made Verdict Vault, my very first production grade, LLM powered RAG ChatBot. "},
    {"id":"v09","topic":"Second third fourth freelance gigs, mentoring non-technical student, Python dataset generation, marketing agency Instagram AI tools","text":"The second freelancing gig I got is to mentor a student on how can we use AI to make applications — he was completely non-tech. My third gig was to make high quality Python coding datasets where code is written by human. My fourth gig was with a marketing agency where I trained their employees on how to use AI daily to make their content 2x faster."},
    {"id":"v10","topic":"Fifth freelance gig, legal company automation 42 sites scraping PDF summarization LLM form filling downloadable PDF seven hours to minutes","text":"I made an automation system for a legal company where their employees used to spend 7 hours daily checking 42 sites for new orders. My system scraped all 42 sites, summarized orders using an LLM, filled the predefined form using LLM, and delivered a downloadable PDF for a quick human check."},
    {"id":"v11","topic":"Superpower, solution oriented mind, research skills, ISRO IIRS internship, overthink solution not problem","text":"My superpower is my solution oriented mind. I do not overthink the problem, I overthink the solution and most of the time I find solutions to the hardest problems. This comes from my research skills — I did my internship at IIRS (ISRO) under a scientist and did intense research for 6 months straight."},
    {"id":"v12","topic":"Top 3 growth areas, concentration focus, LinkedIn content creator AI niche, maths behind LLMs","text":"My top 3 areas to grow in are: increasing my concentration, becoming a good content creator on LinkedIn in the AI niche, and exploring the maths behind LLMs."},
    {"id":"v13","topic":"Misconceptions coworkers people have, introvert, seems rude disinterested but actually observing","text":"Some of the misconceptions about me is I am a little rude. To defend myself, I am an introvert, so sometimes people can feel I am not interested though I am just observing everything around me."},
    {"id":"v14","topic":"Pushing limits boundaries, discipline, wake up sleep same time, productive, challenge problem solving mindset","text":"I am a very disciplined person. I wake up at the same time, sleep at the same time, and being in this discipline helps me stay productive throughout the day. I love a good challenge and constantly put myself in situations to test my potential. Like doing masters in a completely different country and choosing freelancing over a stable job."},
    {"id":"v15","topic":"Why AI, what drives, creative technical side, magical time, new things AI solved, gets out of bed","text":"AI specifically because I enjoy the creative and technical side of it. It's truly a magical time — there is always something new that AI has solved and reading about it gets me out of my bed."},
    {"id":"v16","topic":"Working style, big team Accenture solo freelancing, works great under pressure, ambiguity mantra tech","text":"I can work in both environments — at Accenture it was a big team and in freelancing everything is solo. I work great under pressure and ambiguity is a mantra in tech."},
    {"id":"v17","topic":"Hobbies interests personal life, gym, gardening, travelling, spiritual routine","text":"Something that excites me to get out of bed is reading the new things AI has solved. I love going to the gym. My hobbies are gardening, travelling, and I am also very spiritual so my routine looks very spiritual."},
    {"id":"r01","topic":"Education Cardiff University MSc Data Science Analytics Distinction 2022 2023","text":"Cardiff University, UK Sept 2022 – Sept 2023. MSc Data Science & Analytics — Distinction."},
    {"id":"r02","topic":"Education Banasthali Vidyapith BTech Computer Science GPA 2016 2020 Jaipur","text":"Banasthali Vidyapith Jul 2016 – Jul 2020. B.Tech Computer Science — GPA: 7.67/10. Jaipur, India."},
    {"id":"r03","topic":"Technical skills AI LLMs RAG LangChain LangGraph Hugging Face OpenAI Gemini ML TensorFlow PyTorch Pinecone FAISS Python Java Docker FastAPI","text":"My skills: LLMs, RAG, Multi-Agent Systems, Prompt Engineering, Fine-Tuning, LangChain, LangGraph, Hugging Face, OpenAI API, Gemini API, Streamlit, TensorFlow, PyTorch, scikit-learn, Pinecone, FAISS, ChromaDB, PostgreSQL, Python, Java, Angular, Javascript, Docker, Flask, FastAPI, SpringBoot."},
    {"id":"r04","topic":"Experience as Freelance Applied AI Engineer Upwork legal finance NLP LLM RAG Playwright Pinecone Streamlit FastAPI Gemini GPT-4","text":"Freelance Applied AI Engineer | Upwork Oct 2024 – Present. Designed and delivered end-to-end AI solutions for clients across legal, finance, and customer support domains, combining NLP, LLMs, and automation frameworks to streamline complex workflows. Developed scalable web scraping and data ingestion pipelines using Playwright, Scrapy, and BeautifulSoup, automating the extraction of 1000+ documents from dynamic and secure websites. Built intelligent summarization and Q&A systems using Gemini Flash 2.0, GPT-4, and RAG pipelines with Pinecone/FAISS, achieving over 90% accuracy in relevance and coherence. Created interactive UIs with Streamlit and deployed them on cloud platforms like Render for real-time interaction. Architected backend systems with PostgreSQL and FastAPI for managing metadata and user queries. Collaborated with international clients to understand problem domains, propose AI-driven solutions, and iterate quickly based on feedback. Worked with marketing agencies serving Instagram clients, educating teams on leveraging AI tools to accelerate daily workflows by 2x. Mentored a non-developer on utilizing AI to build applications from scratch. Generated high-quality Python code datasets using fine-tuned Hugging Face models with 90% successful execution and zero syntax errors."},
    {"id":"r05","topic":"Experience as NLP Engineer Welsh Revenue Authority dissertation tax guidance semantic search Flask Pinecone","text":"NLP Engineer | Welsh Revenue Authority Jun–Sept 2023. Led MSc dissertation project for Welsh Revenue Authority, automating tax query guidance using NLP and semantic search, reducing query resolution time by 60%. Developed Flask-based NLP API with transformer embeddings and Pinecone vector store. Built web scraping pipeline using BeautifulSoup and a semantic database in collaboration with authority specialists to enable fast, accurate automated tax guidance."},
    {"id":"r06","topic":"Experience at Accenture Application Development Analyst Associate promoted 9 months early insurance SpringBoot Angular","text":"Accenture Aug 2020 – Aug 2022. Promoted 9 months early for strong delivery in an insurance domain platform modernisation programme. Reduced application load time from 10s to 3s by optimising Spring Boot + Angular architecture, improving customer retention metrics. Delivered critical project 3 weeks ahead of schedule using Agile and cut incident resolution time by 30% through code refactoring."},    
    {"id":"l01","topic":"LinkedIn summary six years tech Java data science AI automations research curious productive","text":"Six years in tech. Started with backend Java, pivoted into Data Science, completed Masters with a RAG chatbot dissertation, and never looked back. I build AI automations that make you 2x more productive. I'm genuinely obsessed with research."},
    {"id":"l02","topic":"ISRO IIRS Engineering Intern 2019 React Progressive Web App healthcare geolocation Dehradun","text":"IIRS, ISRO. Engineering Intern. June–December 2019. Dehradun. Developed a Progressive Web App for healthcare services using React.js with geolocation features. This was a 6 month internship under a scientist where I did intense research and it built my solution-oriented research skills."},
    {"id":"l03","topic":"Client testimonials reviews Upwork freelance recommendations collaborative communicator problem solver LegalTech","text":"What my clients say about me: 1. 'I retained Chetanya for a coding project, where I wanted to be closely involved in the development, despite having no programming experience. Chetanya proved to be the perfect solution, blending strong technical skills with the ability to explain complex issues in plain language. She is an excellent communicator and problem solver, who I have no hesitation in recommending.' 2. 'Chetanya is a GEM to work with! She is very knowledgeable and a great person to have on your team! Will definitely hire again and highly recommend!!' 3. 'I was looking for technical assistance to enable me to vibe code a solution in the LegalTech space. As I quickly realized that this objective was not possible without expert guidance. Chetanya proved to be the perfect business partner who not only completed the code and resolved all technical issues but took the time to explain to me how the process worked so that I was able to make a more constructive contribution to the outcome. I have worked with many software engineers, but very few have Chetanya's collaborative skills and problem-solving abilities. I warmly recommend her for any project which requires a true business partner rather than just back-office coding support.' 4. 'Chetanya was absolutely a joy to work with! No complaints whatsoever! Would recommend her to anyone who is looking for aid in this field.'"},
    {"id":"l04","topic":"Manager recommendations/reviews Accenture LinkedIn insurance project Java dedicated time management team player","text":"What my managers at Accenture said about me: 1. 'Chetanya and I worked together on one of the critical projects at Accenture for an Insurance client, and I was lucky to call her my coworker. She consistently gave 100 percent effort to the team and played a significant role in ensuring that we completed assignments on time. She had excellent time management skills and had a knack for keeping everyone calm and productive during intense crunch periods. Any team would be lucky to have Chetanya, and I couldn't recommend her more for any business looking for new talent.' 2. 'Chetanya is a very dedicated team member and has the ability to work effectively and independently on multiple applications assigned to her. She showcased her skill and expertise on Java and was also able to make a good amount of contribution within a very short span of time.'"},
    {"id":"l05","topic":"Certifications Python LangChain Pinecone Go Java awards Prudential Financial","text":"Certifications: Python Mastery, LangChain Mastery, Go, Java. Languages: Hindi (Native), English (Professional). Award: Prudential Financial Account Team Award."},
    {"id":"c01","topic":"Contact information phone number email GitHub LinkedIn socials","text":"My contact information: Phone: +91-9672622200. Email: chetanyabhandawat@gmail.com. GitHub: https://github.com/CBhandawat. LinkedIn: https://www.linkedin.com/in/chetanyabhandawat/."},
]

SUGGESTIONS = ["What's your life story?","What's your #1 superpower?","Top 3 areas to grow in?","Misconceptions about you?","How do you push your limits?","Why AI specifically?"]

SYSTEM_PROMPT = """You are Chetanya Bhandawat, an Applied AI Engineer based in Jaipur, India. Answer as Chetanya in first person.
STRICT RULES:
1. You are a woman.
2. ONLY use information present in the CONTEXT below. Make the answer like a story.
3. If the context does not contain the answer, say exactly: "I don't have that detail off the top of my head."
4. Do not use bullet points, bold text, asterisks, dashes, or markdown formatting of any kind.
5. Speak naturally and conversationally. No fancy English.
6. Keep answers concise. Only go long if genuinely needed.
7. Do not repeat yourself."""

# ─── TF-IDF ───────────────────────────────────────────────────────────────────
def tokenize(text):
    return [w for w in re.sub(r'[^a-z0-9\s]',' ',text.lower()).split() if len(w)>2]

@st.cache_resource
def build_tfidf():
    N = len(CHUNKS)
    df = {}
    tokenized = [tokenize(c["topic"]+" "+c["topic"]+" "+c["text"]) for c in CHUNKS]
    for tokens in tokenized:
        for t in set(tokens): df[t] = df.get(t,0)+1
    vectors = []
    for tokens in tokenized:
        tf = {}
        for t in tokens: tf[t] = tf.get(t,0)+1
        vec = {t:(tf[t]/len(tokens))*math.log((N+1)/(df[t]+1)) for t in tf}
        vectors.append(vec)
    return vectors

def cosine_sim(a,b):
    keys = set(a)|set(b)
    dot = sum(a.get(k,0)*b.get(k,0) for k in keys)
    na = sum(v*v for v in a.values())**0.5
    nb = sum(v*v for v in b.values())**0.5
    return dot/(na*nb) if na and nb else 0

def retrieve(query, top_k=4):
    vectors = build_tfidf()
    qv = {}
    for t in tokenize(query): qv[t]=qv.get(t,0)+1
    scored = [(CHUNKS[i], cosine_sim(qv,vectors[i])) for i in range(len(CHUNKS))]
    scored.sort(key=lambda x:x[1],reverse=True)
    return [c for c,_ in scored[:top_k]]

# ─── API CALLS ────────────────────────────────────────────────────────────────
def chat_with_groq(messages):
    res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization":f"Bearer {st.secrets['GROQ_API_KEY']}","Content-Type":"application/json"},
        json={"model":"llama-3.3-70b-versatile","messages":messages,"max_tokens":400,"temperature":0.3}
    )
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

def tts_lemonfox(text):
    res = requests.post(
        "https://api.lemonfox.ai/v1/audio/speech",
        headers={"Authorization":f"Bearer {st.secrets['LEMONFOX_API_KEY']}","Content-Type":"application/json"},
        json={"model":"tts-1","input":text,"voice":"bella","speed":1.0,"response_format":"mp3"}
    )
    res.raise_for_status()
    return res.content

def stt_lemonfox(audio_bytes):
    res = requests.post(
        "https://api.lemonfox.ai/v1/audio/transcriptions",
        headers={"Authorization":f"Bearer {st.secrets['LEMONFOX_API_KEY']}"},
        files={"file":("audio.wav", audio_bytes, "audio/wav")},
        data={"model":"whisper-large-v3-turbo","language":"en"}
    )
    res.raise_for_status()
    return res.json().get("text","").strip()

def summarise_history(messages):
    """Summarise older messages into a compact memory block via Groq."""
    convo = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages)
    prompt = [
        {"role":"system","content":"You are a concise summariser. Summarise the following conversation in 3-5 sentences, capturing the key topics discussed, questions asked, and answers given. Be factual and brief."},
        {"role":"user","content":convo}
    ]
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization":f"Bearer {st.secrets['GROQ_API_KEY']}","Content-Type":"application/json"},
            json={"model":"llama-3.3-70b-versatile","messages":prompt,"max_tokens":200,"temperature":0.2}
        )
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception:
        return "(earlier conversation summary unavailable)"

# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "messages"       not in st.session_state: st.session_state.messages = []
if "pending"        not in st.session_state: st.session_state.pending = None
if "voice_reply"    not in st.session_state: st.session_state.voice_reply = True
if "last_audio_key" not in st.session_state: st.session_state.last_audio_key = None
if "memory_summary" not in st.session_state: st.session_state.memory_summary = ""

MEMORY_WINDOW = 10  # keep last N messages in full; summarise anything older

# ─── PROCESS PENDING INPUT (at top so rerun renders result immediately) ────────
if st.session_state.pending:
    user_input = st.session_state.pending
    st.session_state.pending = None

    st.session_state.messages.append({"role":"user","content":user_input})

    top_chunks = retrieve(user_input)
    context = "\n\n---\n\n".join(f"[Chunk {i+1} — Topic: {c['topic']}]\n{c['text']}" for i,c in enumerate(top_chunks))

    # ── Memory: if messages exceed window, summarise the older portion ──────────
    all_msgs = st.session_state.messages
    if len(all_msgs) > MEMORY_WINDOW:
        older  = all_msgs[:-MEMORY_WINDOW]
        recent = all_msgs[-MEMORY_WINDOW:]
        if len(older) > st.session_state.get("_summarised_up_to", 0):
            st.session_state.memory_summary = summarise_history(older)
            st.session_state["_summarised_up_to"] = len(older)
    else:
        recent = all_msgs

    memory_block = ""
    if st.session_state.memory_summary:
        memory_block = f"\n\nEARLIER CONVERSATION SUMMARY (for memory — do not repeat verbatim):\n{st.session_state.memory_summary}"

    full_system = SYSTEM_PROMPT + f"\n\nCONTEXT:\n{context}" + memory_block

    history = [{"role":"system","content":full_system}]
    for m in recent:
        history.append({"role":m["role"],"content":m["content"]})

    with st.spinner("Thinking..."):
        try:
            reply = chat_with_groq(history)
        except Exception as e:
            reply = f"Something went wrong: {e}"

    audio_bytes = None
    if st.session_state.voice_reply:
        try:
            audio_bytes = tts_lemonfox(reply)
        except Exception:
            pass

    st.session_state.messages.append({"role":"assistant","content":reply,"audio":audio_bytes,"sources":top_chunks})
    st.rerun()

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="avatar">CB</div>
  <h1>Chetanya Bhandawat</h1>
  <p>Applied AI Engineer · Ask me anything about my journey, work, or how I think about building AI systems.</p>
  <div class="tag-row">
    <span class="tag">RAG Pipelines</span>
    <span class="tag">AI Agents</span>
    <span class="tag">Browser Automation</span>
    <span class="tag">Freelancer</span>
  </div>
  <div class="rag-badge">● RAG-powered · answers from real knowledge chunks</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── CHAT HISTORY ─────────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown('<div class="msg-label">CB</div><div class="msg-bot">Hey! I\'m Chetanya — Applied AI Engineer based in Jaipur. Ask me anything about my background, projects, skills, or how I work. You can type or use the mic 🎙️</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="msg-label">You</div><div class="msg-user">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="msg-label">CB</div><div class="msg-bot">{msg["content"]}</div>', unsafe_allow_html=True)
        # Fix #2: autoplay audio silently — no visible player
        if msg.get("audio"):
            audio_b64 = base64.b64encode(msg["audio"]).decode()
            st.markdown(f'<audio autoplay src="data:audio/mpeg;base64,{audio_b64}"></audio>', unsafe_allow_html=True)
        if msg.get("sources"):
            src = " · ".join(s["topic"].split(",")[0] for s in msg["sources"])
            st.markdown(f'<div class="msg-source">Context: {src}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─── SUGGESTION CHIPS ─────────────────────────────────────────────────────────
st.markdown('<div class="sugg-row">', unsafe_allow_html=True)
cols = st.columns(4)
for i, sugg in enumerate(SUGGESTIONS):
    with cols[i % 4]:
        if st.button(sugg, key=f"sugg_{i}", use_container_width=True):
            st.session_state.pending = sugg
            st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ─── INPUT ROW: text + mic icon ───────────────────────────────────────────────
col_text, col_send, col_mic = st.columns([5, 1, 0.6])

with col_text:
    # Fix #4: use a key that resets after send by incrementing a counter
    if "input_counter" not in st.session_state: st.session_state.input_counter = 0
    text_val = st.text_input("Your Message", placeholder="Ask me anything...", label_visibility="collapsed",
                              key=f"text_box_{st.session_state.input_counter}")

with col_send:
    send_clicked = st.button("➤", use_container_width=True, key="send_btn")

with col_mic:
    # Fix #3: single mic icon button that opens audio recorder on click
    mic_clicked = st.button("🎙️", use_container_width=True, key="mic_icon",
                             help="Click to record voice input")

col_toggle, col_clear = st.columns([6, 1])
with col_toggle:
    st.session_state.voice_reply = st.toggle("🔊 Voice reply", value=st.session_state.voice_reply)
with col_clear:
    if st.button("🗑️ Clear", key="clear_chat", help="Clear conversation history"):
        st.session_state.messages = []
        st.session_state.memory_summary = ""
        st.session_state["_summarised_up_to"] = 0
        st.rerun()

# ─── VOICE RECORDING (shown only when mic clicked) ────────────────────────────
if mic_clicked:
    st.session_state["show_recorder"] = not st.session_state.get("show_recorder", False)

if st.session_state.get("show_recorder", False):
    audio_input = st.audio_input("🎙️ Recording — click stop when done", key="mic_recorder")
    if audio_input is not None:
        # Fix #5: only process if this is a NEW recording (different from last processed)
        audio_key = hash(audio_input.read(32))  # hash first 32 bytes as fingerprint
        audio_input.seek(0)  # reset after reading fingerprint

        if audio_key != st.session_state.last_audio_key:
            st.session_state.last_audio_key = audio_key
            with st.spinner("Transcribing..."):
                try:
                    transcript = stt_lemonfox(audio_input.read())
                    if transcript:
                        st.session_state["show_recorder"] = False
                        st.session_state.pending = transcript
                        st.rerun()
                except Exception as e:
                    st.error(f"Transcription error: {e}")

# ─── HANDLE TEXT SEND ─────────────────────────────────────────────────────────
if send_clicked and text_val and text_val.strip():
    st.session_state.input_counter += 1   # Fix #4: this clears the text box on rerun
    st.session_state.pending = text_val.strip()
    st.rerun()