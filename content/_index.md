---
# Leave the homepage title empty to use the site title
title:
date: 2022-10-24
type: landing

sections:
  - block: hero
    content:
      title: |
        UCLA Security Lab
      image:
        filename: website-view.png
      text: |
        <br>
        
        The **UCLA Security Lab** conducts research on security and privacy and their interactions with computer systems, machine learning, and human-computer interaction.

  - block: markdown
    content:
      title: Research
      subtitle: ''
      text: |
        Our lab conducts research at the intersection of security, privacy, machine learning, and human-computer interaction. Our work spans three major research directions.

        <div style="display: flex; flex-wrap: wrap; gap: 24px; justify-content: center; margin-top: 32px;">

        <div style="flex: 1; min-width: 280px; max-width: 360px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
          <img src="/media/research-ai-security.png" alt="AI Security" style="width: 100%; height: 200px; object-fit: cover;">
          <div style="padding: 20px;">
            <h3 style="margin-top: 0;">AI Security</h3>
            <p style="font-size: 0.95rem; color: #555;">We investigate the security and trustworthiness of machine learning models, including adversarial attacks, data poisoning, backdoor attacks on model merging, and environmental injection attacks on AI agents.</p>
          </div>
        </div>

        <div style="flex: 1; min-width: 280px; max-width: 360px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
          <img src="/media/research-data-privacy.png" alt="Data Privacy" style="width: 100%; height: 200px; object-fit: cover;">
          <div style="padding: 20px;">
            <h3 style="margin-top: 0;">Data Privacy</h3>
            <p style="font-size: 0.95rem; color: #555;">We study privacy risks and compliance , including GDPR enforcement, personal information disclosure in online communities, location privacy in recommendation systems, and user perceptions of data collection.</p>
          </div>
        </div>

        <div style="flex: 1; min-width: 280px; max-width: 360px; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
          <img src="/media/research-system-security.png" alt="System Security" style="width: 100%; height: 200px; object-fit: cover;">
          <div style="padding: 20px;">
            <h3 style="margin-top: 0;">System Security</h3>
            <p style="font-size: 0.95rem; color: #555;">We analyze the security of software systems including voice-controlled platforms, IoT ecosystems, authentication protocols, smart home automations, and extended reality (XR).</p>
          </div>
        </div>

        </div>
    design:
      columns: '1'

  - block: collection
    content:
      title: Latest News
      subtitle:
      text:
      count: 5
      filters:
        author: ''
        category: ''
        exclude_featured: false
        publication_type: ''
        tag: ''
      offset: 0
      order: desc
      page_type: post
    design:
      view: card
      columns: '1'
---
