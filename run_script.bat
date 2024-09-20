@echo off
call v3\Scripts\activate
python vdo_feed.py

@echo off
call v3\Scripts\activate
python display_feed.py
