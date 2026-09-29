---
title: Research
date: 2024-01-01
type: landing

# Research page in the style of Kai-Wei Chang's research page, rendered by layouts/partials/blocks/research_areas.html.
# Each area's "Related papers" are listed automatically from the publications whose `research_area` matches `key`.
# Site paths have no leading slash so they work under the /UCLA-Sec-Lab-Website/ subpath.
sections:
  - block: research_areas
    content:
      title: Research
      header_link:
        label: See all publications
        url: publication/
      text: Our lab conducts research at the intersection of security, privacy, machine learning, and human-computer interaction. Our work spans three major research directions.
      areas:
        - key: ai-security
          title: AI Security
          status: Active
          description: >-
            We investigate the security and trustworthiness of machine learning models, including adversarial
            attacks, data poisoning, backdoor attacks on model merging, and environmental injection attacks on AI
            agents. Our work addresses threats across the ML pipeline — from training-time poisoning to
            deployment-time adversarial manipulation — and explores defenses such as automated vulnerability repair.
          projects:
            - Trustworthy AI agents, with Kai-Wei Chang, Cho-Jui Hsieh, and Nanyun Peng (Coefficient Giving)
            - "Bruinweb: Amazon Nova AI Challenge — Trusted Software Agents"
            - Trustworthy medical AI (NSF)
            - Trustworthy human-AI collaboration (Okawa Foundation)
            - LLMs for security analysis (Cisco)
          sponsors:
            - name: NSF
              kind: government
            - name: Amazon
              kind: industry
            - name: Cisco
              kind: industry
            - name: Coefficient Giving
              kind: foundation
            - name: Okawa Foundation
              kind: foundation
        - key: data-privacy
          title: Data Privacy
          status: Active
          description: >-
            We study privacy risks and compliance in software systems, including GDPR enforcement, personal
            information disclosure in online communities, location privacy in recommendation systems, and user
            perceptions of data collection in IoT and public WiFi environments. Our research combines automated
            program analysis with empirical user studies to advance privacy protection.
          projects:
            - Privacy regulations and software development, for better rulemaking and compliance (NSF)
            - Privacy-preserving mobility data generation (NSF)
            - Private data analytics, synthesis, and sharing for smart-city mobility research (NSF)
            - Enforcing security and privacy policies to protect research data, with Kai-Wei Chang (NSF)
          sponsors:
            - name: NSF
              kind: government
        - key: system-security
          title: System Security
          status: Active
          description: >-
            We analyze the security of software systems including voice-controlled platforms, IoT ecosystems,
            authentication protocols, smart home automations, and extended reality (XR). Our work spans
            vulnerability discovery in voice assistants, permission analysis, OAuth security verification,
            WebAssembly runtime fuzzing, and usable security tools for end users.
          projects:
            - "CAREER: Secure voice-controlled platforms (NSF)"
            - Safe, private, and secure home automation, with Lujo Bauer and Limin Jia at CMU (NSF)
            - Perception integrity in virtual reality (Meta Research Award)
            - Exploit generation using reinforcement learning, with Yu Feng (Google Research Scholar Award)
            - Device security (Keysight)
          sponsors:
            - name: NSF
              kind: government
            - name: Google
              kind: industry
            - name: Meta
              kind: industry
            - name: Keysight
              kind: industry
---
