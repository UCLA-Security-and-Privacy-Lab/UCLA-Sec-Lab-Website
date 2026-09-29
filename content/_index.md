---
# Homepage: one kwchang-style card rendered by layouts/partials/blocks/lab_home.html.
# Site paths have no leading slash (research/, publication/2026-oakland/) so they work under the /UCLA-Sec-Lab-Website/ subpath.
title:
date: 2022-10-24
type: landing

sections:
  - block: lab_home
    content:
      hero:
        title: BruinSec Lab
        roles:
          - Electrical and Computer Engineering · Computer Science
          - University of California, Los Angeles
        summary: "BruinSec Lab, led by Prof. Yuan Tian at UCLA, studies the security, privacy, and safety of modern and emerging systems — from AI models and agents to IoT, voice platforms, and extended reality. We combine program analysis, protocol analysis, machine learning, and human factors, and publish at IEEE S&P, USENIX Security, CCS, NDSS, ICLR, and ICML."
        buttons:
          - label: Research
            url: research/
            primary: true
          - label: Publications
            url: publication/
          - label: People
            url: people/
          - label: News
            url: post/
          - label: Join Us
            url: contact/
      pi:
        author: Prof-YuanTian
        name: Yuan Tian
        lines:
          - Associate Professor
          - ECE & CS, UCLA
        links:
          - label: Email
            url: mailto:yuant@ucla.edu
          - label: Homepage
            url: https://www.ytian.info/
          - label: Scholar
            url: https://scholar.google.com/citations?user=ja0GtqgAAAAJ
      news:
        count: 5
      research:
        label: Research at a glance
        areas:
          - title: AI Security
            description: We investigate the security and trustworthiness of machine learning models, including adversarial attacks, data poisoning, backdoor attacks on model merging, and environmental injection attacks on AI agents.
            chips:
              - label: "EIA (ICLR '25)"
                url: publication/2025-eia-iclr/
              - label: "BadMerging (CCS '24)"
                url: publication/2024-badmerging/
              - label: "Chimera (USENIX Sec '25)"
                url: publication/2025-chimera/
              - label: "SoK: Vulnerability Repair (USENIX Sec '25)"
                url: publication/2025-sok/
              - label: "Poisoning Attacks (ICML '21)"
                url: publication/2021-icml/
          - title: Data Privacy
            description: We study privacy risks and compliance, including GDPR enforcement, personal information disclosure in online communities, location privacy in recommendation systems, and user perceptions of data collection.
            chips:
              - label: "GDPR Consent (S&P '26)"
                url: publication/2026-oakland/
              - label: "Smart Home IFA (PETS '26)"
                url: publication/2026-pets/
              - label: "City-wide WiFi (PETS '25)"
                url: publication/2025-freewifi-pets/
              - label: "CHKPLUG (NDSS '23)"
                url: publication/2023-chkplug/
              - label: "SenRev (PETS '23)"
                url: publication/2023-senrev/
          - title: System Security
            description: We analyze the security of software systems including voice-controlled platforms, IoT ecosystems, authentication protocols, smart home automations, and extended reality (XR).
            chips:
              - label: "XR Threats (NDSS '26)"
                url: publication/2026-ndss/
              - label: "Waltzz (USENIX Sec '25)"
                url: publication/2025-waltzz/
              - label: "AuthSaber (CCS '24)"
                url: publication/2024-authsaber/
              - label: "Alexa Skill Vetting (ICSE '24)"
                url: publication/2024-alexa/
              - label: "TKPERM (NDSS '20)"
                url: publication/2020-tkperm/
      projects:
        - title: Bruinweb
          status: Active
          topics: [AI Agents, Web Security]
          description: "Our team in the Amazon Nova AI Challenge: Trusted Software Agents — one of 10 international teams selected in 2026."
          links:
            - label: News
              url: post/26-amazon-nova-challenge/
        - title: Trustworthy AI Agents
          status: Active
          topics: [AI Security, Agents]
          description: Research on safe and trustworthy AI agents, supported by Coefficient Giving, with Kai-Wei Chang, Cho-Jui Hsieh, and Nanyun Peng.
          links:
            - label: News
              url: post/26-coefficient-giving/
        - title: Trustworthy Medical AI
          status: Active
          topics: [AI Security, Healthcare]
          description: NSF-supported research on making medical AI systems secure and trustworthy.
          links:
            - label: News
              url: post/26-nsf-medical-ai/
      highlights:
        - title: "Breaking the Illusion: Automated Reasoning of GDPR Consent Violations"
          venue: IEEE S&P 2026
          url: publication/2026-oakland/
        - title: "From Perception to Protection: Security and Privacy Threats in Extended Reality"
          venue: NDSS 2026
          url: publication/2026-ndss/
        - title: "BadMerging: Backdoor Attacks Against Model Merging"
          venue: ACM CCS 2024
          url: publication/2024-badmerging/
        - title: "AuthSaber: Automated Safety Verification of OpenID Connect Programs"
          venue: ACM CCS 2024
          url: publication/2024-authsaber/
        - title: "Chimera: Fooling Image Recapture and Deepfake Detectors"
          venue: USENIX Security 2025
          url: publication/2025-chimera/
        - title: "EIA: Environmental Injection Attack on Generalist Web Agents"
          venue: ICLR 2025
          url: publication/2025-eia-iclr/
      impact:
        - value: "2020"
          caption: NSF CAREER Award
          url: awards/
        - value: "2021"
          caption: Google Research Scholar Award
          url: awards/
        - value: "2022"
          caption: Okawa Foundation Award
          url: awards/
        - value: "4"
          caption: platforms (Android, Chrome, Firefox, iOS) adopted fixes from our research
          url: awards/
      funding:
        - NSF
        - Google
        - Amazon
        - Meta
        - Cisco
        - Keysight
        - Okawa Foundation
        - Coefficient Giving
      join:
        label: Join the lab
        text: We are looking for PhD students, postdocs, and research interns interested in systems security, AI security, and privacy.
        button:
          label: View opportunities
          url: contact/
---
