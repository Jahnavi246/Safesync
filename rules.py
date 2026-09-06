def evaluate_hazard_rules(hazard_type, age, mobility, battery_level, offline_mode, language):
    """
    Universal Rule-Based Decision Engine:
    Evaluates profile traits (Age, Mobility, Battery) against 7 distinct disaster categories.
    """
    steps = []
    warnings = []

    # 1. FLOOD
    if "Flood" in hazard_type:
        if age >= 60 or mobility != "Normal":
            steps.append("Move toward designated higher ground at a slow, steady pace.")
            steps.append("Follow wheelchair/accessible evacuation paths provided on the map.")
            steps.append("Signal for immediate transport assistance if water rises rapidly.")
            warnings.append("Avoid fast-flowing water entirely — 6 inches can knock a person over.")
        else:
            steps.append("Evacuate immediately to designated high ground or shelter.")
            steps.append("Assist nearby children, elderly, or mobility-impaired individuals.")
            warnings.append("Do not walk or drive through flooded roads or submerged bridges.")

    # 2. FIRE
    elif "Fire" in hazard_type:
        steps.append("Get down low and crawl under smoke to reach the nearest exit.")
        steps.append("Touch door handles with the back of your hand before opening; if hot, do not open.")
        if mobility == "Wheelchair":
            steps.append("Proceed directly to the designated Accessible Refuge Area and activate SOS.")
        else:
            steps.append("Use stairwells only. NEVER use elevators during a fire emergency.")
        warnings.append("Once outside, stay out. Never re-enter a burning structure for belongings.")

    # 3. GAS LEAK
    elif "Gas Leak" in hazard_type:
        steps.append("Evacuate the premises immediately into fresh, outdoor air.")
        steps.append("Leave doors and windows open behind you if it does not delay exit.")
        warnings.append("DO NOT flip light switches, light matches, or create any sparks.")
        warnings.append("Do not operate cell phones inside the leak area.")

    # 4. BUILDING COLLAPSE
    elif "Building Collapse" in hazard_type:
        steps.append("If trapped: Cover mouth with a cloth or mask to prevent dust inhalation.")
        steps.append("Tap on pipes or walls periodically so search teams can hear your location.")
        steps.append("If mobile: Exit calmly via clear structural corridors, avoiding damaged stairways.")
        warnings.append("Shout only as a last resort to preserve energy and prevent dust inhalation.")

    # 5. ROAD ACCIDENT
    elif "Road Accident" in hazard_type:
        steps.append("Turn off vehicle ignition immediately to prevent fire hazards.")
        steps.append("Check yourself and passengers for injuries before attempting to move.")
        steps.append("Move to a safe spot away from traffic and activate hazard lights / SOS.")
        warnings.append("Do not move critically injured persons unless immediate fire/explosion risk exists.")

    # 6. CYCLONE
    elif "Cyclone" in hazard_type:
        steps.append("Remain indoors in an interior room away from glass windows and loose roofing.")
        steps.append("Disconnect non-essential electrical appliances to protect against power surges.")
        steps.append("Keep emergency kit, flashlights, and battery-powered radio readily accessible.")
        warnings.append("Do not be fooled by the 'Eye of the Storm' calm period; winds will resume suddenly.")

    # 7. EARTHQUAKE
    elif "Earthquake" in hazard_type:
        if mobility == "Wheelchair":
            steps.append("Lock wheelchair wheels, cover your head and neck with your arms and a cushion.")
        else:
            steps.append("DROP, COVER, and HOLD ON: Get under a sturdy table or desk.")
        steps.append("Stay indoors until shaking stops completely and it is safe to exit.")
        warnings.append("Stay away from windows, heavy furniture, hanging lights, and exterior walls.")

    # System Adaptive Constraints
    if battery_level <= 20:
        steps.insert(0, "🔋 BATTERY CRITICAL: Screen brightness minimized. Audio guidance prioritized.")
    if offline_mode:
        steps.insert(0, "📶 OFFLINE MODE: Using cached offline maps and local emergency protocols.")

    return steps, warnings
