def evaluate_plan(plan):
    insights = []

    try:
        travel_cost = int(plan["budget_summary"]["travel"].split()[0])
        total = int(plan["budget_summary"]["total"].split()[0])

        if travel_cost > total * 0.4:
            insights.append("⚠ Travel takes a large portion of your budget")

        if len(plan["itinerary"]) > 3:
            insights.append("⚠ This trip is tightly packed. Consider adding rest time.")

        if not insights:
            insights.append("✅ This plan is balanced for time and budget")

    except:
        insights.append("ℹ Could not fully analyze this plan")

    return insights
