package com.example.agent;

import java.util.LinkedHashMap;
import java.util.Map;

public class ClinicConfig {
    private final String clinicName;
    private final String address;
    private final String phone;
    private final String email;
    private final String bookingUrl;
    private final Map<String, String> hours;
    private final Map<String, String> services;

    public ClinicConfig() {
        this.clinicName = getProp("CLINIC_NAME", "Harmony Acupuncture Clinic");
        this.address = getProp("CLINIC_ADDRESS", "123 Wellness Ave, Suite 200, Your City");
        this.phone = getProp("CLINIC_PHONE", "(555) 123-4567");
        this.email = getProp("CLINIC_EMAIL", "hello@harmonyacupuncture.example");
        this.bookingUrl = getProp("BOOKING_URL", "https://example.com/book");
        this.hours = defaultHours();
        this.services = defaultServices();
    }

    private String getProp(String key, String defaultValue) {
        String sys = System.getProperty(key);
        if (sys != null && sys.trim().length() > 0) return sys.trim();
        String env = System.getenv(key);
        if (env != null && env.trim().length() > 0) return env.trim();
        return defaultValue;
    }

    private Map<String, String> defaultHours() {
        LinkedHashMap<String, String> h = new LinkedHashMap<String, String>();
        h.put("Mon", "9:00–18:00");
        h.put("Tue", "9:00–18:00");
        h.put("Wed", "9:00–18:00");
        h.put("Thu", "9:00–18:00");
        h.put("Fri", "9:00–16:00");
        h.put("Sat", "10:00–14:00");
        h.put("Sun", "Closed");
        return h;
    }

    private Map<String, String> defaultServices() {
        LinkedHashMap<String, String> s = new LinkedHashMap<String, String>();
        s.put("Acupuncture (Initial 75–90 min)", "$120");
        s.put("Acupuncture (Follow-up 45–60 min)", "$80");
        s.put("Cupping add-on", "$25");
        s.put("Moxibustion add-on", "$15");
        s.put("Herbal consult", "$40");
        return s;
    }

    public String getClinicName() { return clinicName; }
    public String getAddress() { return address; }
    public String getPhone() { return phone; }
    public String getEmail() { return email; }
    public String getBookingUrl() { return bookingUrl; }
    public Map<String, String> getHours() { return hours; }
    public Map<String, String> getServices() { return services; }
}
