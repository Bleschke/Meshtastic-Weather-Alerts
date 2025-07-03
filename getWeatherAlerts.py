import requests

# --- USER: Set your county and state abbreviation here ---
county_name = "Brewster"
state_abbr = "TX"
# --------------------------------------------------------

def get_alerts_by_area_desc(county_name, state_abbr):
    url = f"https://api.weather.gov/alerts/active?area={state_abbr}"
    resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    if resp.status_code != 200:
        print("Error retrieving weather alerts.")
        return []
    data = resp.json()
    alerts = []
    # More flexible match: county_name as substring in areaDesc
    county_name_lc = county_name.lower()
    # Also check for "County" or not
    county_options = [
        county_name_lc,
        f"{county_name_lc} county"
    ]
    for feature in data.get('features', []):
        area_desc = feature['properties'].get('areaDesc', '').lower()
        # Check if any county variant is a substring in area_desc
        if any(option in area_desc for option in county_options):
            alerts.append(feature['properties'])
    return alerts

def print_alerts(alerts):
    if not alerts:
        print("No active weather alerts for your county.")
        return
    for alert in alerts:
        print("-" * 40)
        print("⚠️ NOAA WEATHER ALERT "\n\n)
        print("Headline:", alert.get("headline"))
        print("Effective:", alert.get("effective"))
        print("Expires:", alert.get("expires"))
        print("Hazard:", alert.get("eventDescription", alert.get("event", 'N/A')))
        print("Impact:", alert.get("response", "N/A"))
        print("Impacted Locations:", alert.get("areaDesc", "N/A"))
        print("Instructions:", alert.get("instruction", "N/A"))
        print("-" * 40, end="\n\n")

def main():
    alerts = get_alerts_by_area_desc(county_name, state_abbr)
    print_alerts(alerts)

if __name__ == "__main__":
    main()
