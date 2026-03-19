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
  
  - block: my-custom-block
    content:
      title: Research Directions
      items:
        - title: AI Security & Privacy
          image: research-ai-security.png
        - title: System Security
          image: research-system-security.png
        - title: Data Privacy
          image: research-data-privacy.png

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
