import os
from dotenv import load_dotenv
load_dotenv()

from autogen import (
    GroupChat,
    GroupChatManager,
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)

CONFIG_PATH = "GROQ_CONFIG_LIST.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(
        f"{CONFIG_PATH} not found. Create it and include your GROQ model/api_key/base_url."
    )

config_list = config_list_from_json(CONFIG_PATH)

# Shared llm_config for convenience
llm_config = {"config_list": config_list, "temperature": 0.2}


# Helper: build an inner team

def create_inner_team(team_name: str, region: str):
    """
    Creates an inner team (GroupChat + GroupChatManager) with:
      - UserProxyAgent (human-in-the-loop for that inner team)
      - DataCollector (AssistantAgent)
      - RiskAnalyzer (AssistantAgent)
      - Planner (AssistantAgent)

    Returns: manager (GroupChatManager), and a dictionary of agents.
    """
    # Create the assistant agents
    data_collector = AssistantAgent(
        name=f"{team_name}_DataCollector",
        llm_config=llm_config,
        system_message=f"You gather data for {region} and summarize key indicators (locations, counts, infrastructure).",
    )

    risk_analyzer = AssistantAgent(
        name=f"{team_name}_RiskAnalyzer",
        llm_config=llm_config,
        system_message=f"You analyze collected data for {region} and produce risk scores and hotspots.",
    )

    planner = AssistantAgent(
        name=f"{team_name}_Planner",
        llm_config=llm_config,
        system_message=f"You take risk analysis for {region} and propose prioritized emergency response plans.",
    )

    # UserProxyAgent for inner-team human-in-loop
    inner_user = UserProxyAgent(
        name=f"{team_name}_User",
        human_input_mode="ALWAYS",  # prompts terminal for approvals/overrides
        max_consecutive_auto_reply=1,
        code_execution_config={"use_docker": False},
        system_message="You are the human-in-the-loop for the inner team. Approve/reject/override agent outputs."
    )

    # Create GroupChat with manual speaker selection to avoid internal LLM speaker selection issues
    group_chat = GroupChat(
        agents=[inner_user, data_collector, risk_analyzer, planner],
        messages=[],
        max_round=20,
        speaker_selection_method="manual",  # manual selection at terminal
    )

    manager = GroupChatManager(groupchat=group_chat, name=f"{team_name}_Manager", llm_config=llm_config)
    agents = {
        "user": inner_user,
        "data_collector": data_collector,
        "risk_analyzer": risk_analyzer,
        "planner": planner,
        "group_chat": group_chat,
        "manager": manager,
    }
    return manager, agents



# Create two inner teams

inner1_manager, inner1_agents = create_inner_team("TeamA", "Bihar")
inner2_manager, inner2_agents = create_inner_team("TeamB", "Odisha")


# Outer team: coordinator and outer user (human oversight)

outer_coordinator = AssistantAgent(
    name="OuterCoordinator",
    llm_config=llm_config,
    system_message="You coordinate multiple inner teams and aggregate their outputs, propose resource allocations."
)

outer_user = UserProxyAgent(
    name="OuterUser",
    human_input_mode="ALWAYS",  # human supervises inter-team decisions
    max_consecutive_auto_reply=1,
    code_execution_config={"use_docker": False},
    system_message="You are the outer-level human who approves inter-team coordination and final outputs."
)

# Create a GroupChat for the outer team coordinating the two inner managers' outputs.
outer_group = GroupChat(
    agents=[outer_user, outer_coordinator],
    messages=[],
    max_round=20,
    speaker_selection_method="manual",
)
outer_manager = GroupChatManager(groupchat=outer_group, name="OuterManager", llm_config=llm_config)



# Demonstration flow

def run_inner_team_flow(manager, agents, initial_context: str):
    """
    Run a scripted sequence inside an inner team:
      1) Human (inner_user) asks DataCollector to gather data (init_context)
      2) Human prompts RiskAnalyzer to analyze
      3) Human prompts Planner to propose plan
      4) Human (inner_user) approves/rejects/overrides the plan
    This function uses the UserProxyAgent to enable approvals.
    """
    user = agents["user"]
    data_collector = agents["data_collector"]
    risk_analyzer = agents["risk_analyzer"]
    planner = agents["planner"]
    manager_obj = agents["manager"]

    print("\n=== Starting inner-team flow for:", manager_obj.name, "===")

    # Step 1: Ask data collector to gather/summarize data
    print("\n[Human -> DataCollector] Ask to gather data (you will be prompted).")
    user.initiate_chat(manager_obj, message=f"Please gather data for the situation: {initial_context}")

    # Terminal will prompt: choose speaker. Select DataCollector to respond.
    # Step 2: Ask risk analyzer to analyze the collected data
    print("\n[Human -> RiskAnalyzer] Ask to analyze collected data.")
    user.initiate_chat(manager_obj, message="Please analyze the collected data and identify hotspots and risk levels.")

    # Step 3: Ask planner to propose a prioritized plan
    print("\n[Human -> Planner] Request prioritized plan.")
    user.initiate_chat(manager_obj, message="Based on the risk analysis, propose a prioritized emergency response plan.")

    # Step 4: Human approval: forward planner output to the inner user for approval
    print("\n[Human Approval] Planner has proposed a plan. You (the human) will now be asked to APPROVE/REJECT or OVERRIDE.")
    user.initiate_chat(manager_obj, message="Planner produced a recommendation. Please APPROVE, REJECT, or PROVIDE OVERRIDE constraints for the plan.")

    print("=== Inner-team flow completed for:", manager_obj.name, "===\n")


def run_outer_coordination(outer_mgr, outer_user_agent, inner_managers):
    """
    Outer-level coordination:
     - Ask each inner team manager to provide their finalized recommendation
     - Ask outer human to allocate resources and validate final output
    """
    print("\n=== Starting outer-team coordination ===")
    # Ask inner teams for their final recommendations
    for m in inner_managers:
        print(f"\n[Outer -> {m.name}] Request final recommendation from inner team manager.")
        outer_user_agent.initiate_chat(m, message="Please provide your final recommendation and prioritized resource needs.")

    # Outer coordinator aggregates and suggests allocations
    print("\n[OuterCoordinator] Aggregate inner-team recommendations and propose a resource allocation plan.")
    outer_user_agent.initiate_chat(outer_mgr, message="Aggregate the teams' recommendations and propose a resource allocation plan across teams.")

    # Outer human approval for allocation
    print("\n[Outer human approval] You (outer human) will now be asked to APPROVE/REJECT/OVERRIDE the resource allocation.")
    outer_user_agent.initiate_chat(outer_mgr, message="Please APPROVE, REJECT, or OVERRIDE the proposed resource allocation and validate final outputs.")

    print("=== Outer-team coordination complete ===\n")



# Execute demo

if __name__ == "__main__":
    print("\n AutoGen SoM Demo — Assignment 0 (Human-in-the-loop) \n")
    # Provide initial contexts for each inner team
    context1 = "Severe flooding in Bihar: estimated displaced 500+, roads damaged, power outages."
    context2 = "Cyclone warning in Odisha: expected coastal storm surge and heavy rainfall."

    # Run inner teams. Note: each initiate_chat triggers terminal prompts to select speakers and to allow human input.
    run_inner_team_flow(inner1_manager, inner1_agents, context1)
    run_inner_team_flow(inner2_manager, inner2_agents, context2)

    # Outer coordination: ask each inner manager for final recommendation, then human approves allocation
    run_outer_coordination(outer_manager, outer_user, [inner1_manager, inner2_manager])

    print("\n Demo finished. Save logs/screenshots for your submission.\n")
    print("IMPORTANT: When prompted at terminal:")
    print(" - You will see a numbered list of speakers. Choose the agent you want to speak (DataCollector, RiskAnalyzer, Planner, or User).")
    print(" - When the UserProxyAgent prompts for approval, type APPROVE, REJECT, or type new instructions to OVERRIDE the plan.")


