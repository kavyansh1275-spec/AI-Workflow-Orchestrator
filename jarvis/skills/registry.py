from .base import Skill

SPECS = {
"programming": ("Write, modify, test and debug software", ("python","javascript","typescript","code","program","debug"), ("write_code","run_tests","debug")),
"web_development": ("Build web applications", ("website","web","html","css","react","frontend","backend"), ("design_ui","build_frontend","build_backend")),
"ai_ml": ("Work with machine learning and AI systems", ("ai","machine learning","neural","transformer","model","training"), ("design_model","evaluate_model","train_model")),
"research": ("Research and synthesize information", ("research","find","investigate","study","compare"), ("search","synthesize","cite")),
"critical_thinking": ("Analyze claims, assumptions and evidence", ("analyze","evidence","reason","critique"), ("identify_assumptions","evaluate_evidence")),
"learning": ("Learn and improve skills systematically", ("learn","teach","practice","improve"), ("decompose_skill","practice","evaluate")),
"debugging": ("Diagnose and fix software problems", ("bug","error","exception","debug","fix"), ("reproduce","diagnose","patch","test")),
"decision_making": ("Compare options using explicit criteria", ("decision","choose","options","tradeoff"), ("compare","assess_constraints","recommend_process")),
"sales": ("Support ethical sales workflows", ("sell","sales","lead","prospect","client"), ("qualify","draft_outreach","follow_up")),
"marketing": ("Plan marketing and campaigns", ("marketing","campaign","ad","promotion","audience"), ("research_audience","create_campaign")),
"copywriting": ("Create clear persuasive copy", ("copy","headline","caption","ad","description"), ("draft","edit","adapt_tone")),
"customer_research": ("Understand customer needs", ("customer","user","pain point","feedback"), ("interview_plan","synthesize_feedback")),
"product_design": ("Turn problems into product requirements", ("product","feature","mvp","requirements"), ("define_problem","specify_feature")),
"entrepreneurship": ("Develop and evaluate business ideas", ("business","startup","entrepreneur","company"), ("business_model","validation_plan")),
"negotiation": ("Prepare structured negotiations", ("negotiate","negotiation","deal","price"), ("map_interests","prepare_options")),
"finance": ("Apply basic financial reasoning", ("finance","budget","revenue","cost","profit"), ("calculate","scenario_analysis")),
"project_management": ("Plan and track projects", ("project","milestone","deadline","sprint"), ("breakdown","schedule","risk_check")),
"video_editing": ("Plan and automate video editing workflows", ("video","edit","short","reel"), ("shot_list","edit_plan")),
"blender_3d": ("Work with 3D and Blender workflows", ("blender","3d","model","render"), ("scene_plan","model_plan","render_plan")),
"graphic_design": ("Create visual design specifications", ("graphic","poster","logo","banner","design"), ("layout","brand_spec")),
"animation": ("Plan animation and motion", ("animation","animate","motion","character"), ("storyboard","motion_plan")),
"storytelling": ("Develop stories, scripts and narrative structure", ("story","storytelling","script","character","episode"), ("outline","scene_plan","dialogue")),
"ui_ux": ("Design usable interfaces", ("ui","ux","interface","user experience"), ("wireframe","interaction_plan")),
"content_creation": ("Plan and create social content", ("content","instagram","youtube","social","post"), ("content_plan","calendar")),
"networking": ("Prepare professional relationship-building workflows", ("network","networking","connection","contact"), ("outreach_plan","follow_up")),
"writing": ("Draft, edit and structure written material", ("write","writing","document","essay","email"), ("draft","revise")),
"ai_agents": ("Design tool-using agent systems", ("agent","agents","tool","memory","multi-agent"), ("tool_plan","agent_loop","evaluation")),
"cybersecurity": ("Apply defensive security fundamentals", ("security","authentication","permission","secure"), ("threat_model","security_check")),
"system_design": ("Design reliable software systems", ("architecture","system","scalable","database"), ("requirements","architecture","tradeoffs")),
"data_handling": ("Process structured data and APIs", ("sql","pandas","api","json","data","csv"), ("parse","transform","validate")),
"automation": ("Connect tools and automate workflows", ("automation","workflow","integrate","zapier","make","n8n"), ("workflow_plan","integration_plan")),
}

class SkillRegistry:
    def __init__(self):
        self.skills = {name: Skill(name, desc, tuple(keywords), tuple(capabilities)) for name,(desc,keywords,capabilities) in SPECS.items()}
    def get(self, name: str) -> Skill:
        return self.skills[name]
    def list(self) -> list[str]:
        return list(self.skills)
