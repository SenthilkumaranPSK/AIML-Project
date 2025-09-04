# Student Malpractice Detection System

## Overview

This is an AI-powered student malpractice detection system designed for exam hall monitoring. The application uses computer vision and machine learning to detect suspicious behaviors in real-time, including hand gestures indicating cheating, mobile phone usage, and talking/mouth movements. Built with Flask as the web framework, the system provides live video monitoring, real-time alerts, event logging, and comprehensive reporting capabilities for educational institutions.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **UI Framework**: Bootstrap 5 for responsive design with Font Awesome icons
- **JavaScript**: Vanilla JavaScript with polling-based real-time updates
- **Styling**: Custom CSS with CSS variables for theming and responsive video containers

### Backend Architecture
- **Web Framework**: Flask with threaded request handling
- **Detection Engine**: Custom `MalpracticeDetector` class implementing multiple AI models
- **Session Management**: Flask sessions with global state management for monitoring
- **Concurrency**: Threading for real-time video processing without blocking web requests

### AI/ML Detection Pipeline
- **Hand Gesture Detection**: MediaPipe Hands for hand landmark detection and gesture analysis
- **Mobile Phone Detection**: YOLOv8 object detection model for identifying mobile devices
- **Talking Detection**: MediaPipe Face Mesh for mouth landmark tracking and movement analysis
- **Detection Cooldown**: Time-based filtering to prevent spam alerts

### Data Management
- **In-Memory Storage**: Global variables for session state and malpractice logs
- **Event Logging**: Timestamped event records with detection types and counts
- **File Operations**: Snapshot saving and PDF report generation

### Video Processing
- **OpenCV Integration**: Video capture and frame processing
- **Real-time Streaming**: Flask response streaming for live video feed
- **Multiple Sources**: Support for both live camera and local video file inputs

### Reporting System
- **PDF Generation**: ReportLab for professional malpractice reports
- **Event Summaries**: Detailed logging with timestamps and detection counts
- **Export Functionality**: Downloadable PDF reports for institutional records

## External Dependencies

### AI/ML Libraries
- **MediaPipe**: Google's framework for hand and face landmark detection
- **Ultralytics YOLO**: YOLOv8 model for object detection (mobile phones)
- **OpenCV**: Computer vision library for video processing and image manipulation
- **NumPy**: Numerical computing for array operations and mathematical functions

### Web Framework
- **Flask**: Python web framework for HTTP handling and routing
- **Werkzeug**: WSGI utilities including ProxyFix middleware

### Frontend Libraries
- **Bootstrap 5**: CSS framework delivered via CDN for responsive UI components
- **Font Awesome 6**: Icon library delivered via CDN for UI iconography

### Document Generation
- **ReportLab**: PDF generation library for creating professional reports with tables, images, and styling

### Development Tools
- **Python Logging**: Built-in logging module for debugging and monitoring
- **Threading**: Python's threading module for concurrent video processing