import requests
import os

# --- USER: Set your counties and state abbreviation here ---
counties = ["Clinton", "Essex"]    #Enter multiple counties here if applicable
state_abbr = "NY"                  #Enter Abbreviated state here
ALERT_ID_FILE = "sent_alerts.txt"
CHAR_LIMIT = 200
# ----------------------------------------------------------

def get_alerts_by_area_desc(counties, state_abbr):
    url = f"https://api.weather.gov/alerts/active?area={state_abbr}"
    resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
    if resp.status_code != 200:
        print("Error retrieving weather alerts.")
        return []
    data = resp.json()
    alerts = []
    county_options = []
    for county in counties:
        county_lc = county.lower()
        county_options.extend([county_lc, f"{county_lc} county"])
    for feature in data.get('features', []):
        area_desc = feature['properties'].get('areaDesc', '').lower()
        if any(option in area_desc for option in county_options):
            alerts.append(feature['properties'])
    return alerts

def get_first_line(text):
    if not text or not isinstance(text, str) or not text.strip():
        return "N/A"
    return text.strip().split('\n')[0]

def build_alert_outputs(alerts):
    """Return a list of outputs, one for each alert (for per-alert splitting)."""
    outputs = []
    for i, alert in enumerate(alerts, 1):
        out = (
            f"Weather Alerts:\n"
            f"⚠️ Alert {i}:\n"
            f"Headline: {alert.get('headline', 'N/A')}\n"
            #f"Effective: {alert.get('effective', 'N/A')}\n"
            #f"Expires: {alert.get('expires', 'N/A')}\n"
            #f"Hazard: {alert.get('eventDescription') or alert.get('event', 'N/A')}\n"
            #f"Impact: {alert.get('response', 'N/A')}\n"
            #f"Impacted Locations: {alert.get('areaDesc', 'N/A')}\n"
            f"Instructions: {get_first_line(alert.get('instruction', 'N/A'))}\n"
            f"---EOM--- \n\n"
        )
        outputs.append(out)
    return outputs

def load_sent_alert_ids(filename):
    if not os.path.exists(filename):
        return set()
    with open(filename, 'r') as f:
        return set(line.strip() for line in f)

def save_sent_alert_ids(ids, filename):
    with open(filename, 'w') as f:
        for alert_id in ids:
            f.write(f"{alert_id}\n")

def send_message(message):
    print("Sending message:")
    print(message)
    # Uncomment below for actual sending
    # os.system(f"/usr/local/bin/meshtastic --ch-index 3 --sendtext \"{message}\"")

def split_and_send(message, char_limit):
    while message:
        part = message[:char_limit]
        send_message(part)
        message = message[char_limit:]

def main():
    alerts = get_alerts_by_area_desc(counties, state_abbr)
    sent_ids = load_sent_alert_ids(ALERT_ID_FILE)
    new_alerts = []
    new_ids = set(sent_ids)
    for alert in alerts:
        alert_id = alert.get('id')
        if alert_id and alert_id not in sent_ids:
            new_alerts.append(alert)
            new_ids.add(alert_id)
    outputs = build_alert_outputs(new_alerts)
    if outputs:
        for out in outputs:
            if len(out) > CHAR_LIMIT:
                split_and_send(out, CHAR_LIMIT)
            else:
                send_message(out)
        save_sent_alert_ids(new_ids, ALERT_ID_FILE)
    else:
        print("No new weather alerts for your counties.")

if __name__ == "__main__":
    main()
