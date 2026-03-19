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
  
  - block: research_direction
    content:
      title: Research Directions
      rd_1_title: AI Security & Privacy
      rd_1_image: research-ai-security.png
      rd_2_title: System Security
      rd_2_image: research-system-security.png
      rd_3_title: Data Privacy
      rd_3_image: research-data-privacy.png

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

  - block: markdown
    content:
      title:
      subtitle:
      text: |
        {{% cta cta_link="./people/" cta_text="Meet the team →" %}}
    design:
      columns: '1'
---
