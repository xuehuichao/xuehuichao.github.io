---
layout: default
title: Home
---

# Huichao Xue
Welcome to my personal website

# About
This is my personal GitHub Pages website. More content coming soon!

# Projects
Check out my work on [GitHub](https://github.com/xuehuichao).

# Blog
{% for post in site.posts %}
{% unless post.lang == 'zh' %}
{% assign chinese_slug = post.url | append: '-zh' %}
{% assign chinese_version = site.posts | where: "url", chinese_slug | first %}
{% unless chinese_version %}
{% assign post_filename = post.path | split: '/' | last | replace: '.md', '' %}
{% assign chinese_filename = post_filename | append: '-zh' %}
{% assign chinese_version = site.posts | where_exp: "p", "p.path contains chinese_filename" | first %}
{% endunless %}
- [{{ post.title }}]({{ post.url }}){% if chinese_version %} · [{{ chinese_version.title }}]({{ chinese_version.url }}){% endif %} - {{ post.date | date: "%B %d, %Y" }}
{% endunless %}
{% endfor %}

# Contact
Find me on [GitHub](https://github.com/xuehuichao)