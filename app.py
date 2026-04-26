import streamlit as st
from agent_system import run_research

st.set_page_config(page_title="Research Assistant", layout="wide")

st.title("Research Assistant")

# -----------------------------
# SESSION STATE
# -----------------------------
if "tabs" not in st.session_state:
    st.session_state.tabs = []

if "active_tab" not in st.session_state:
    st.session_state.active_tab = None


# -----------------------------
# SIDEBAR (LIKE CHATGPT)
# -----------------------------
st.sidebar.title("💬 Chats")

# 🔹 New Search Button
if st.sidebar.button("➕ New Search"):
    st.session_state.active_tab = None  # reset to new search page


# 🔹 History Tabs
for i, tab in enumerate(st.session_state.tabs):
    if st.sidebar.button(f"{i+1}. {tab['topic'][:20]}"):
        st.session_state.active_tab = i


# -----------------------------
# MAIN AREA
# -----------------------------
# 🔹 If no tab selected → show search input
if st.session_state.active_tab is None:
    st.subheader("New Search")

    topic = st.text_input("Enter a topic", placeholder="Example: XGBoost")

    if st.button("Search"):
        if topic.strip():
            with st.spinner("Searching..."):
                result = run_research(topic)

            st.session_state.tabs.append(result)
            st.session_state.active_tab = len(st.session_state.tabs) - 1
            st.rerun()
        else:
            st.warning("Please enter a topic")


# 🔹 If tab selected → show results
else:
    result = st.session_state.tabs[st.session_state.active_tab]

    # Title
    st.subheader(f"📊 {result.get('topic')}") 

    # -------------------------


    # -------------------------
    # SUMMARY
    # -------------------------
    st.subheader("Summary")
    st.write(result.get("summary", ""))

    # -------------------------
    # RUNTIME
    # -------------------------
    st.subheader("⏱ Runtime")
    runtime = result.get("runtime", 0)

    if runtime > 60:
        st.success(f"{round(runtime/60, 2)} minutes")
    else:
        st.success(f"{runtime} seconds")

    # # BEST RESULT ACROSS RUNS
    # # -------------------------
    # best_result = result.get("best_result", {})
    # previous_runs_count = result.get("previous_runs_count", 0)

    # st.subheader("Best Result Across Runs")
    # if best_result:
    #     st.markdown(f"### [{best_result.get('title', 'Untitled')}]({best_result.get('link', '#')})")
    #     st.write(f"**Published:** {best_result.get('published', 'N/A')}")
    #     st.write(best_result.get("snippet", ""))
    #     st.caption(
    #         f"Combined score: {best_result.get('combined_score', 0)} | "
    #         f"Seen in previous runs: {best_result.get('history_hits', 0)} | "
    #         f"Latest run: {best_result.get('latest_hits', 0)} | "
    #         f"Past matches loaded: {previous_runs_count}"
    #     )
    #     st.divider()
    # else:
    #     st.info("No best result could be selected for this search.")

    # -------------------------
    # WEB RESULTS
    # -------------------------
    st.subheader("Web Results")
    for item in result.get("web_results", []):
        if item.get("error"):
            continue

        st.markdown(f"### [{item.get('title')}]({item.get('link')})")
        st.write(f"**Published:** {item.get('published', 'N/A')}")
        st.write(item.get("snippet", ""))
        st.caption(f"Score: {item.get('score', 0)}")
        st.divider()

    # -------------------------
    # COMPARED RESULTS
    # -------------------------
    # st.subheader("Internal Comparison")
    # st.write("This section merges the latest search with earlier stored searches and keeps the strongest matches on top.")

    # for item in result.get("compared_results", [])[:5]:
    #     st.markdown(f"### [{item.get('title', 'Untitled')}]({item.get('link', '#')})")
    #     st.write(f"**Published:** {item.get('published', 'N/A')}")
    #     st.write(item.get("snippet", ""))
    #     st.caption(
    #         f"Combined score: {item.get('combined_score', 0)} | "
    #         f"History hits: {item.get('history_hits', 0)} | "
    #         f"Latest hits: {item.get('latest_hits', 0)}"
    #     )
    #     st.divider()

    # -------------------------
    # IMAGES
    # -------------------------
    st.subheader("Images")
    cols = st.columns(3)

    for i, img in enumerate(result.get("images", [])):
        if img.get("error"):
            continue

        with cols[i % 3]:
            st.image(img.get("image_url"), caption=img.get("title"))

    # -------------------------
    # YOUTUBE VIDEOS
    # -------------------------
    st.subheader("YouTube Videos")
    videos = [v for v in result.get("videos", []) if not v.get("error")]

    if videos:
        video_cols = st.columns(2)
        for i, video in enumerate(videos):
            with video_cols[i % 2]:
                thumbnail_url = video.get("thumbnail_url")
                if thumbnail_url:
                    st.image(thumbnail_url, use_container_width=True)

                st.markdown(f"### [{video.get('title', 'Untitled')}]({video.get('link', '#')})")
                if video.get("channel"):
                    st.write(f"**Channel:** {video.get('channel')}")
                st.write(f"**Published:** {video.get('published', 'N/A')}")
                if video.get("duration"):
                    st.caption(f"Duration: {video.get('duration')}")
                st.write(video.get("snippet", ""))
                st.caption("YouTube result")
                st.divider()
    else:
        st.info("No YouTube videos found for this search.")

    # -------------------------
    # PAPERS
    # -------------------------
    st.subheader("Research Papers")
    for paper in result.get("papers", []):
        if paper.get("error"):
            continue

        st.markdown(f"### [{paper.get('title')}]({paper.get('link')})")
        st.write(f"**Published:** {paper.get('published')}")
        st.write(paper.get("summary")[:500] + "...")
        st.divider()
