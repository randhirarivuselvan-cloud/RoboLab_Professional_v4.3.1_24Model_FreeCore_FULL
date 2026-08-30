from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class EngineResult:
    engine: str
    status: str
    data: dict[str, Any]
    warnings: list[str]

class NativeEngineeringEngine:
    """Deterministic engineering engines used when no external model is configured.
    These are not presented as a frontier LLM; they provide structured, testable baselines.
    """
    def _parts(self, text: str) -> list[dict[str, Any]]:
        t=text.lower(); out=[]
        if any(x in t for x in ["arduino", "esp32", "microcontroller"]): out.append({"category":"controller","name":"Microcontroller board","selection":"Choose by GPIO, ADC, PWM, voltage and compute needs"})
        if any(x in t for x in ["ultrasonic", "distance"]): out.append({"category":"sensor","name":"HC-SR04-class distance sensor","notes":"Use a level-safe interface for 3.3V MCUs"})
        if any(x in t for x in ["camera", "vision"]): out.append({"category":"sensor","name":"Camera module","notes":"Check interface bandwidth and compute requirements"})
        if "imu" in t or "gyro" in t or "accelerometer" in t: out.append({"category":"sensor","name":"6-axis IMU","notes":"Calibrate bias and frame orientation"})
        if any(x in t for x in ["motor", "wheel", "rover", "car"]): out.append({"category":"actuator","name":"DC gearmotor + motor driver","notes":"Select driver for stall current and battery voltage"})
        if "servo" in t: out.append({"category":"actuator","name":"Hobby servo","notes":"Provide adequate 5–6V supply and common ground"})
        return out

    def architect(self, description: str) -> dict[str, Any]:
        t=description.lower(); parts=self._parts(description)
        systems=[]
        if any(x in t for x in ["robot","rover","vehicle"]): systems.append("mobile_robotics")
        if any(x in t for x in ["wifi","bluetooth","iot","cloud"]): systems.append("connectivity")
        if any(x in t for x in ["camera","vision","image"]): systems.append("perception")
        return {"goal":description.strip(),"systems":systems,"candidate_components":parts,"interfaces":["power","control","telemetry"],"requirements_to_confirm":["controller","supply voltage","peak current","mechanical load","environment"],"confidence":"engineering-baseline"}

    def circuit(self, description: str) -> dict[str, Any]:
        p=self._parts(description); connections=[]
        has_mcu=any(x["category"]=="controller" for x in p)
        for x in p:
            if x["category"]=="sensor": connections.append({"from":x["name"],"to":"controller","interface":"sensor input","check":"logic levels / timing"})
            if x["category"]=="actuator": connections.append({"from":"controller","to":x["name"],"interface":"driver/control","check":"current and flyback handling"})
        return {"components":p,"connections":connections,"power_rules":["Do not power motors from MCU GPIO pins","Size regulator and battery for peak load","Use a common reference ground where required"],"controller_detected":has_mcu}

    def code(self, description: str, board: str, language: str) -> dict[str, Any]:
        t=description.lower(); ultrasonic=any(x in t for x in ["ultrasonic","distance","hc-sr04"]); servo="servo" in t; motor=any(x in t for x in ["motor","wheel","rover","car"])
        if "arduino" in language.lower() or "arduino" in board.lower():
            lines=["// RoboLab Native Engineering Engine v4.0.1","// Generated baseline; verify every pin and library before hardware use.","", "void setup() {", "  Serial.begin(115200);", "}", "", "void loop() {"]
            if ultrasonic: lines += ["  // Read distance sensor; verify divider/level shifting for MCU voltage."]
            if motor: lines += ["  // Drive motors through a rated motor driver; never from GPIO directly."]
            if servo: lines += ["  // Command servo using the appropriate library and supply."]
            lines += ["  delay(20);", "}"]
            return {"language":language,"board":board,"code":"\n".join(lines),"checks":["pin_map","libraries","logic_levels","power_budget","failsafe_behavior"]}
        return {"language":language,"board":board,"code":f"# RoboLab baseline for {board}\n# Implement board-specific SDK integration for: {description.strip()}","checks":["sdk","pin_map","power","failsafe"]}

    def cad(self, description: str) -> dict[str, Any]:
        return {"design_goal":description.strip(),"assemblies":["base/chassis","electronics_mount","sensor_mount"],"parameters":["overall_length","overall_width","overall_height","wall_thickness","fastener_size"],"manufacturing_notes":["Add service access","Avoid trapping heat around power electronics","Use fillets/chamfers where appropriate"],"cad_format":"parametric-specification"}

    def verify(self, description: str) -> dict[str, Any]:
        checks=[
            ("requirements", bool(description.strip()), "Project description is present"),
            ("power", not any(x in description.lower() for x in ["high current", "mains"]), "No obvious high-risk power-domain request detected"),
            ("interfaces", True, "Interface details must be confirmed during engineering review"),
        ]
        return {"checks":[{"name":n,"passed":p,"message":m} for n,p,m in checks],"overall":"PASS_WITH_REVIEW" if all(p for _,p,_ in checks) else "REVIEW_REQUIRED"}

    def compile_project(self, project: dict[str, Any]) -> dict[str, Any]:
        return {"artifact":"robolab-project-manifest","schema_version":"1","ready":False,"reason":"Native engine produces a validated manifest, not a firmware/CAD binary compiler artifact.","project_keys":sorted(project.keys())}

    def audit(self, project: dict[str, Any]) -> dict[str, Any]:
        risks=[]
        if not project.get("idea") and not project.get("description"): risks.append("missing_project_idea")
        if not project.get("requirements"): risks.append("requirements_not_explicit")
        return {"risk_count":len(risks),"risks":risks,"status":"PASS_WITH_REVIEW" if not risks else "REVIEW_REQUIRED"}

    def bom(self, description: str) -> dict[str, Any]:
        parts=self._parts(description)
        return {"items":parts,"count":len(parts),"pricing":"not live; verify vendor, stock and regional pricing before purchase"}

    def debug(self, code: str, language: str) -> dict[str, Any]:
        issues=[]
        if language.lower().startswith("arduino") or "cpp" in language.lower():
            if code.count("{") != code.count("}"): issues.append("brace_count_mismatch")
            if "delay(" not in code and "millis(" not in code: issues.append("timing_strategy_not_obvious")
        return {"language":language,"issues":issues,"status":"PASS_WITH_REVIEW" if not issues else "REVIEW_REQUIRED"}
