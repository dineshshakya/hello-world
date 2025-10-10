package com.example.agent;

import java.util.Iterator;
import java.util.Locale;
import java.util.Map;

public class AcupunctureClinicAgent {
    private final ClinicConfig config;

    public AcupunctureClinicAgent() {
        this(new ClinicConfig());
    }

    public AcupunctureClinicAgent(ClinicConfig config) {
        this.config = config;
    }

    public String respond(String userMessage) {
        if (userMessage == null) {
            return greeting();
        }
        String text = userMessage.trim();
        if (text.length() == 0) {
            return greeting();
        }
        String normalized = text.toLowerCase(Locale.ENGLISH);

        if (containsAny(normalized, new String[]{"book", "booking", "schedule", "appointment", "reserve"})) {
            return "You can book online at " + config.getBookingUrl() + " or call " + config.getPhone() + ". Our hours: " + hoursInline() + ".";
        }

        if (containsAny(normalized, new String[]{"hour", "open", "time", "when"})) {
            return "Hours for " + config.getClinicName() + ": " + hoursMultiLine();
        }

        if (containsAny(normalized, new String[]{"price", "cost", "fee", "rate", "how much"})) {
            return "Pricing: " + servicesInline() + ". We accept HSA/FSA. For insurance, we can provide a superbill for out-of-network reimbursement.";
        }

        if (containsAny(normalized, new String[]{"service", "offer", "treatment", "cupping", "moxibustion", "gua", "herb"})) {
            return "Services: " + servicesInline() + ".";
        }

        if (containsAny(normalized, new String[]{"insur", "hsa", "fsa", "reimburse"})) {
            return "We’re out-of-network. Many plans reimburse. We’ll provide a superbill; HSA/FSA cards are accepted. Please check your benefits.";
        }

        if (containsAny(normalized, new String[]{"where", "address", "location", "directions"})) {
            return "We’re located at " + config.getAddress() + ". Call " + config.getPhone() + " if you need help finding us.";
        }

        if (containsAny(normalized, new String[]{"contact", "phone", "email", "call", "text"})) {
            return "Contact " + config.getClinicName() + " at " + config.getPhone() + " or " + config.getEmail() + ".";
        }

        if (containsAny(normalized, new String[]{"what to expect", "first visit", "intake", "how does it work", "process"})) {
            return "Expect a brief intake, tongue and pulse assessment, and a relaxing 30–45 minute acupuncture session. Wear loose, comfortable clothing and eat a light snack beforehand.";
        }

        if (containsAny(normalized, new String[]{"pregnan", "contra", "safety", "safe", "needle"})) {
            return "Acupuncture is generally safe when performed by a licensed practitioner. We tailor points for pregnancy and other conditions. Always share your medical history.";
        }

        if (containsAny(normalized, new String[]{"hello", "hi", "hey", "help"})) {
            return greeting();
        }

        return "I can help with booking, hours, services, pricing/insurance, location, and what to expect. What would you like to know?";
    }

    private boolean containsAny(String text, String[] needles) {
        for (int i = 0; i < needles.length; i++) {
            if (text.indexOf(needles[i]) >= 0) {
                return true;
            }
        }
        return false;
    }

    private String greeting() {
        return "Hi! I’m the " + config.getClinicName() + " assistant. Ask me about booking, hours, services, pricing/insurance, or location.";
    }

    private String hoursInline() {
        StringBuilder sb = new StringBuilder();
        Iterator<Map.Entry<String,String>> it = config.getHours().entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<String,String> e = it.next();
            sb.append(e.getKey()).append(": ").append(e.getValue());
            if (it.hasNext()) sb.append(", ");
        }
        return sb.toString();
    }

    private String hoursMultiLine() {
        StringBuilder sb = new StringBuilder();
        Iterator<Map.Entry<String,String>> it = config.getHours().entrySet().iterator();
        boolean first = true;
        while (it.hasNext()) {
            Map.Entry<String,String> e = it.next();
            if (!first) sb.append(" ");
            sb.append(e.getKey()).append(": ").append(e.getValue()).append(".");
            first = false;
        }
        return sb.toString();
    }

    private String servicesInline() {
        StringBuilder sb = new StringBuilder();
        Iterator<Map.Entry<String,String>> it = config.getServices().entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<String,String> e = it.next();
            sb.append(e.getKey()).append(" - ").append(e.getValue());
            if (it.hasNext()) sb.append("; ");
        }
        return sb.toString();
    }
}
