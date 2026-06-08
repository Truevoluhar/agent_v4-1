from pydantic import BaseModel

from agent.permissions import permission_gate
from agent.tools.registry import get_tool_schemas, execute_registered_tool
from agent.session import Session
from agent.agent import Agent
from agent.context_builder import ContextBuilder

#
# Pomozne funkcije
#

class ModelStructuredResponse(BaseModel):
    is_task_finished: bool
    summary: str
    


def ask_user_permission(tool_name: str, tool_input: dict, reason: str) -> bool:
    print()
    print("Permission required")
    print(f"Tool: {tool_name}")
    print(f"Input: {tool_input}")
    print(f"Reason: {reason}")
    answer = input("Allow? [y/N]: ".strip().lower())
    
    return answer in {"y", "yes"}


def resolve_permission_decision(
    session: Session,
    tool_name: str,
    tool_input: dict,
    decision,
    input_func=input,
) -> str:
    """
    Vrne zadnjo executable akcijo
    - allow
    - deny
    """
    
    if decision.action == "allow":
        return "allow"
    
    if decision.action == "deny":
        return "deny"

    if decision.action == "ask":
        if not session.interactive:
            return "deny"
        
        print()
        print("Permission required")
        print(f"Tool: {tool_name}")
        print(f"Input: {tool_input}")
        print(f"Reason: {decision.reason}")
        
        answer = input_func("Allow? [y/N]: ".strip().lower())
        
        if answer in {"y", "yes"}:
            return "allow"
        
        return "deny"
    
    return "deny"
    
#
# Glavni loop
#
    
def run_agent(session: Session, agent: Agent, context_builder: ContextBuilder, max_steps: int = 20, input_func=input) -> str:
    tools = get_tool_schemas(agent.name)
    
    session.add_event("user_message", {
        "content": session.user_prompt
    })
    
    for _ in range(max_steps):
        
        messages = context_builder.build_context(session, agent)

        response = agent.client.chat(messages, tools)
        
        if response.has_tool_call:
            tool_call = response.tool_call
            tool_call_id = tool_call.id or f"local_call_{len(session.events)}"

            session.add_event("model_tool_call", {
                "id": tool_call_id,
                "name": tool_call.name,
                "input": tool_call.input
            })
            
            decision = permission_gate(
                tool_name=tool_call.name, 
                tool_input=tool_call.input,
                workspace=session.workspace_path(),
                mode=session.permission_mode,
                interactive=session.interactive
            )
            
            resolved_action = resolve_permission_decision(
                session=session,
                tool_name=tool_call.name,
                tool_input=tool_call.input,
                decision=decision,
                input_func=input_func
            )
            
            session.add_event("permission_decision", {
                "tool": tool_call.name,
                "input": tool_call.input,
                "decision": decision.action,
                "resolved_action": resolved_action,
                "reason": decision.reason,
                "matched_rule": decision.matched_rule
            })
            
            if resolved_action == "deny":
                result = {
                    "ok": False,
                    "output": None,
                    "error": f"Permission denied: {decision.reason}",
                    "metadata": {
                        "permission_decision": decision.action,
                        "resolved_action": resolved_action,
                        "matched_rule": decision.matched_rule
                    }
                }
            else:
                result = execute_registered_tool(
                    workspace=session.workspace_path(), 
                    tool_name=tool_call.name, 
                    tool_input=tool_call.input)
            
            session.add_event("tool_result", {
                "tool_call_id": tool_call_id,
                "tool": tool_call.name,
                "result": result
            })
            
            continue
        
        
        session.final = response.text
        session.add_event("final_answer", {
            "content": response.text
        })
        session.save()
        
        return response.text
    
    session.final = "Stopped: max_steps exceeded"
    
    session.add_event("final_answer", {
        "content": session.final
    })
    
    session.save()
    
    return session.final