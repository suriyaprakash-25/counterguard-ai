import sys
import pathlib

# Add the project root to sys.path so we can import backend correctly
root_dir = pathlib.Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.services.investigation_engine import InvestigationEngine

def main():
    print("Initializing LangGraph orchestrator engine...")
    engine = InvestigationEngine()
    
    listing_id = "FLK-8823910-white-sneaker"
    listing_data = {"title": "Brand new sneakers", "price": 49.99}
    
    print(f"Executing pipeline for listing: {listing_id}...\n")
    final_state = engine.run(listing_id, listing_data)
    
    print("\n" + "="*40)
    print(f"Investigation ID: {final_state['listing_id']}")
    print("="*40)
    
    print("\n--- Evidence Timeline ---")
    for event in final_state["evidence_timeline"]:
        print(f"[{event['timestamp']}] {event['agent'].upper()}: {event['action']}")
        print(f"  -> {event['detail']}")
        if event.get('confidence_delta', 0) > 0:
            print(f"  -> Confidence altered by +{event['confidence_delta']}")
            
    print("\n--- Agent Findings ---")
    for agent, finding in final_state.get("agent_findings", {}).items():
        print(f"{agent}: {finding}")
        
    print(f"\nFinal Status: {final_state.get('status')}")
    print(f"Final Confidence: {final_state.get('confidence_score')}%")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()
