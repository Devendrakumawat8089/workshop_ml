from fastmcp import FastMCP
from database import get_doctor, get_patient

mcp = FastMCP("Dev Clinic MCP Server")


@mcp.tool
def doctor_details(name: str) -> dict:
    """Look up a doctor by exact name, for example 'Dr. Mehta'."""
    doctor = get_doctor(name)
    if not doctor:
        return {
            "success": False,
            "message": f"No doctor found with the name '{name}'."
        }
    return {"success": True, "doctor": doctor}


@mcp.tool
def patient_details(patient_id: int) -> dict:
    """Look up a patient using their database patient ID."""
    patient = get_patient(patient_id)
    if not patient:
        return {
            "success": False,
            "message": f"No patient found with ID {patient_id}."
        }
    return {"success": True, "patient": patient}


if __name__ == "__main__":
    # The client URL in ai_agent.py must match this HTTP MCP endpoint.
    mcp.run(transport="http", host="127.0.0.1", port=8001, path="/mcp")
