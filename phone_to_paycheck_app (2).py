import streamlit as st
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

ACCESS_CODE = "PHONE2026"
PRIMARY = HexColor("#1A365D")
ACCENT = HexColor("#ED8936")
DARK = HexColor("#2D3748")
MUTED = HexColor("#718096")

st.set_page_config(page_title="Phone to Paycheck", page_icon="📱", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.stButton>button {width:100%;border-radius:8px;height:3em;font-weight:600;}
.plan-box{background:#f8fafc;border-left:5px solid #ED8936;padding:1.1rem 1.3rem;border-radius:0 8px 8px 0;margin:1rem 0;}
.step-box{background:#edf2f7;padding:0.85rem 1.1rem;border-radius:8px;margin-bottom:0.55rem;}
h1,h2,h3{color:#1A365D;}
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "plan" not in st.session_state:
    st.session_state.plan = None

def generate_blueprint(answers):
    time = answers.get("time", "")
    preference = answers.get("preference", "")
    skills = answers.get("skills", [])
    goal = answers.get("goal", "")
    niche = (answers.get("niche") or "").strip() or "general lifestyle & practical tips"

    paths = {"freelance": 0, "content": 0, "digital": 0, "ugc": 0}

    if preference == "Talking on camera":
        paths["content"] += 3
        paths["ugc"] += 3
    elif preference == "Writing & designing":
        paths["digital"] += 3
        paths["freelance"] += 2
    elif preference == "Helping people with tasks":
        paths["freelance"] += 4
    elif preference == "Creating something once and selling repeatedly":
        paths["digital"] += 4
    else:
        paths["freelance"] += 1
        paths["content"] += 1
        paths["digital"] += 1

    if "Comfort talking on video" in skills:
        paths["content"] += 2
        paths["ugc"] += 2
    if "Writing skill" in skills:
        paths["freelance"] += 2
        paths["digital"] += 1
    if "Design / Canva experience" in skills:
        paths["digital"] += 2
        paths["freelance"] += 1
    if "Social media following" in skills:
        paths["content"] += 2
        paths["digital"] += 1

    if time in ["15–30 minutes", "30–60 minutes"]:
        paths["digital"] += 2
        paths["freelance"] += 1
    else:
        paths["content"] += 1
        paths["ugc"] += 1

    if "First $100" in goal:
        paths["freelance"] += 2
    if "$1,000+" in goal or "Replace a job" in goal:
        paths["content"] += 1
        paths["digital"] += 1

    sorted_paths = sorted(paths.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_paths[0][0]
    secondary = sorted_paths[1][0] if sorted_paths[1][1] > 0 else None

    name_map = {
        "freelance": "Freelance Services (Fiverr-first)",
        "content": "Short-Form Content Creation",
        "digital": "Digital Products (Canva + Storefront)",
        "ugc": "UGC Creator (Brand Videos)"
    }
    primary_name = name_map[primary]
    secondary_name = name_map.get(secondary)

    if primary == "freelance":
        why = "You prefer helping people with concrete tasks or want the fastest path to first cash. Fiverr lets you package simple services and get paying clients without needing an audience first."
        tools = ["Fiverr app – create seller account", "Canva – make portfolio samples & gig images", "Gmail – clean professional email", "Google Drive – store samples & deliveries"]
        day1_7 = [
            "Day 1: Download Fiverr + Canva. Create a clean profile with a clear photo and short bio.",
            "Day 2: Design 3 strong sample pieces in Canva related to your niche.",
            f"Day 3: Create your first highly specific gig (example: “I will write 10 Instagram captions for {niche} brands”).",
            "Day 4: Price the basic package $12–25. Publish and share the gig link in 3–5 relevant Facebook groups or Reddit threads.",
            "Day 5: Improve the gig with better images or add a second related gig.",
            "Day 6–7: Promote 20–30 min every day. Reply to every message within one hour."
        ]
        days_8_30 = [
            "Days 8–14: Deliver any orders early and ask for reviews. Keep promoting daily.",
            "Days 15–21: Raise prices slightly once you have 3–5 five-star reviews. Add a mid-tier package.",
            "Days 22–30: Create a simple portfolio page. Start offering the same services via Stripe Payment Links for direct clients."
        ]
        money = "Fiverr handles all payments (they take ~20%). Once you have reviews, raise your prices. For higher-margin direct clients later, create free Stripe Payment Links."
        reels = "Film short 15–30 second videos showing your samples or “how I help clients”. Post on TikTok/Reels with a link to your Fiverr profile in bio."
        advertise = "Free first: Share your gig in niche Facebook groups, Reddit (r/forhire + niche subs), and your own socials. Later: $5–10/day TikTok or Instagram ads once you have social proof."
        ideas = [
            f"Write 10–15 social media captions for {niche} accounts",
            f"Design simple Canva templates for {niche}",
            f"Create product description packages for {niche} sellers",
            "Offer basic virtual assistant tasks (email replies, research, scheduling)",
            "Make short promo videos or talking-head scripts for other creators"
        ]
    elif primary == "content":
        why = "You are comfortable on camera or want the highest long-term upside. Short-form video is currently the fastest way to build an audience that can later buy products, services, or brand deals."
        tools = ["CapCut – free powerful video editor", "TikTok + Instagram + YouTube apps", "Canva – thumbnails, graphics, end screens", "Later: Gumroad or Payhip for your own products"]
        day1_7 = [
            "Day 1: Download CapCut, TikTok, Instagram, YouTube. Create clean profiles with a clear bio.",
            f"Day 2: Choose your angle inside “{niche}”. Study 8–10 top accounts and note their hooks.",
            "Day 3: Film and edit your first 3 vertical videos (15–45 seconds) in CapCut with captions.",
            "Day 4: Post one video on TikTok + Reels + Shorts. Strong hook in the first 3 seconds is critical.",
            "Day 5–7: Post at least one video every single day. Focus on consistency, not perfection."
        ]
        days_8_30 = [
            "Days 8–14: Keep daily posting. Experiment with 2–3 different styles of hooks and formats.",
            "Days 15–21: Double down on the video style that gets the best retention. Start adding soft CTAs.",
            "Days 22–30: Create your first simple digital product or affiliate offer and promote it from your best videos."
        ]
        money = "Early income: TikTok Creator Rewards, live gifts, affiliate links. Later: sell your own digital products (Gumroad/Payhip – both use Stripe) or get brand deals and UGC work."
        reels = "Always vertical. Use CapCut auto-captions. Put the main point or curiosity in the first 3 seconds. Batch-film 4–5 videos at once when possible."
        advertise = "Organic consistency first. After you have proven videos, run $5–15/day Spark Ads or Instagram ads driving to a landing page or product."
        ideas = [
            f"Quick tips or myths about {niche}",
            f"“Day in the life” or behind-the-scenes related to {niche}",
            f"Product reviews or recommendations in the {niche} space",
            f"Short tutorials or “how I do X” videos",
            "Story-style videos that end with a soft offer"
        ]
    elif primary == "digital":
        why = "You like creating something once and selling it repeatedly, or you have limited daily time. Digital products give real leverage — make it once, sell it for months or years."
        tools = ["Canva – design the actual products + mockups", "Gumroad or Payhip – storefront + automatic delivery + payments", "CapCut – optional short promo videos", "TikTok / Instagram – free traffic"]
        day1_7 = [
            "Day 1: Download Canva. Create free accounts on Gumroad and/or Payhip.",
            f"Day 2: Design your first simple digital product related to “{niche}” (planner, checklist, template pack, mini-guide, etc.).",
            "Day 3: Create 3–4 attractive mockup images in Canva showing the product in use.",
            "Day 4: Upload the product, write a clear benefit-focused description, set price $7–17, and publish.",
            "Day 5: Make 2–3 short promo videos in CapCut.",
            "Day 6–7: Post the promo videos and share your sales link everywhere you can."
        ]
        days_8_30 = [
            "Days 8–14: Create a second related product or a small bundle. Keep posting value content + product links.",
            "Days 15–21: Improve the sales page based on any feedback. Test a slightly higher price.",
            "Days 22–30: Add a simple email capture or upsell. Consider moving high-volume products to a lower-fee option or pure Stripe Payment Links."
        ]
        money = "Gumroad and Payhip both process payments via Stripe. Payhip’s free plan (5%) is often better than Gumroad’s free plan (10% + $0.50). For maximum control later, use Stripe Payment Links directly."
        reels = "Show the product on screen, flip through pages, or do a quick “what’s inside” video. Keep it under 30 seconds and end with the link."
        advertise = "Post helpful content related to the product and add a soft CTA. Share in Facebook groups and relevant communities. Later run simple ads to the product page."
        ideas = [
            f"Printable or digital planner / tracker for {niche}",
            f"Canva template pack (Instagram posts, stories, or carousels) for {niche}",
            f"Checklist or swipe-file related to {niche}",
            f"Mini-guide or “starter kit” PDF about {niche}",
            "Bundle of 3 small products at a higher price point"
        ]
    else:
        why = "You are comfortable talking on camera and want paid work without needing a big following. Brands pay for authentic, phone-shot videos that feel real."
        tools = ["CapCut – edit your samples and client videos", "Google Drive or Canva – simple portfolio", "Billo + JoinBrands – beginner-friendly UGC platforms", "Phone with good natural light"]
        day1_7 = [
            "Day 1: Film 3–4 sample videos using products you already own (unboxing, demo, honest review, “how I use it”).",
            "Day 2: Edit them cleanly in CapCut (captions + good pacing).",
            "Day 3: Put the best samples in a Google Drive folder or simple Canva portfolio page.",
            "Day 4: Create accounts on Billo and JoinBrands and complete your profiles thoroughly.",
            "Day 5–7: Apply to 8–12 briefs every day. Treat applying like part of the actual job."
        ]
        days_8_30 = [
            "Days 8–14: Continue applying daily. Deliver any accepted jobs early and ask for permission to use them in your portfolio.",
            "Days 15–21: Once you have 5+ delivered videos, raise your rates and start pitching small brands directly on Instagram.",
            "Days 22–30: Create a simple media kit and consider offering packages via Stripe Payment Links for direct brand clients."
        ]
        money = "Most UGC platforms pay via PayPal or direct deposit. Typical beginner rates are $50–150+ per short video. Direct brand clients can be charged via Stripe Payment Links for higher margins."
        reels = "Your UGC samples can also be posted (with permission) as content. Behind-the-scenes of your process also attracts potential clients."
        advertise = "The platforms themselves are the main source of work. Supplement with cold Instagram DMs to small brands whose ads you already like."
        ideas = [
            f"Product demo or unboxing videos in the {niche} space",
            f"Honest review style videos for {niche} products",
            f"“How I use this daily” lifestyle UGC",
            "Before/after or problem → solution style clips",
            "Testimonial-style talking head videos"
        ]

    return {
        "primary": primary_name,
        "secondary": secondary_name,
        "niche": niche,
        "time": time,
        "goal": goal,
        "why": why,
        "tools": tools,
        "day1_7": day1_7,
        "days_8_30": days_8_30,
        "money": money,
        "reels": reels,
        "advertise": advertise,
        "ideas": ideas
    }

def create_pdf(plan):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=0.7*inch, leftMargin=0.7*inch, topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="MainTitle", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6))
    styles.add(ParagraphStyle(name="SubTitle", fontName="Helvetica", fontSize=11, leading=14, textColor=ACCENT, alignment=TA_CENTER, spaceAfter=12))
    styles.add(ParagraphStyle(name="SectionHead", fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=PRIMARY, spaceBefore=12, spaceAfter=4))
    styles.add(ParagraphStyle(name="BodyText2", fontName="Helvetica", fontSize=9.5, leading=13, textColor=DARK, alignment=TA_JUSTIFY, spaceAfter=4))
    styles.add(ParagraphStyle(name="BulletText", fontName="Helvetica", fontSize=9.5, leading=12.5, textColor=DARK, leftIndent=12, spaceAfter=2))
    styles.add(ParagraphStyle(name="Small", fontName="Helvetica", fontSize=8.5, leading=11, textColor=MUTED, alignment=TA_CENTER))

    story = []
    story.append(Paragraph("PHONE TO PAYCHECK", styles["MainTitle"]))
    story.append(Paragraph("Your Personalized Business Blueprint", styles["SubTitle"]))
    story.append(Paragraph(f"Generated {datetime.now().strftime('%B %d, %Y')}", styles["Small"]))
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=10))
    story.append(Paragraph("Recommended Primary Path", styles["SectionHead"]))
    story.append(Paragraph(f"<b>{plan['primary']}</b>", styles["BodyText2"]))
    story.append(Paragraph(plan["why"], styles["BodyText2"]))
    if plan["secondary"]:
        story.append(Paragraph(f"<b>Secondary path:</b> {plan['secondary']}", styles["BodyText2"]))
    story.append(Paragraph(f"<b>Niche focus:</b> {plan['niche']}", styles["BodyText2"]))
    story.append(Paragraph(f"<b>Time available:</b> {plan['time']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Goal:</b> {plan['goal']}", styles["BodyText2"]))
    story.append(Paragraph("Tools to Set Up Today", styles["SectionHead"]))
    for t in plan["tools"]:
        story.append(Paragraph(f"• {t}", styles["BulletText"]))
    story.append(Paragraph("Specific Ideas for You", styles["SectionHead"]))
    for idea in plan["ideas"]:
        story.append(Paragraph(f"• {idea}", styles["BulletText"]))
    story.append(Paragraph("First 7 Days – Launch", styles["SectionHead"]))
    for step in plan["day1_7"]:
        story.append(Paragraph(f"• {step}", styles["BulletText"]))
    story.append(Paragraph("Days 8–30 – Build Momentum", styles["SectionHead"]))
    for step in plan["days_8_30"]:
        story.append(Paragraph(f"• {step}", styles["BulletText"]))
    story.append(Paragraph("How You Collect Money", styles["SectionHead"]))
    story.append(Paragraph(plan["money"], styles["BodyText2"]))
    story.append(Paragraph("Creating Reels & Short Videos", styles["SectionHead"]))
    story.append(Paragraph(plan["reels"], styles["BodyText2"]))
    story.append(Paragraph("Getting Traffic & Customers", styles["SectionHead"]))
    story.append(Paragraph(plan["advertise"], styles["BodyText2"]))
    story.append(Paragraph("Stripe Payment Links (Higher Margin Option)", styles["SectionHead"]))
    story.append(Paragraph("1. Go to stripe.com and create a free account.<br/>2. Dashboard → Payment Links → Create payment link.<br/>3. Add title, price, optional image.<br/>4. Copy the link and share it anywhere.<br/>5. Stripe deposits money to your bank.", styles["BodyText2"]))
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
    story.append(Paragraph("You now have a clear map. Take the first step today.", styles["BodyText2"]))
    story.append(Paragraph("Phone to Paycheck  •  Personalized Blueprint", styles["Small"]))
    doc.build(story)
    buffer.seek(0)
    return buffer

def show_login():
    st.title("📱 Phone to Paycheck")
    st.subheader("Personalized Business Blueprint")
    st.write("Enter the access code you received after purchase.")
    code = st.text_input("Access Code", type="password", placeholder="Enter code")
    if st.button("Unlock →", type="primary"):
        if code.strip().upper() == ACCESS_CODE.upper():
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect code. Check the email or message you received after purchase.")

def show_welcome():
    st.title("📱 Phone to Paycheck")
    st.subheader("Your Personalized Business Blueprint")
    st.success("Access granted.")
    st.write("Answer a few quick questions (≈ 2 minutes). The more honest you are, the better your plan will be.")
    if st.button("Start My Blueprint →", type="primary"):
        st.session_state.step = 1
        st.rerun()

def show_q_time():
    st.header("1. Time Available")
    time = st.radio("How much time can you realistically put in most days?", ["15–30 minutes", "30–60 minutes", "1–2 hours", "2+ hours"], index=1)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            st.session_state.step = 0
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.answers["time"] = time
            st.session_state.step = 2
            st.rerun()

def show_q_pref():
    st.header("2. What Feels Most Natural?")
    pref = st.radio("Choose the option that feels easiest or most exciting:", ["Talking on camera", "Writing & designing", "Helping people with tasks", "Creating something once and selling repeatedly", "Not sure — recommend the best for me"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            st.session_state.step = 1
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.answers["preference"] = pref
            st.session_state.step = 3
            st.rerun()

def show_q_skills():
    st.header("3. What Do You Already Have?")
    skills = st.multiselect("Select all that apply:", ["Social media following", "Writing skill", "Design / Canva experience", "Comfort talking on video", "None yet"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            st.session_state.step = 2
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.answers["skills"] = skills
            st.session_state.step = 4
            st.rerun()

def show_q_goal():
    st.header("4. Your Main Goal (Next 60 Days)")
    goal = st.radio("What do you most want right now?", ["First $100 as fast as possible", "Consistent $300–500 / month side income", "Reach $1,000+ / month", "Build toward replacing a job"])
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            st.session_state.step = 3
            st.rerun()
    with c2:
        if st.button("Next →", type="primary"):
            st.session_state.answers["goal"] = goal
            st.session_state.step = 5
            st.rerun()

def show_q_niche():
    st.header("5. Niche or Interests (Optional but Powerful)")
    st.write("What topics do you already know or enjoy? This lets me give you concrete ideas.")
    niche = st.text_input("Examples: money tips, coffee, fitness, skincare, parenting…", placeholder="Type a few words or leave blank")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("← Back"):
            st.session_state.step = 4
            st.rerun()
    with c2:
        if st.button("Build My Blueprint →", type="primary"):
            st.session_state.answers["niche"] = niche
            st.session_state.step = 6
            st.rerun()

def show_blueprint():
    if st.session_state.plan is None:
        st.session_state.plan = generate_blueprint(st.session_state.answers)
    plan = st.session_state.plan

    st.title("🎉 Your Personalized Blueprint")
    st.caption(f"Generated {datetime.now().strftime('%B %d, %Y')}")

    st.markdown(f'<div class="plan-box"><h3 style="margin-top:0;color:#1A365D;">Recommended Primary Path</h3><p style="font-size:1.2rem;"><strong>{plan["primary"]}</strong></p><p>{plan["why"]}</p></div>', unsafe_allow_html=True)

    if plan["secondary"]:
        st.markdown(f"**Secondary path:** {plan['secondary']}")
    st.markdown(f"**Niche:** {plan['niche']}  \n**Time:** {plan['time']}  |  **Goal:** {plan['goal']}")

    st.subheader("🛠️ Tools to Set Up Today")
    for t in plan["tools"]:
        st.markdown(f"- {t}")

    st.subheader("💡 Specific Ideas for You")
    for idea in plan["ideas"]:
        st.markdown(f"- {idea}")

    st.subheader("📅 First 7 Days – Launch")
    for step in plan["day1_7"]:
        st.markdown(f'<div class="step-box">{step}</div>', unsafe_allow_html=True)

    st.subheader("📈 Days 8–30 – Build Momentum")
    for step in plan["days_8_30"]:
        st.markdown(f"- {step}")

    st.subheader("💰 How You Collect Money")
    st.write(plan["money"])

    st.subheader("🎬 Creating Reels & Short Videos")
    st.write(plan["reels"])

    st.subheader("📢 Getting Traffic & Customers")
    st.write(plan["advertise"])

    with st.expander("🔑 How to Create Stripe Payment Links"):
        st.markdown("1. Go to [stripe.com](https://stripe.com) on your phone browser and create a free account.\n2. Dashboard → **Payment Links** → **Create payment link**.\n3. Add title, price, optional image.\n4. Copy the link and share it anywhere.\n5. Money goes straight to your bank (only normal Stripe fees).")

    st.markdown("---")
    try:
        pdf_buffer = create_pdf(plan)
        st.download_button(label="📥 Download My Blueprint (PDF)", data=pdf_buffer.getvalue(), file_name="Phone_to_Paycheck_Blueprint.pdf", mime="application/pdf", type="primary")
    except Exception as e:
        st.error("PDF generation temporarily unavailable. Please try again.")

    if st.button("Start Over"):
        st.session_state.step = 0
        st.session_state.answers = {}
        st.session_state.plan = None
        st.rerun()

if not st.session_state.authenticated:
    show_login()
else:
    if st.session_state.step == 0:
        show_welcome()
    elif st.session_state.step == 1:
        show_q_time()
    elif st.session_state.step == 2:
        show_q_pref()
    elif st.session_state.step == 3:
        show_q_skills()
    elif st.session_state.step == 4:
        show_q_goal()
    elif st.session_state.step == 5:
        show_q_niche()
    elif st.session_state.step == 6:
        show_blueprint()
