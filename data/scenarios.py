"""In-memory scenarios and their user-facing, evidence-mapped descriptions."""

SCENARIO_GUIDANCE = {
    "Normal traffic": {
        "summary": "One ordinary sample command follows the virtual node path.",
        "mapping": "Baseline",
        "vulnerable": "Accepted by the model",
        "hardened": "Accepted by the model",
    },
    "Replay attempt": {
        "summary": "A previously seen command is submitted once more to the virtual relay.",
        "mapping": "Freshness check · NIST logical access / device security",
        "vulnerable": "Duplicate command accepted",
        "hardened": "Duplicate nonce rejected",
    },
    "Authentication failure": {
        "summary": "One invalid lab credential is recorded; this is not a guessing loop.",
        "mapping": "OWASP IoT I1 · NIST logical access",
        "vulnerable": "Invalid credential rejected",
        "hardened": "Invalid credential rejected",
    },
    "MQTT without TLS": {
        "summary": "Inspect the selected profile's transport policy. No packets or broker session are created.",
        "mapping": "OWASP IoT I7 · NIST data protection",
        "vulnerable": "No TLS policy configured",
        "hardened": "TLS required by profile",
    },
    "Flood / high request-rate event": {
        "summary": "Apply one fixed 40-request sample to counters; no requests are sent or looped.",
        "mapping": "OWASP IoT I2 · availability model",
        "vulnerable": "40 sample requests unthrottled",
        "hardened": "38 of 40 sample requests rate-limited",
    },
    "Unsigned OTA attempt": {
        "summary": "Present firmware metadata without a valid signature. No image is uploaded or flashed.",
        "mapping": "OWASP IoT I4 · NIST software update",
        "vulnerable": "Candidate would be accepted",
        "hardened": "Candidate rejected",
    },
    "Debug interface exposure": {
        "summary": "Inspect the modeled UART debug policy; no serial interface is probed.",
        "mapping": "OWASP IoT I2 / I10 · NIST logical access",
        "vulnerable": "UART debug exposed",
        "hardened": "UART debug restricted",
    },
    "Default credential access": {
        "summary": "Try one fixed lab-only default credential. No password guessing or credential list is used.",
        "mapping": "OWASP IoT I1 · NIST logical access",
        "vulnerable": "Default credential accepted",
        "hardened": "Default credential rejected",
    },
    "Unauthorized MQTT topic write": {
        "summary": "Submit one fixed command to the virtual relay topic without the required topic permission.",
        "mapping": "OWASP IoT I3 · NIST logical access to interfaces",
        "vulnerable": "Open topic policy accepts command",
        "hardened": "Topic ACL rejects command",
    },
}

SCENARIOS = tuple(SCENARIO_GUIDANCE)
