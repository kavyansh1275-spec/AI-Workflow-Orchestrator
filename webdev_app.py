from __future__ import annotations
import streamlit as st
from webdev.engine import WebDeveloper

st.set_page_config(page_title="AI Web Developer",page_icon="⚡",layout="wide")
st.title("⚡ AI Web Developer")
st.caption("Plan → Code → Test → Repair → Browser QA → Deploy")

with st.sidebar:
    st.subheader("Workspace")
    project_name=st.text_input("Project name",placeholder="my-business-site")
    github_repo=st.text_input("GitHub repository",placeholder="owner/repository")
    github_branch=st.text_input("Branch",value="main")
    deploy=st.checkbox("Prepare deployment")
    max_repairs=st.slider("Max repair attempts",0,5,3)

request=st.chat_input("Describe the website or app you want to build...")
if request:
    with st.chat_message("user"): st.write(request)
    with st.chat_message("assistant"):
        with st.status("AI Web Developer is working...",expanded=True):
            report=WebDeveloper().run(request,project_name or None,github_repo or None,github_branch,deploy,max_repairs)
            st.success("Run complete")
            c=st.columns(4)
            c[0].metric("Run",report.run_id)
            c[1].metric("Stages",len(report.steps))
            c[2].metric("Tests",len(report.tests))
            c[3].metric("Errors",len(report.errors))
            for step in report.steps:
                st.write(f"**{step.name}** — {step.status} — {step.detail}")
            if report.live_url: st.link_button("Open live result",report.live_url)
            st.download_button("Download full report",report.json(),file_name=report.run_id+"-report.json")
